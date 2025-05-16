# Directory: backend/skills/
# File: skill_registry.py
# Description: Advanced skill registry with versioning support for dynamic skill loading.

import asyncio
import importlib
import inspect
import json
import os
import pkgutil
import sys
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from backend.skills import register_skill, execute_skill, list_skills, SkillError
from backend.memory.base_memory import BaseMemory
from backend.utils.logger import setup_logger
from backend.utils.error_handler import SuperMeanException

# Logger setup
log = setup_logger(name="skill_registry")

class SkillRegistryError(SuperMeanException):
    """Custom exception for skill registry operations."""
    def __init__(self, message="Skill registry operation failed", status_code=500, cause: Optional[Exception] = None):
        super().__init__(message, status_code)
        if cause:
            self.__cause__ = cause

class SkillRegistry:
    """
    Advanced skill registry with versioning support for dynamic skill loading.
    
    Features:
    - Dynamic skill discovery and loading
    - Skill versioning and compatibility tracking
    - Skill dependency management
    - Performance metrics collection
    - Skill caching for improved performance
    - Skill validation and testing
    """
    
    def __init__(
        self,
        memory: Optional[BaseMemory] = None,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the SkillRegistry.
        
        Args:
            memory: Optional memory instance for persistent skill metadata
            config: Optional configuration settings
        """
        self.memory = memory
        self.config = config or {}
        
        # Skill version tracking
        self.skill_versions: Dict[str, Dict[str, Any]] = {}
        # Skill dependency tracking
        self.skill_dependencies: Dict[str, Set[str]] = {}
        # Skill performance metrics
        self.skill_metrics: Dict[str, Dict[str, Any]] = {}
        # Skill loading paths
        self.skill_paths: List[str] = self.config.get("skill_paths", [])
        
        # Auto-discovery settings
        self.auto_discover = self.config.get("auto_discover", True)
        
        log.info("SkillRegistry initialized")
        
        # Perform initial skill discovery if auto-discover is enabled
        if self.auto_discover:
            asyncio.create_task(self.discover_skills())
    
    async def discover_skills(self, paths: Optional[List[str]] = None) -> List[str]:
        """
        Discover and load skills from specified paths or default skill paths.
        
        Args:
            paths: Optional list of paths to search for skills
            
        Returns:
            List of discovered skill names
        """
        search_paths = paths or self.skill_paths
        if not search_paths:
            # Default to the skills directory if no paths specified
            module_dir = os.path.dirname(os.path.abspath(__file__))
            search_paths = [module_dir]
        
        discovered_skills = []
        
        for path in search_paths:
            log.info(f"Discovering skills in path: {path}")
            
            if os.path.isdir(path):
                # Add path to sys.path if not already there
                if path not in sys.path:
                    sys.path.insert(0, path)
                
                # Get the package name for this path
                package_name = os.path.basename(path)
                
                # Discover modules in the package
                try:
                    for _, name, is_pkg in pkgutil.iter_modules([path]):
                        if name.endswith("_skill") and not is_pkg:
                            # This looks like a skill module
                            module_name = f"{package_name}.{name}"
                            try:
                                # Import the module
                                module = importlib.import_module(module_name)
                                
                                # Look for skill functions in the module
                                for attr_name in dir(module):
                                    attr = getattr(module, attr_name)
                                    if callable(attr) and hasattr(attr, "_is_skill"):
                                        skill_name = getattr(attr, "_skill_name", attr_name)
                                        discovered_skills.append(skill_name)
                                        
                                        # Register skill version information
                                        version = getattr(module, "__version__", "0.1.0")
                                        self.skill_versions[skill_name] = {
                                            "version": version,
                                            "module": module_name,
                                            "last_updated": datetime.now().isoformat()
                                        }
                                        
                                        log.info(f"Discovered skill: {skill_name} (v{version})")
                            except Exception as e:
                                log.error(f"Error loading module {module_name}: {e}")
                except Exception as e:
                    log.error(f"Error discovering skills in path {path}: {e}")
        
        log.info(f"Discovered {len(discovered_skills)} skills")
        return discovered_skills
    
    async def register_skill_version(self, skill_name: str, version: str, metadata: Dict[str, Any]) -> bool:
        """
        Register or update version information for a skill.
        
        Args:
            skill_name: Name of the skill
            version: Version string (e.g., "1.2.3")
            metadata: Additional metadata for the skill version
            
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            # Update in-memory version tracking
            self.skill_versions[skill_name] = {
                "version": version,
                "last_updated": datetime.now().isoformat(),
                **metadata
            }
            
            # Store in persistent memory if available
            if self.memory:
                await self.memory.store(
                    f"skill_version:{skill_name}",
                    self.skill_versions[skill_name]
                )
            
            log.info(f"Registered skill version: {skill_name} (v{version})")
            return True
        except Exception as e:
            log.error(f"Error registering skill version for {skill_name}: {e}")
            return False
    
    async def get_skill_version(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        Get version information for a skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Dictionary with version information, or None if not found
        """
        # Try memory first if available
        if self.memory:
            version_info = await self.memory.retrieve(f"skill_version:{skill_name}")
            if version_info:
                return version_info
        
        # Fall back to in-memory tracking
        return self.skill_versions.get(skill_name)
    
    async def register_skill_dependency(self, skill_name: str, dependencies: List[str]) -> bool:
        """
        Register dependencies for a skill.
        
        Args:
            skill_name: Name of the skill
            dependencies: List of skill names this skill depends on
            
        Returns:
            True if registration was successful, False otherwise
        """
        try:
            # Update in-memory dependency tracking
            self.skill_dependencies[skill_name] = set(dependencies)
            
            # Store in persistent memory if available
            if self.memory:
                await self.memory.store(
                    f"skill_dependencies:{skill_name}",
                    list(dependencies)
                )
            
            log.info(f"Registered dependencies for skill {skill_name}: {dependencies}")
            return True
        except Exception as e:
            log.error(f"Error registering dependencies for skill {skill_name}: {e}")
            return False
    
    async def get_skill_dependencies(self, skill_name: str) -> List[str]:
        """
        Get dependencies for a skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            List of skill names this skill depends on
        """
        # Try memory first if available
        if self.memory:
            dependencies = await self.memory.retrieve(f"skill_dependencies:{skill_name}")
            if dependencies:
                return dependencies
        
        # Fall back to in-memory tracking
        return list(self.skill_dependencies.get(skill_name, set()))
    
    async def record_skill_metrics(self, skill_name: str, execution_time: float, success: bool) -> None:
        """
        Record performance metrics for a skill execution.
        
        Args:
            skill_name: Name of the skill
            execution_time: Time taken to execute the skill (in seconds)
            success: Whether the execution was successful
        """
        if skill_name not in self.skill_metrics:
            self.skill_metrics[skill_name] = {
                "total_executions": 0,
                "successful_executions": 0,
                "failed_executions": 0,
                "total_execution_time": 0.0,
                "average_execution_time": 0.0,
                "last_execution_time": None
            }
        
        metrics = self.skill_metrics[skill_name]
        metrics["total_executions"] += 1
        metrics["total_execution_time"] += execution_time
        metrics["average_execution_time"] = metrics["total_execution_time"] / metrics["total_executions"]
        metrics["last_execution_time"] = datetime.now().isoformat()
        
        if success:
            metrics["successful_executions"] += 1
        else:
            metrics["failed_executions"] += 1
        
        # Store in persistent memory if available
        if self.memory:
            await self.memory.store(
                f"skill_metrics:{skill_name}",
                metrics
            )
    
    async def get_skill_metrics(self, skill_name: str) -> Optional[Dict[str, Any]]:
        """
        Get performance metrics for a skill.
        
        Args:
            skill_name: Name of the skill
            
        Returns:
            Dictionary with performance metrics, or None if not found
        """
        # Try memory first if available
        if self.memory:
            metrics = await self.memory.retrieve(f"skill_metrics:{skill_name}")
            if metrics:
                return metrics
        
        # Fall back to in-memory tracking
        return self.skill_metrics.get(skill_name)
    
    async def execute_skill_with_metrics(self, skill_name: str, *args, **kwargs) -> Any:
        """
        Execute a skill and record performance metrics.
        
        Args:
            skill_name: Name of the skill to execute
            *args: Positional arguments for the skill
            **kwargs: Keyword arguments for the skill
            
        Returns:
            Result of the skill execution
        """
        start_time = asyncio.get_event_loop().time()
        success = False
        result = None
        
        try:
            # Execute the skill
            result = await execute_skill(skill_name, *args, **kwargs)
            success = True
            return result
        except Exception as e:
            log.error(f"Error executing skill {skill_name}: {e}")
            raise
        finally:
            # Record metrics regardless of success/failure
            execution_time = asyncio.get_event_loop().time() - start_time
            await self.record_skill_metrics(skill_name, execution_time, success)
    
    async def get_all_skills(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get information about all registered skills, optionally filtered by category.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            List of skill information dictionaries
        """
        # Get basic skill information from the skills registry
        skills_info = list_skills(category)
        
        # Enhance with version and metrics information
        for skill_info in skills_info:
            skill_name = skill_info["name"]
            
            # Add version information
            version_info = await self.get_skill_version(skill_name)
            if version_info:
                skill_info["version"] = version_info.get("version", "unknown")
                skill_info["last_updated"] = version_info.get("last_updated")
            
            # Add metrics information
            metrics = await self.get_skill_metrics(skill_name)
            if metrics:
                skill_info["metrics"] = metrics
            
            # Add dependency information
            dependencies = await self.get_skill_dependencies(skill_name)
            if dependencies:
                skill_info["dependencies"] = dependencies
        
        return skills_info
    
    async def validate_skill(self, skill_name: str) -> Dict[str, Any]:
        """
        Validate a skill by checking its availability and dependencies.
        
        Args:
            skill_name: Name of the skill to validate
            
        Returns:
            Validation result dictionary
        """
        result = {
            "skill_name": skill_name,
            "available": False,
            "dependencies_met": False,
            "issues": []
        }
        
        # Check if skill exists
        skills = list_skills()
        skill_exists = any(skill["name"] == skill_name for skill in skills)
        
        if not skill_exists:
            result["issues"].append(f"Skill '{skill_name}' not found in registry")
            return result
        
        result["available"] = True
        
        # Check dependencies
        dependencies = await self.get_skill_dependencies(skill_name)
        missing_dependencies = []
        
        for dep in dependencies:
            dep_exists = any(skill["name"] == dep for skill in skills)
            if not dep_exists:
                missing_dependencies.append(dep)
        
        if missing_dependencies:
            result["issues"].append(f"Missing dependencies: {', '.join(missing_dependencies)}")
        else:
            result["dependencies_met"] = True
        
        return result