from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
from python.helpers import files
import json
import os

class OpenCogKnowledge(Tool):
    """
    Tool for importing, exporting, and managing knowledge in OpenCog AtomSpace.
    
    This tool provides functionality to:
    - Import knowledge from various formats (text, JSON, structured data)
    - Export AtomSpace contents to different formats
    - Load domain-specific knowledge bases
    - Convert between different knowledge representations
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._atomspace = None
        self._initialize_opencog()

    def _initialize_opencog(self):
        """Initialize OpenCog components."""
        try:
            from opencog.atomspace import AtomSpace, types
            from opencog.type_constructors import (
                ConceptNode, PredicateNode, EvaluationLink, 
                InheritanceLink, ListLink, set_default_atomspace
            )
            
            self._atomspace = AtomSpace()
            set_default_atomspace(self._atomspace)
            
            self._types = types
            self._ConceptNode = ConceptNode
            self._PredicateNode = PredicateNode
            self._EvaluationLink = EvaluationLink
            self._InheritanceLink = InheritanceLink
            self._ListLink = ListLink
            
        except ImportError as e:
            PrintStyle.error(f"OpenCog not available: {e}")
            self._atomspace = None

    async def execute(self, action="info", **kwargs):
        """
        Execute OpenCog knowledge management operations.
        
        Actions:
        - info: Get information about knowledge base
        - import_text: Import knowledge from plain text
        - import_json: Import knowledge from JSON format
        - import_triples: Import RDF-like triples
        - export_atoms: Export atoms to various formats
        - load_domain: Load domain-specific knowledge
        - save_knowledge: Save current knowledge to file
        - clear_knowledge: Clear all knowledge
        """
        
        if not self._atomspace:
            return Response(
                message="OpenCog knowledge management is not available. Please install OpenCog.",
                break_loop=False
            )

        try:
            if action == "info":
                return await self._get_knowledge_info()
            elif action == "import_text":
                return await self._import_text(**kwargs)
            elif action == "import_json":
                return await self._import_json(**kwargs)
            elif action == "import_triples":
                return await self._import_triples(**kwargs)
            elif action == "export_atoms":
                return await self._export_atoms(**kwargs)
            elif action == "load_domain":
                return await self._load_domain(**kwargs)
            elif action == "save_knowledge":
                return await self._save_knowledge(**kwargs)
            elif action == "clear_knowledge":
                return await self._clear_knowledge()
            else:
                available_actions = ["info", "import_text", "import_json", "import_triples", 
                                   "export_atoms", "load_domain", "save_knowledge", "clear_knowledge"]
                return Response(
                    message=f"Unknown action '{action}'. Available actions: {', '.join(available_actions)}",
                    break_loop=False
                )
                
        except Exception as e:
            PrintStyle.error(f"OpenCog knowledge operation failed: {e}")
            return Response(
                message=f"Knowledge operation failed: {str(e)}",
                break_loop=False
            )

    async def _get_knowledge_info(self):
        """Get information about the current knowledge base."""
        atom_count = len(self._atomspace)
        
        # Count different atom types
        concept_count = len(self._atomspace.get_atoms_by_type(self._types.ConceptNode))
        predicate_count = len(self._atomspace.get_atoms_by_type(self._types.PredicateNode))
        evaluation_count = len(self._atomspace.get_atoms_by_type(self._types.EvaluationLink))
        inheritance_count = len(self._atomspace.get_atoms_by_type(self._types.InheritanceLink))
        
        info = f"""OpenCog Knowledge Base Information:
- Total atoms: {atom_count}
- Concept nodes: {concept_count}
- Predicate nodes: {predicate_count}
- Evaluation links (facts): {evaluation_count}
- Inheritance links: {inheritance_count}

