# OpenCog Reasoning Tool

## Description
The `opencog_reasoning` tool provides access to OpenCog's reasoning engines for logical inference, pattern matching, and knowledge derivation. It enables sophisticated cognitive reasoning capabilities beyond simple data retrieval.

## Usage

### Basic Information
```
tool: opencog_reasoning
action: info
```
Get information about available reasoning capabilities.

### Adding Reasoning Rules
```
tool: opencog_reasoning
action: add_inheritance
parent: "ParentConcept"
child: "ChildConcept"
```
Add an inheritance relationship (ChildConcept inherits from ParentConcept).

```
tool: opencog_reasoning
action: add_implication
antecedent: "Condition"
consequent: "Result"
```
Add an implication rule (if Condition then Result).

### Performing Inference
```
tool: opencog_reasoning
action: forward_chain
premises: ["premise1", "premise2"]
max_steps: 10
```
Perform forward chaining inference from given premises.

```
tool: opencog_reasoning
action: backward_chain
goal: "GoalToProve"
max_depth: 5
```
Perform backward chaining to prove a goal.

### Pattern Matching
```
tool: opencog_reasoning
action: pattern_match
pattern: "search_pattern"
```
Find patterns in the knowledge base.

### General Inference
```
tool: opencog_reasoning
action: infer
query: "QueryConcept"
method: "forward"  # or "backward" or "pattern"
```
Perform general inference using specified method.

## Examples

Build a knowledge base with reasoning:
```
tool: opencog_reasoning
action: add_inheritance
parent: "Animal"
child: "Dog"
```

```
tool: opencog_reasoning
action: add_inheritance  
parent: "Animal"
child: "Cat"
```

```
tool: opencog_reasoning
action: add_implication
antecedent: "Animal"
consequent: "NeedsFood"
```

Perform forward chaining:
```
tool: opencog_reasoning
action: forward_chain
premises: ["Dog"]
```
This should infer "NeedsFood" because Dog->Animal->NeedsFood.

Prove a goal:
```
tool: opencog_reasoning
action: backward_chain
goal: "NeedsFood"
```
This will try to find a proof path for why something needs food.

## Advanced Usage

Complex reasoning chains:
```
tool: opencog_reasoning
action: add_implication
antecedent: "Mammal"
consequent: "WarmBlooded"
```

```
tool: opencog_reasoning
action: forward_chain
premises: ["Dog", "Cat"]
max_steps: 15
```

## Notes
- Reasoning builds upon knowledge stored in AtomSpace
- Forward chaining derives new facts from known facts and rules
- Backward chaining works backwards from goals to find proofs  
- Pattern matching finds structural similarities in knowledge
- Combine with opencog_atomspace for complete cognitive processing
- Reasoning quality depends on the richness of your knowledge base