# Directory: backend/agents/
# File: security_agent.py
# Description: Agent specialized for security monitoring and threat prevention.

import asyncio
from typing import Any, Dict, Optional, List, Set
from pathlib import Path
import hashlib
import re
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
import sqlparse
import bandit
from safety.util import read_requirements

from backend.agents.base_agent import BaseAgent, ExecuteSkillType
from backend.models.model_router import ModelRouter
from backend.memory.base_memory import BaseMemory
from backend.skills import SkillError
from backend.utils.logger import setup_logger

class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, callback):
        self.callback = callback
        super().__init__()

    def on_modified(self, event):
        if not event.is_directory:
            self.callback(event.src_path)

class SecurityAgent(BaseAgent):
    """
    A specialized agent for monitoring and protecting against security threats.
    Capabilities include file monitoring, vulnerability scanning, and attack prevention.
    """

    DEFAULT_SYSTEM_PROMPT = (
        "You are an expert Security Engineer focused on protecting systems against cyber threats. "
        "Your capabilities include:\n"
        "1. Real-time file system monitoring and threat detection\n"
        "2. Code security analysis and vulnerability scanning\n"
        "3. SQL injection and XSS attack prevention\n"
        "4. Dependency security analysis\n"
        "5. Incident response and reporting\n"
        "Use systematic approach to security analysis and maintain detailed logs of all activities."
    )

    def __init__(
        self,
        agent_id: str,
        model_router: ModelRouter,
        agent_memory: BaseMemory,
        execute_skill_func: ExecuteSkillType,
        config: Optional[Dict[str, Any]] = None,
        system_prompt: Optional[str] = None
    ):
        """Initialize the SecurityAgent with monitoring capabilities."""
        super().__init__(
            agent_id=agent_id,
            agent_name="SecurityAgent",
            model_router=model_router,
            agent_memory=agent_memory,
            execute_skill_func=execute_skill_func,
            config=config or {},
            system_prompt=system_prompt or self.DEFAULT_SYSTEM_PROMPT
        )

        # Initialize security monitoring
        self.monitored_files: Dict[str, str] = {}  # path -> hash
        self.file_observer = Observer()
        self.event_handler = FileChangeHandler(self._handle_file_change)
        self.suspicious_patterns = self._load_suspicious_patterns()
        self.initialize_monitoring()

    def _load_suspicious_patterns(self) -> Dict[str, List[str]]:
        """Load patterns for detecting suspicious code."""
        return {
            'sql_injection': [
                r".*(?i)(?:UNION.*SELECT|INSERT.*INTO|UPDATE.*SET|DELETE.*FROM).*",
                r".*(?i)(?:DROP.*TABLE|ALTER.*TABLE|EXEC.*sp_).*",
                r".*(?i)(?:SELECT.*FROM.*WHERE.*=.*1.*=.*1).*"
            ],
            'xss': [
                r".*(?i)(?:<script.*>|javascript:).*",
                r".*(?i)(?:onerror=|onload=|onclick=).*",
                r".*(?i)(?:alert\(|eval\(|document\.cookie).*"
            ],
            'command_injection': [
                r".*(?i)(?:system\(|exec\(|shell_exec\().*",
                r".*(?i)(?:`.*`|\|.*\||;.*;).*",
                r".*(?i)(?:>/dev/null|2>&1).*"
            ],
            'file_operations': [
                r".*(?i)(?:file_get_contents\(|fopen\(|readfile\().*",
                r".*(?i)(?:include\(|require\(|include_once\().*",
                r".*(?i)(?:unlink\(|rmdir\(|mkdir\().*"
            ]
        }

    def initialize_monitoring(self):
        """Initialize file system monitoring."""
        try:
            workspace_path = Path.cwd()
            self.file_observer.schedule(self.event_handler, str(workspace_path), recursive=True)
            self.file_observer.start()
            self.log.info(f"Started monitoring workspace: {workspace_path}")
        except Exception as e:
            self.log.error(f"Failed to initialize file monitoring: {e}")
            raise SkillError("Failed to initialize security monitoring") from e

    async def _handle_file_change(self, file_path: str):
        """Handle file change events and analyze for security threats."""
        try:
            # Calculate new file hash
            with open(file_path, 'rb') as f:
                new_hash = hashlib.sha256(f.read()).hexdigest()

            # Check if file was actually modified
            if file_path in self.monitored_files and self.monitored_files[file_path] == new_hash:
                return

            self.monitored_files[file_path] = new_hash
            
            # Analyze file for security threats
            threats = await self.analyze_file_security(file_path)
            if threats:
                await self._report_security_threat(file_path, threats)

        except Exception as e:
            self.log.error(f"Error handling file change for {file_path}: {e}")

    async def analyze_file_security(self, file_path: str) -> List[Dict[str, Any]]:
        """Analyze a file for security threats."""
        threats = []
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            # Check for suspicious patterns
            for threat_type, patterns in self.suspicious_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.MULTILINE)
                    for match in matches:
                        threats.append({
                            'type': threat_type,
                            'pattern': pattern,
                            'line': content.count('\n', 0, match.start()) + 1,
                            'match': match.group()
                        })

            # Additional security checks based on file type
            if file_path.endswith('.py'):
                await self._analyze_python_security(file_path, threats)
            elif file_path.endswith(('.js', '.ts')):
                await self._analyze_js_security(file_path, threats)

        except Exception as e:
            self.log.error(f"Error analyzing file security for {file_path}: {e}")
            
        return threats

    async def _analyze_python_security(self, file_path: str, threats: List[Dict[str, Any]]):
        """Analyze Python file security using bandit."""
        try:
            from bandit.core.manager import BanditManager
            from bandit.core.config import BanditConfig
            from bandit.core import constants

            # Setup Bandit configuration and manager
            b_conf = BanditConfig()
            manager = BanditManager(b_conf, 'file', False)
            manager.discover_files([file_path], True)
            manager.run_tests()
            # Bandit 1.7+ uses Severity and Confidence enums, and get_issue_list expects string levels
            for issue in manager.get_issue_list(sev_level="LOW", conf_level="LOW"):
                threats.append({
                    'type': 'python_security',
                    'severity': str(issue.severity),
                    'confidence': str(issue.confidence),
                    'description': issue.text,
                    'line': issue.lineno
                })
        except Exception as e:
            self.log.error(f"Error in Python security analysis: {e}")

    async def _analyze_js_security(self, file_path: str, threats: List[Dict[str, Any]]):
        """Analyze JavaScript/TypeScript file security."""
        # This would integrate with ESLint security plugins or other JS security tools
        pass

    async def _report_security_threat(self, file_path: str, threats: List[Dict[str, Any]]):
        """Report detected security threats."""
        try:
            # Store threat information in memory
            await self._remember(
                f"security_threat_{file_path}",
                {
                    'file_path': file_path,
                    'threats': threats,
                    'timestamp': asyncio.get_event_loop().time()
                },
                {
                    'type': 'security_threat',
                    'severity': max(threat.get('severity', 'medium') for threat in threats)
                }
            )

            # Create detailed report
            report = await self._create_threat_report(file_path, threats)
            
            # Log the threat
            self.log.warning(f"Security threat detected in {file_path}:\n{report}")

            # Could integrate with notification systems here
            
        except Exception as e:
            self.log.error(f"Error reporting security threat: {e}")

    async def _create_threat_report(self, file_path: str, threats: List[Dict[str, Any]]) -> str:
        """Create a detailed report of security threats."""
        try:
            report_prompt = (
                f"Analyze the following security threats detected in {file_path} "
                f"and provide a detailed report with risk assessment and mitigation recommendations:\n"
                f"{threats}"
            )
            
            report = await self._call_llm(
                prompt=report_prompt,
                model_preference="gpt-4"  # Assuming this model is available
            )
            
            return report
            
        except Exception as e:
            self.log.error(f"Error creating threat report: {e}")
            return f"Error creating threat report: {e}"

    async def check_sql_injection(self, query: str) -> Dict[str, Any]:
        """Check for SQL injection vulnerabilities in a query."""
        try:
            # Parse and analyze SQL query
            parsed = sqlparse.parse(query)
            analysis = {
                'is_safe': True,
                'warnings': [],
                'recommendations': []
            }

            for statement in parsed:
                # Check for dangerous patterns
                statement_str = str(statement)
                if re.search(r"(?i)(\bUNION\b.*\bSELECT\b|\bDROP\b|\bDELETE\b)", statement_str):
                    analysis['is_safe'] = False
                    analysis['warnings'].append("Potentially dangerous SQL operation detected")

                # Check for proper parameterization
                if re.search(r"'.*'", statement_str):
                    analysis['warnings'].append("Direct string literals in query - use parameterized queries")
                    analysis['recommendations'].append("Use query parameters instead of string concatenation")

            return analysis

        except Exception as e:
            self.log.error(f"Error analyzing SQL query: {e}")
            raise SkillError("SQL analysis failed") from e

    def cleanup(self):
        """Clean up monitoring resources."""
        try:
            self.file_observer.stop()
            self.file_observer.join()
        except Exception as e:
            self.log.error(f"Error during cleanup: {e}")

    def __del__(self):
        """Ensure cleanup on deletion."""
        self.cleanup()

    # Add a minimal async run implementation to allow instantiation in tests
    async def run(self, *args, **kwargs):
        return None