Knowledge operations available:
- Import text: action="import_text", text="knowledge text"
- Import JSON: action="import_json", file_path="path/to/file.json"
- Import triples: action="import_triples", triples=[["subject", "predicate", "object"]]
- Export atoms: action="export_atoms", format="text|json"
- Load domain knowledge: action="load_domain", domain="AI|science|common_sense"
"""
        return Response(message=info, break_loop=False)

    async def _import_text(self, text="", **kwargs):
        """Import knowledge from plain text by extracting facts and relationships."""
        if not text:
            return Response(
                message="Error: 'text' parameter required for import_text",
                break_loop=False
            )
        
        # Simple text processing to extract concepts and relationships
        sentences = text.split('.')
        concepts_added = []
        facts_added = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if not sentence:
                continue
                
            # Extract concepts (words that start with capital letters)
            words = sentence.split()
            concepts = [word.strip('.,!?') for word in words if word[0].isupper() and len(word) > 1]
            
            for concept in concepts:
                if concept not in concepts_added:
                    concept_node = self._ConceptNode(concept)
                    self._atomspace.add(concept_node)
                    concepts_added.append(concept)
            
            # Look for simple relationship patterns
            if ' is ' in sentence.lower():
                parts = sentence.lower().split(' is ')
                if len(parts) == 2:
                    subject = parts[0].strip().title()
                    object_part = parts[1].strip().title()
                    
                    # Create inheritance relationship
                    if subject and object_part:
                        subject_node = self._ConceptNode(subject)
                        object_node = self._ConceptNode(object_part)
                        inheritance = self._InheritanceLink(subject_node, object_node)
                        self._atomspace.add(inheritance)
                        facts_added.append(f"{subject} is {object_part}")
        
        result = f"Imported knowledge from text:\n"
        result += f"- Concepts added: {len(concepts_added)} ({', '.join(concepts_added[:5])}{'...' if len(concepts_added) > 5 else ''})\n"
        result += f"- Facts added: {len(facts_added)}"
        if facts_added:
            result += f" ({facts_added[0]}{'...' if len(facts_added) > 1 else ''})"
        
        return Response(message=result, break_loop=False)

    async def _import_json(self, file_path="", data=None, **kwargs):
        """Import knowledge from JSON format."""
        if not file_path and not data:
            return Response(
                message="Error: Either 'file_path' or 'data' parameter required for import_json",
                break_loop=False
            )
        
        try:
            if file_path:
                with open(files.get_abs_path(file_path), 'r') as f:
                    knowledge_data = json.load(f)
            else:
                knowledge_data = data if isinstance(data, dict) else json.loads(data)
            
            imported_count = 0
            
            # Import concepts
            if 'concepts' in knowledge_data:
                for concept in knowledge_data['concepts']:
                    concept_node = self._ConceptNode(concept)
                    self._atomspace.add(concept_node)
                    imported_count += 1
            
            # Import facts/relationships
            if 'facts' in knowledge_data:
                for fact in knowledge_data['facts']:
                    if isinstance(fact, dict) and 'subject' in fact and 'predicate' in fact and 'object' in fact:
                        subject_node = self._ConceptNode(fact['subject'])
                        predicate_node = self._PredicateNode(fact['predicate'])
                        object_node = self._ConceptNode(fact['object'])
                        
                        evaluation = self._EvaluationLink(
                            predicate_node,
                            self._ListLink(subject_node, object_node)
                        )
                        self._atomspace.add(evaluation)
                        imported_count += 1
            
            # Import inheritance relationships
            if 'inheritance' in knowledge_data:
                for inheritance in knowledge_data['inheritance']:
                    if isinstance(inheritance, dict) and 'child' in inheritance and 'parent' in inheritance:
                        child_node = self._ConceptNode(inheritance['child'])
                        parent_node = self._ConceptNode(inheritance['parent'])
                        
                        inheritance_link = self._InheritanceLink(child_node, parent_node)
                        self._atomspace.add(inheritance_link)
                        imported_count += 1
            
            return Response(
                message=f"Successfully imported {imported_count} knowledge items from JSON",
                break_loop=False
            )
            
        except Exception as e:
            return Response(
                message=f"Failed to import JSON knowledge: {str(e)}",
                break_loop=False
            )

    async def _import_triples(self, triples=None, **kwargs):
        """Import knowledge as RDF-like triples [subject, predicate, object]."""
        if not triples:
            return Response(
                message="Error: 'triples' parameter required (list of [subject, predicate, object] lists)",
                break_loop=False
            )
        
        if not isinstance(triples, list):
            return Response(
                message="Error: 'triples' must be a list of [subject, predicate, object] lists",
                break_loop=False
            )
        
        imported_count = 0
        
        for triple in triples:
            if not isinstance(triple, list) or len(triple) != 3:
                continue
                
            subject, predicate, obj = triple
            
            subject_node = self._ConceptNode(str(subject))
            predicate_node = self._PredicateNode(str(predicate))
            object_node = self._ConceptNode(str(obj))
            
            evaluation = self._EvaluationLink(
                predicate_node,
                self._ListLink(subject_node, object_node)
            )
            self._atomspace.add(evaluation)
            imported_count += 1
        
        return Response(
            message=f"Successfully imported {imported_count} triples as facts",
            break_loop=False
        )

    async def _export_atoms(self, format="text", atom_type="all", **kwargs):
        """Export atoms to various formats."""
        if format not in ["text", "json"]:
            return Response(
                message="Error: format must be 'text' or 'json'",
                break_loop=False
            )
        
        if format == "text":
            return await self._export_text(atom_type)
        else:
            return await self._export_json(atom_type)

    async def _export_text(self, atom_type="all"):
        """Export atoms as human-readable text."""
        lines = ["OpenCog AtomSpace Export:\n"]
        
        if atom_type == "all" or atom_type == "concepts":
            concepts = self._atomspace.get_atoms_by_type(self._types.ConceptNode)
            if concepts:
                lines.append("Concepts:")
                for concept in concepts:
                    lines.append(f"  - {concept.name}")
                lines.append("")
        
        if atom_type == "all" or atom_type == "facts":
            evaluations = self._atomspace.get_atoms_by_type(self._types.EvaluationLink)
            if evaluations:
                lines.append("Facts:")
                for evaluation in evaluations:
                    if len(evaluation.out) >= 2:
                        predicate = evaluation.out[0]
                        if hasattr(predicate, 'name'):
                            predicate_name = predicate.name
                        else:
                            predicate_name = str(predicate)
                        
                        args = evaluation.out[1]
                        if hasattr(args, 'out') and len(args.out) >= 2:
                            subject = args.out[0].name if hasattr(args.out[0], 'name') else str(args.out[0])
                            obj = args.out[1].name if hasattr(args.out[1], 'name') else str(args.out[1])
                            lines.append(f"  - {subject} {predicate_name} {obj}")
                lines.append("")
        
        if atom_type == "all" or atom_type == "inheritance":
            inheritances = self._atomspace.get_atoms_by_type(self._types.InheritanceLink)
            if inheritances:
                lines.append("Inheritance relationships:")
                for inheritance in inheritances:
                    if len(inheritance.out) >= 2:
                        child = inheritance.out[0].name if hasattr(inheritance.out[0], 'name') else str(inheritance.out[0])
                        parent = inheritance.out[1].name if hasattr(inheritance.out[1], 'name') else str(inheritance.out[1])
                        lines.append(f"  - {child} inherits from {parent}")
        
        result = "\n".join(lines)
        return Response(message=result, break_loop=False)

    async def _export_json(self, atom_type="all"):
        """Export atoms as structured JSON."""
        export_data = {}
        
        if atom_type == "all" or atom_type == "concepts":
            concepts = self._atomspace.get_atoms_by_type(self._types.ConceptNode)
            export_data['concepts'] = [concept.name for concept in concepts if hasattr(concept, 'name')]
        
        if atom_type == "all" or atom_type == "facts":
            evaluations = self._atomspace.get_atoms_by_type(self._types.EvaluationLink)
            facts = []
            for evaluation in evaluations:
                if len(evaluation.out) >= 2:
                    predicate = evaluation.out[0]
                    predicate_name = predicate.name if hasattr(predicate, 'name') else str(predicate)
                    
                    args = evaluation.out[1]
                    if hasattr(args, 'out') and len(args.out) >= 2:
                        subject = args.out[0].name if hasattr(args.out[0], 'name') else str(args.out[0])
                        obj = args.out[1].name if hasattr(args.out[1], 'name') else str(args.out[1])
                        facts.append({
                            'subject': subject,
                            'predicate': predicate_name,
                            'object': obj
                        })
            export_data['facts'] = facts
        
        if atom_type == "all" or atom_type == "inheritance":
            inheritances = self._atomspace.get_atoms_by_type(self._types.InheritanceLink)
            inheritance_list = []
            for inheritance in inheritances:
                if len(inheritance.out) >= 2:
                    child = inheritance.out[0].name if hasattr(inheritance.out[0], 'name') else str(inheritance.out[0])
                    parent = inheritance.out[1].name if hasattr(inheritance.out[1], 'name') else str(inheritance.out[1])
                    inheritance_list.append({
                        'child': child,
                        'parent': parent
                    })
            export_data['inheritance'] = inheritance_list
        
        result = f"Exported OpenCog knowledge as JSON:\n{json.dumps(export_data, indent=2)}"
        return Response(message=result, break_loop=False)

    async def _load_domain(self, domain="", **kwargs):
        """Load domain-specific knowledge."""
        if not domain:
            return Response(
                message="Error: 'domain' parameter required. Available domains: AI, science, common_sense",
                break_loop=False
            )
        
        domain_knowledge = self._get_domain_knowledge(domain.lower())
        
        if not domain_knowledge:
            return Response(
                message=f"Unknown domain '{domain}'. Available domains: AI, science, common_sense",
                break_loop=False
            )
        
        added_count = 0
        
        # Add concepts
        for concept in domain_knowledge.get('concepts', []):
            concept_node = self._ConceptNode(concept)
            self._atomspace.add(concept_node)
            added_count += 1
        
        # Add inheritance relationships
        for inheritance in domain_knowledge.get('inheritance', []):
            child_node = self._ConceptNode(inheritance['child'])
            parent_node = self._ConceptNode(inheritance['parent'])
            inheritance_link = self._InheritanceLink(child_node, parent_node)
            self._atomspace.add(inheritance_link)
            added_count += 1
        
        # Add facts
        for fact in domain_knowledge.get('facts', []):
            subject_node = self._ConceptNode(fact['subject'])
            predicate_node = self._PredicateNode(fact['predicate'])
            object_node = self._ConceptNode(fact['object'])
            
            evaluation = self._EvaluationLink(
                predicate_node,
                self._ListLink(subject_node, object_node)
            )
            self._atomspace.add(evaluation)
            added_count += 1
        
        return Response(
            message=f"Loaded {added_count} knowledge items from domain: {domain}",
            break_loop=False
        )

    def _get_domain_knowledge(self, domain):
        """Get predefined knowledge for specific domains."""
        domains = {
            'ai': {
                'concepts': ['ArtificialIntelligence', 'MachineLearning', 'NeuralNetwork', 'Agent', 'Algorithm', 'Model'],
                'inheritance': [
                    {'child': 'MachineLearning', 'parent': 'ArtificialIntelligence'},
                    {'child': 'NeuralNetwork', 'parent': 'MachineLearning'},
                    {'child': 'Agent', 'parent': 'ArtificialIntelligence'}
                ],
                'facts': [
                    {'subject': 'Agent', 'predicate': 'can_perform', 'object': 'Tasks'},
                    {'subject': 'NeuralNetwork', 'predicate': 'learns_from', 'object': 'Data'},
                    {'subject': 'Algorithm', 'predicate': 'solves', 'object': 'Problems'}
                ]
            },
            'science': {
                'concepts': ['Physics', 'Chemistry', 'Biology', 'Mathematics', 'Atom', 'Cell', 'Energy'],
                'inheritance': [
                    {'child': 'Physics', 'parent': 'Science'},
                    {'child': 'Chemistry', 'parent': 'Science'},
                    {'child': 'Biology', 'parent': 'Science'}
                ],
                'facts': [
                    {'subject': 'Atom', 'predicate': 'composed_of', 'object': 'Protons'},
                    {'subject': 'Cell', 'predicate': 'basic_unit_of', 'object': 'Life'},
                    {'subject': 'Energy', 'predicate': 'cannot_be', 'object': 'Destroyed'}
                ]
            },
            'common_sense': {
                'concepts': ['Human', 'Animal', 'Plant', 'Water', 'Fire', 'Air', 'Food'],
                'inheritance': [
                    {'child': 'Human', 'parent': 'Animal'},
                    {'child': 'Dog', 'parent': 'Animal'},
                    {'child': 'Rose', 'parent': 'Plant'}
                ],
                'facts': [
                    {'subject': 'Human', 'predicate': 'needs', 'object': 'Food'},
                    {'subject': 'Plant', 'predicate': 'needs', 'object': 'Water'},
                    {'subject': 'Fire', 'predicate': 'produces', 'object': 'Heat'}
                ]
            }
        }
        
        return domains.get(domain)

    async def _save_knowledge(self, file_path="opencog_knowledge.json", **kwargs):
        """Save current knowledge to file."""
        try:
            export_result = await self._export_json("all")
            # Extract JSON from the response message
            json_start = export_result.message.find('{')
            if json_start != -1:
                json_data = export_result.message[json_start:]
                
                abs_path = files.get_abs_path("tmp", file_path)
                with open(abs_path, 'w') as f:
                    f.write(json_data)
                
                return Response(
                    message=f"Knowledge saved to: {abs_path}",
                    break_loop=False
                )
            else:
                return Response(
                    message="Failed to extract JSON data for saving",
                    break_loop=False
                )
                
        except Exception as e:
            return Response(
                message=f"Failed to save knowledge: {str(e)}",
                break_loop=False
            )

    async def _clear_knowledge(self, **kwargs):
        """Clear all knowledge from AtomSpace."""
        initial_count = len(self._atomspace)
        self._atomspace.clear()
        
        return Response(
            message=f"Cleared all knowledge. Removed {initial_count} atoms.",
            break_loop=False
        )