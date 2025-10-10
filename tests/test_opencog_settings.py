#!/usr/bin/env python3
"""
Test OpenCog settings integration
"""

import os
import sys

def test_opencog_settings_structure():
    """Test that OpenCog settings are properly defined in the settings structure."""
    try:
        # Get the project root directory
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(test_dir)
        settings_file = os.path.join(project_root, 'python', 'helpers', 'settings.py')
        
        # Read settings file directly to avoid import issues
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # Check that OpenCog settings are defined in TypedDict
        expected_settings = [
            'opencog_enabled: bool',
            'opencog_atomspace_persistence: bool',
            'opencog_reasoning_engine: str',
            'opencog_default_domain: str',
            'opencog_max_atoms: int',
            'opencog_reasoning_steps: int'
        ]
        
        for setting in expected_settings:
            assert setting in content, f"Missing OpenCog setting: {setting}"
        
        print("✓ OpenCog settings are properly defined in Settings TypedDict")
        
        # Check that default values are set
        default_values = [
            'opencog_enabled=True',
            'opencog_atomspace_persistence=False',
            'opencog_reasoning_engine="forward_chain"',
            'opencog_default_domain=""',
            'opencog_max_atoms=10000',
            'opencog_reasoning_steps=10'
        ]
        
        for default in default_values:
            assert default in content, f"Missing OpenCog default value: {default}"
            
        print("✓ OpenCog default settings are properly configured")
        
        # Check that UI section is defined
        ui_elements = [
            'opencog_section: SettingsSection',
            '"id": "opencog"',
            '"title": "OpenCog Integration"',
            'opencog_enabled',
            'opencog_atomspace_persistence',
            'opencog_reasoning_engine',
            'opencog_default_domain',
            'opencog_max_atoms',
            'opencog_reasoning_steps'
        ]
        
        for element in ui_elements:
            assert element in content, f"Missing OpenCog UI element: {element}"
            
        print("✓ OpenCog settings UI section is properly configured")
        
        # Check that section is added to the sections list
        assert 'opencog_section,' in content, "OpenCog section not added to sections list"
        print("✓ OpenCog section is included in settings output")
        
        return True
        
    except Exception as e:
        print(f"✗ OpenCog settings test failed: {e}")
        return False

def test_opencog_extension_settings_integration():
    """Test that the extension properly reads settings."""
    try:
        # Get the project root directory
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(test_dir)
        extension_file = os.path.join(project_root, 'python', 'extensions', 'agent_init', '_05_opencog_init.py')
        
        with open(extension_file, 'r') as f:
            content = f.read()
        
        # Check that settings are imported and used
        assert 'from python.helpers.settings import get_settings' in content
        assert 'settings = get_settings()' in content
        assert 'settings.get("opencog_enabled"' in content
        assert 'settings.get("opencog_default_domain"' in content
        
        print("✓ OpenCog extension properly integrates with settings")
        return True
        
    except Exception as e:
        print(f"✗ OpenCog extension settings test failed: {e}")
        return False

def test_opencog_settings_validation():
    """Test that OpenCog settings have proper validation and constraints."""
    try:
        # Get the project root directory
        test_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(test_dir)
        settings_file = os.path.join(project_root, 'python', 'helpers', 'settings.py')
        
        with open(settings_file, 'r') as f:
            content = f.read()
        
        # Check for proper field types and constraints
        validation_elements = [
            '"type": "switch"',  # For boolean settings
            '"type": "select"',  # For enum settings
            '"type": "number"',  # For numeric settings
            '"min": 1000',       # For max_atoms constraint
            '"max": 100000',     # For max_atoms constraint
            '"min": 1',          # For reasoning_steps constraint
            '"max": 50',         # For reasoning_steps constraint
        ]
        
        for element in validation_elements:
            assert element in content, f"Missing validation element: {element}"
        
        print("✓ OpenCog settings have proper validation and constraints")
        return True
        
    except Exception as e:
        print(f"✗ OpenCog settings validation test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing OpenCog settings integration...")
    print()
    
    success = True
    
    if not test_opencog_settings_structure():
        success = False
    
    if not test_opencog_extension_settings_integration():
        success = False
        
    if not test_opencog_settings_validation():
        success = False
    
    print()
    if success:
        print("✓ All OpenCog settings tests passed!")
    else:
        print("✗ Some OpenCog settings tests failed!")
        exit(1)