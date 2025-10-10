# Agent Delegation Hierarchy

This document demonstrates the multi-layered delegation system implemented in Agent Zero, providing examples of how to use the nested delegation capabilities.

## Overview

The Agent Zero system now supports up to 3 layers of nested delegation, allowing for sophisticated organizational structures:

1. **Individual Contributors** (0 layers of delegation)
2. **Team Leaders** (1 layer of delegation)
3. **Department Managers** (2 layers of delegation)
4. **Enterprise Directors** (3 layers of delegation)

## Agent Roles and Capabilities

### Individual Contributors (0-Layer Delegation)
These agents perform specific tasks directly without further delegation:

- **developer**: Software development, coding, architecture implementation
- **researcher**: Data analysis, research, documentation, investigation  
- **hacker**: Security testing, penetration testing, vulnerability assessment
- **analyst**: Business intelligence, data analysis, quantitative research
- **architect**: System architecture, technical design, solution blueprints
- **consultant**: Strategic advisory, process optimization, business transformation
- **product-manager**: Product strategy, roadmap planning, feature prioritization

### Team Leaders (1-Layer Delegation)
Team leaders coordinate individual contributors to deliver complex projects:

- Delegates to: developer, researcher, hacker, analyst, architect, consultant, product-manager
- Use case: Multi-disciplinary projects requiring coordination of specialists
- Example: Full-stack web application with security assessment and market research

### Department Managers (2-Layer Delegation)
Department managers oversee multiple teams through team leaders:

- Delegates to: team-leader agents (who then delegate to individual contributors)
- Use case: Large initiatives spanning multiple projects and specialist domains
- Example: Enterprise digital transformation with multiple concurrent workstreams

### Enterprise Directors (3-Layer Delegation)
Enterprise directors manage entire organizational portfolios:

- Delegates to: dept-manager agents (who delegate to team-leader agents, who delegate to individual contributors)
- Use case: Company-wide transformations, strategic initiatives, major organizational changes
- Example: Global market expansion with technology, operations, and partnership components

## Usage Examples

### Using call_subordinate Tool

```json
{
    "tool_name": "call_subordinate",
    "tool_args": {
        "profile": "team-leader",
        "message": "Develop a secure e-commerce platform with market analysis. Coordinate development, security testing, and competitive research.",
        "reset": "true"
    }
}
```

### Delegation Chain Example

1. **User** → **Enterprise Director**: "Launch a new product line in international markets"

2. **Enterprise Director** → **Department Manager**: "Execute product development and localization for European market entry"

3. **Department Manager** → **Team Leader**: "Develop multilingual product features and conduct market research for German market"

4. **Team Leader** → **Individual Contributors**:
   - **Developer**: "Implement i18n framework and German localization"
   - **Researcher**: "Analyze German e-commerce market and regulatory requirements"
   - **Product Manager**: "Define German-specific product features and pricing strategy"

## Best Practices

### When to Use Each Level

- **Individual Contributors**: Single-domain tasks (coding, research, analysis)
- **Team Leaders**: Multi-domain projects requiring specialist coordination
- **Department Managers**: Enterprise initiatives with multiple concurrent projects
- **Enterprise Directors**: Strategic transformations affecting entire organizations

### Delegation Guidelines

1. **Clear Scope Definition**: Each level should have well-defined boundaries and objectives
2. **Appropriate Complexity**: Match delegation level to task complexity and scope
3. **Resource Management**: Higher-level agents focus on coordination, not direct execution
4. **Quality Integration**: Each level ensures outputs integrate coherently with overall objectives

## Profile Selection

When using the `call_subordinate` tool, specify the appropriate profile:

```json
{
    "profile": "enterprise-director",  // For 3-layer delegation
    "profile": "dept-manager",         // For 2-layer delegation  
    "profile": "team-leader",          // For 1-layer delegation
    "profile": "developer"             // For direct execution
}
```

## Testing the System

The delegation hierarchy can be tested using the validation script:

```bash
python /tmp/test_agent_delegation.py
```

This validates that all agent profiles are discoverable and their contexts can be loaded properly.