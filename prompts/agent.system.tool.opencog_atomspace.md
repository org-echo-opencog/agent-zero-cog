# OpenCog AtomSpace Tool

## Description
The `opencog_atomspace` tool provides access to OpenCog's AtomSpace for advanced knowledge representation and cognitive processing. AtomSpace is a graph-based knowledge database that allows for sophisticated reasoning and learning.

## Usage

### Basic Information
```
tool: opencog_atomspace
action: info
```
Get information about the current AtomSpace state.

### Managing Concepts
```
tool: opencog_atomspace
action: add_concept
name: "ConceptName"
```
Add a concept node to the AtomSpace.

### Managing Facts
```
tool: opencog_atomspace
action: add_fact
predicate: "relationship_name"
subject: "SubjectConcept"
object: "ObjectConcept"
```
Add a fact as an evaluation link (subject-predicate-object triple).

### Querying Knowledge
```
tool: opencog_atomspace  
action: query
pattern: "search_term"
```
Search for atoms matching a pattern.

### Listing Atoms
```
tool: opencog_atomspace
action: list_atoms
atom_type: "ConceptNode"
limit: 10
```
List atoms of a specific type. Common types: ConceptNode, PredicateNode, EvaluationLink.

### Getting Specific Atoms
```
tool: opencog_atomspace
action: get_atom
name: "AtomName"
```
Retrieve a specific atom by name.

### Counting Atoms
```
tool: opencog_atomspace
action: count
atom_type: "ConceptNode"  # optional - if not provided, counts all atoms
```
Count atoms in the AtomSpace.

### Clearing AtomSpace
```
tool: opencog_atomspace
action: clear
```
Clear all atoms from the AtomSpace.

## Examples

Add concepts and relationships:
```
tool: opencog_atomspace
action: add_concept
name: "Dog"
```

```
tool: opencog_atomspace
action: add_concept  
name: "Animal"
```

```
tool: opencog_atomspace
action: add_fact
predicate: "is_a"
subject: "Dog"
object: "Animal"
```

Query for relationships:
```
tool: opencog_atomspace
action: query
pattern: "Dog"
```

## Notes
- AtomSpace provides sophisticated knowledge representation beyond simple key-value storage
- Supports complex reasoning and inference through graph structures
- Concepts and relationships are automatically created as needed
- Use this for cognitive tasks requiring logical reasoning and knowledge graphs