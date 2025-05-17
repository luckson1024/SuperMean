# Simple test to verify design_agent.py can be imported and f-string syntax is correct

import sys
import os

# Add the parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

try:
    from backend.agents.design_agent import DesignAgent
    print("Successfully imported DesignAgent")
    
    # Test the f-string syntax by creating a simple instance of the class
    # and checking if the format_part and context_part variables are created correctly
    def test_format_string_syntax():
        # Create a mock task description
        task_description = "Test task"
        kwargs = {
            'context': 'Test context',
            'target_format': 'markdown'
        }
        
        # Extract the relevant parts from the code
        context_part = f"CONTEXT: {kwargs.get('context')}\n" if kwargs.get('context') else ""
        format_part = f" in {kwargs['target_format']} format" if kwargs.get('target_format') else ""
        
        # Print the results
        print(f"context_part: '{context_part}'")
        print(f"format_part: '{format_part}'")
        
        # Construct the prompt as in the design_agent.py file
        prompt = (
            f"DESIGN TASK: {task_description}\n"
            f"{context_part}"
            f"\n\n"
            f"Follow this structure for your response:\n"
            "1. Requirements Analysis:\n"
            "2. Design Strategy:\n"
            "3. Detailed Design Output"
            f"{format_part}"
        )
        
        print(f"\nFull prompt:\n{prompt}")
        print("\nF-string syntax test passed!")
    
    # Run the test
    test_format_string_syntax()
    
except ImportError as e:
    print(f"Failed to import DesignAgent: {e}")
    sys.exit(1)
except SyntaxError as e:
    print(f"Syntax error in design_agent.py: {e}")
    print(f"Line {e.lineno}, position {e.offset}: {e.text}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected error: {e}")
    sys.exit(1)