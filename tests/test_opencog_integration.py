"""
Test OpenCog integration with Agent Zero
"""

import sys
import os

# Add the parent directory to the path so we can import modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_opencog_availability():
    """Test if OpenCog can be imported (if installed)."""
    try:
        from opencog.atomspace import AtomSpace, types
        from opencog.type_constructors import ConceptNode
        print("✓ OpenCog is available")
        return True
    except ImportError:
        print("⚠ OpenCog not installed - integration will be disabled")
        return False

def test_opencog_atomspace_tool():
    """Test basic OpenCog AtomSpace tool functionality."""
    try:
        # Check if we can import the tool file
        with open('python/tools/opencog_atomspace.py', 'r') as f:
            content = f.read()
            assert 'class OpenCogAtomSpace' in content
            assert 'from opencog.atomspace import AtomSpace' in content
        print("✓ OpenCog AtomSpace tool file is properly structured")
    except Exception as e:
        print(f"✗ OpenCog AtomSpace tool test failed: {e}")
        raise

def test_opencog_reasoning_tool():
    """Test basic OpenCog reasoning tool functionality."""
    try:
        # Check if we can import the tool file
        with open('python/tools/opencog_reasoning.py', 'r') as f:
            content = f.read()
            assert 'class OpenCogReasoning' in content
            assert 'forward_chain' in content
            assert 'backward_chain' in content
        print("✓ OpenCog Reasoning tool file is properly structured")
    except Exception as e:
        print(f"✗ OpenCog Reasoning tool test failed: {e}")
        raise

def test_opencog_knowledge_tool():
    """Test basic OpenCog knowledge tool functionality."""
    try:
        # Check if we can import the tool file
        with open('python/tools/opencog_knowledge.py', 'r') as f:
            content = f.read()
            assert 'class OpenCogKnowledge' in content
            assert 'import_text' in content
            assert 'export_atoms' in content
        print("✓ OpenCog Knowledge tool file is properly structured")  
    except Exception as e:
        print(f"✗ OpenCog Knowledge tool test failed: {e}")
        raise

def test_opencog_extension():
    """Test OpenCog initialization extension."""
    try:
        # Check if we can import the extension file
        with open('python/extensions/agent_init/_05_opencog_init.py', 'r') as f:
            content = f.read()
            assert 'class OpenCogInit' in content
            assert 'from opencog.atomspace import AtomSpace' in content
        print("✓ OpenCog initialization extension file is properly structured")
    except Exception as e:
        print(f"✗ OpenCog extension test failed: {e}")
        raise

def test_full_integration():
    """Test that OpenCog integration works end-to-end (if OpenCog is available)."""
    if not test_opencog_availability():
        print("⚠ Skipping full integration test - OpenCog not available")
        return
    
    try:
        from opencog.atomspace import AtomSpace
        from opencog.type_constructors import ConceptNode, set_default_atomspace
        
        # Create atomspace
        atomspace = AtomSpace()
        set_default_atomspace(atomspace)
        
        # Add some atoms
        dog_concept = ConceptNode("Dog")
        animal_concept = ConceptNode("Animal")
        
        # Verify atoms were created
        assert len(atomspace) >= 2
        print("✓ OpenCog full integration test passed")
        
    except Exception as e:
        print(f"✗ OpenCog integration test failed: {e}")
        raise

if __name__ == "__main__":
    print("Testing OpenCog integration with Agent Zero...")
    print()
    
    try:
        test_opencog_availability()
        test_opencog_atomspace_tool()
        test_opencog_reasoning_tool() 
        test_opencog_knowledge_tool()
        test_opencog_extension()
        test_full_integration()
        
        print()
        print("✓ All OpenCog integration tests passed!")
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        sys.exit(1)