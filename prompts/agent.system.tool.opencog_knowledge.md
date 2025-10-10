# OpenCog Knowledge Management Tool

## Description
The `opencog_knowledge` tool provides comprehensive knowledge import/export and management capabilities for OpenCog AtomSpace. It allows loading knowledge from various sources and formats, exporting knowledge bases, and managing domain-specific knowledge.

## Usage

### Basic Information
```
tool: opencog_knowledge
action: info
```
Get information about the current knowledge base.

### Importing Knowledge

#### From Plain Text
```
tool: opencog_knowledge
action: import_text
text: "Dogs are animals. Cats are animals. Animals need food."
```
Automatically extract concepts and relationships from natural language text.

#### From JSON
```
tool: opencog_knowledge
action: import_json
file_path: "knowledge/animals.json"
```

Or with direct data:
```
tool: opencog_knowledge
action: import_json
data: {
  "concepts": ["Dog", "Cat", "Animal"],
  "facts": [
    {"subject": "Dog", "predicate": "needs", "object": "Food"}
  ],
  "inheritance": [
    {"child": "Dog", "parent": "Animal"}
  ]
}
```

#### From Triples
```
tool: opencog_knowledge
action: import_triples
triples: [
  ["Dog", "is_a", "Animal"],
  ["Cat", "is_a", "Animal"],
  ["Animal", "needs", "Food"]
]
```
Import RDF-style subject-predicate-object triples.

### Exporting Knowledge

#### As Human-Readable Text
```
tool: opencog_knowledge
action: export_atoms
format: "text"
atom_type: "all"  # or "concepts", "facts", "inheritance"
```

#### As Structured JSON
```
tool: opencog_knowledge
action: export_atoms
format: "json"
atom_type: "all"
```

### Domain Knowledge Loading
```
tool: opencog_knowledge
action: load_domain
domain: "AI"  # Available: "AI", "science", "common_sense"
```
Load predefined knowledge for specific domains.

### Saving/Loading Knowledge Base
```
tool: opencog_knowledge
action: save_knowledge
file_path: "my_knowledge.json"
```

```
tool: opencog_knowledge
action: import_json
file_path: "my_knowledge.json"
```

### Clearing Knowledge
```
tool: opencog_knowledge
action: clear_knowledge
```
Clear all knowledge from the AtomSpace.

## Examples

### Building a Knowledge Base
```
tool: opencog_knowledge
action: load_domain
domain: "AI"
```

```
tool: opencog_knowledge
action: import_text
text: "Machine learning is a subset of artificial intelligence. Neural networks are a type of machine learning model. Deep learning uses neural networks with many layers."
```

### Working with Custom Knowledge
```
tool: opencog_knowledge
action: import_triples
triples: [
  ["Python", "is_a", "ProgrammingLanguage"],
  ["JavaScript", "is_a", "ProgrammingLanguage"],
  ["ProgrammingLanguage", "used_for", "SoftwareDevelopment"]
]
```

### Exporting for Review
```
tool: opencog_knowledge
action: export_atoms
format: "text"
atom_type: "facts"
```

## JSON Knowledge Format
When importing JSON, use this structure:
```json
{
  "concepts": ["Concept1", "Concept2"],
  "facts": [
    {
      "subject": "Subject",
      "predicate": "relationship",
      "object": "Object"
    }
  ],
  "inheritance": [
    {
      "child": "ChildConcept",
      "parent": "ParentConcept"
    }
  ]
}
```

## Available Domains
- **AI**: Artificial intelligence, machine learning, agents, algorithms
- **science**: Physics, chemistry, biology, mathematics concepts  
- **common_sense**: Basic human knowledge about everyday objects and relationships

## Notes
- Text import uses simple NLP to extract concepts and relationships
- JSON format provides precise control over knowledge structure
- Triples format is compatible with RDF and semantic web standards
- Domain loading provides quick access to common knowledge areas
- All imported knowledge integrates with OpenCog reasoning capabilities
- Export functions help review and backup your knowledge bases