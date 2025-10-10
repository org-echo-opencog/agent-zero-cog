# OpenCog Integration with Agent Zero

## Overview

Agent Zero now includes comprehensive integration with OpenCog, a framework for Artificial General Intelligence (AGI). This integration provides advanced cognitive capabilities including sophisticated knowledge representation, logical reasoning, and pattern matching.

## What is OpenCog?

OpenCog is an AGI framework that combines multiple AI approaches to create more comprehensive intelligent systems. Its core component, AtomSpace, serves as a knowledge representation database that enables complex reasoning and learning tasks.

## Features

The OpenCog integration provides three main tools:

### 1. OpenCog AtomSpace (`opencog_atomspace`)
- **Knowledge Representation**: Store concepts, facts, and relationships in a graph-based knowledge database
- **Atom Management**: Create, query, and manage different types of atoms (concepts, predicates, links)
- **Knowledge Queries**: Search and retrieve knowledge using pattern matching
- **Graph Operations**: Build and navigate complex knowledge graphs

### 2. OpenCog Reasoning (`opencog_reasoning`)
- **Logical Inference**: Perform forward and backward chaining reasoning
- **Rule-based Logic**: Define and apply logical rules and implications
- **Pattern Matching**: Find structural patterns in knowledge bases
- **Cognitive Reasoning**: Solve problems requiring multi-step logical inference

### 3. OpenCog Knowledge Management (`opencog_knowledge`)
- **Knowledge Import/Export**: Load knowledge from text, JSON, and structured formats
- **Domain Knowledge**: Access pre-built knowledge bases for AI, science, and common sense
- **Knowledge Conversion**: Transform between different knowledge representations
- **Backup/Restore**: Save and restore complete knowledge bases

## Installation

### Prerequisites
OpenCog integration requires the OpenCog Python packages:

```bash
pip install opencog==5.0.3
pip install opencog-cogserver==5.0.3
```

**Note**: If OpenCog is not installed, Agent Zero will continue to work normally but OpenCog tools will be disabled with informative messages.

### Verification
Run the integration test to verify installation:

```bash
python tests/test_opencog_integration.py
```

## Quick Start

### Basic Knowledge Building
```python
# Initialize AtomSpace and add some concepts
tool: opencog_atomspace
action: add_concept
name: "Dog"

tool: opencog_atomspace  
action: add_concept
name: "Animal"

# Create relationships
tool: opencog_atomspace
action: add_fact
predicate: "is_a"
subject: "Dog"
object: "Animal"
```

### Reasoning Example
```python
# Add reasoning rules
tool: opencog_reasoning
action: add_inheritance
parent: "Animal"
child: "Dog"

tool: opencog_reasoning
action: add_implication
antecedent: "Animal"
consequent: "NeedsFood"

# Perform inference
tool: opencog_reasoning
action: forward_chain
premises: ["Dog"]
# This will infer "NeedsFood" because Dog->Animal->NeedsFood
```

### Knowledge Import
```python
# Load domain knowledge
tool: opencog_knowledge
action: load_domain
domain: "AI"

# Import from text
tool: opencog_knowledge
action: import_text
text: "Machine learning is a subset of artificial intelligence. Neural networks are machine learning models."

# Export for review
tool: opencog_knowledge
action: export_atoms
format: "text"
```

## Advanced Usage

### Complex Reasoning Workflows
1. **Knowledge Preparation**: Load domain knowledge and import specific facts
2. **Rule Definition**: Define logical rules and implications
3. **Inference Execution**: Perform forward/backward chaining
4. **Result Analysis**: Query and validate inferred conclusions

### Integration with Agent Zero Features
- **Memory System**: OpenCog complements Agent Zero's memory system with structured knowledge representation
- **Tool Coordination**: Combine OpenCog reasoning with other Agent Zero tools for complex problem solving
- **Multi-Agent Systems**: Share knowledge bases between agent instances

## Use Cases

### Scientific Reasoning
- Build knowledge bases of scientific facts and relationships  
- Perform logical inference to derive new scientific conclusions
- Model complex domain knowledge (physics, chemistry, biology)

### Software Development
- Represent code structures and relationships
- Reason about software architectures and dependencies
- Model programming concepts and best practices

### General Problem Solving
- Break down complex problems into logical components
- Apply systematic reasoning to find solutions
- Build and query knowledge about problem domains

## Architecture Integration

The OpenCog integration follows Agent Zero's extensible architecture:

### Tools
- `opencog_atomspace.py`: Core AtomSpace operations
- `opencog_reasoning.py`: Reasoning and inference engine
- `opencog_knowledge.py`: Knowledge import/export utilities

### Extensions
- `_05_opencog_init.py`: Initializes OpenCog when agents start

### Prompts
- Tool instruction files provide detailed usage guidance
- Example prompts demonstrate cognitive reasoning patterns

## Performance Considerations

- **Memory Usage**: AtomSpace stores knowledge in memory; monitor usage for large knowledge bases
- **Reasoning Complexity**: Complex inference operations may take time for large knowledge graphs
- **Initialization**: OpenCog initialization adds minimal overhead to agent startup

## Troubleshooting

### OpenCog Not Available
If you see "OpenCog not available" messages:
1. Install OpenCog packages: `pip install opencog opencog-cogserver`
2. Verify installation with the integration test
3. Check Python path includes OpenCog libraries

### Import Errors
- Ensure Python version compatibility (OpenCog supports Python 3.6+)
- Install OpenCog dependencies as described in OpenCog documentation
- Try installing from source if binary packages fail

### Performance Issues
- Monitor AtomSpace size with `action: info` commands
- Clear unused knowledge with `action: clear` when appropriate
- Use domain-specific knowledge loading instead of loading everything

## Examples

See `prompts/example_opencog_usage.md` for comprehensive examples of:
- Building knowledge bases from scratch
- Performing multi-step reasoning
- Integrating OpenCog with other Agent Zero capabilities
- Solving complex cognitive tasks

## Contributing

To extend OpenCog integration:
1. Add new reasoning algorithms to `opencog_reasoning.py`
2. Implement additional knowledge formats in `opencog_knowledge.py`
3. Create domain-specific knowledge modules
4. Add new AtomSpace operations as needed

The integration is designed to be modular and extensible while maintaining compatibility with Agent Zero's architecture.