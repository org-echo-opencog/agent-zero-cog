from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
import json

class OpenCogAtomSpace(Tool):
    """
    Tool for interacting with OpenCog AtomSpace for knowledge representation and reasoning.
    
    This tool provides access to OpenCog's knowledge representation and reasoning capabilities,
    allowing agents to store, retrieve, and reason over complex knowledge structures.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._atomspace = None
        self._initialize_atomspace()

    def _initialize_atomspace(self):
        """Initialize the OpenCog AtomSpace."""
        try:
            from opencog.atomspace import AtomSpace, types
            from opencog.type_constructors import ConceptNode, PredicateNode, EvaluationLink, ListLink
            
            self._atomspace = AtomSpace()
            self._types = types
            self._ConceptNode = ConceptNode
            self._PredicateNode = PredicateNode
            self._EvaluationLink = EvaluationLink
            self._ListLink = ListLink
            
            # Set the global atomspace for type constructors
            from opencog.type_constructors import set_default_atomspace
            set_default_atomspace(self._atomspace)
            
        except ImportError as e:
            PrintStyle.error(f"OpenCog not available: {e}")
            PrintStyle.warning("Please install OpenCog: pip install opencog")
            self._atomspace = None

    async def execute(self, action="info", **kwargs):
        """
        Execute OpenCog AtomSpace operations.
        
        Actions:
        - info: Get information about the AtomSpace
        - add_concept: Add a concept node
        - add_fact: Add a fact as an evaluation link
        - query: Query the AtomSpace 
        - list_atoms: List all atoms of a specific type
        - get_atom: Get specific atom by name
        - count: Count atoms in AtomSpace
        - clear: Clear the AtomSpace
        """
        
        if not self._atomspace:
            return Response(
                message="OpenCog AtomSpace is not available. Please install OpenCog.",
                break_loop=False
            )

        try:
            if action == "info":
                return await self._get_info()
            elif action == "add_concept":
                return await self._add_concept(**kwargs)
            elif action == "add_fact":
                return await self._add_fact(**kwargs)
            elif action == "query":
                return await self._query(**kwargs)
            elif action == "list_atoms":
                return await self._list_atoms(**kwargs)
            elif action == "get_atom":
                return await self._get_atom(**kwargs)
            elif action == "count":
                return await self._count_atoms(**kwargs)
            elif action == "clear":
                return await self._clear_atomspace()
            else:
                available_actions = ["info", "add_concept", "add_fact", "query", "list_atoms", "get_atom", "count", "clear"]
                return Response(
                    message=f"Unknown action '{action}'. Available actions: {', '.join(available_actions)}",
                    break_loop=False
                )
                
        except Exception as e:
            PrintStyle.error(f"OpenCog operation failed: {e}")
            return Response(
                message=f"OpenCog operation failed: {str(e)}",
                break_loop=False
            )

    async def _get_info(self):
        """Get information about the AtomSpace."""
        atom_count = len(self._atomspace)
        info = {
            "atom_count": atom_count,
            "atomspace_uuid": str(self._atomspace.get_uuid()),
            "available_types": [str(t) for t in dir(self._types) if not t.startswith('_')],
        }
        
        result = f"""OpenCog AtomSpace Information:
- Total atoms: {atom_count}
- AtomSpace UUID: {info['atomspace_uuid']}
- Available atom types: {len(info['available_types'])} types available

To use OpenCog operations:
- Add concept: action="add_concept", name="concept_name"
- Add fact: action="add_fact", predicate="predicate", subject="subject", object="object"  
- Query: action="query", pattern="query_pattern"
- List atoms: action="list_atoms", atom_type="ConceptNode"
"""
        return Response(message=result, break_loop=False)

    async def _add_concept(self, name="", **kwargs):
        """Add a concept node to the AtomSpace."""
        if not name:
            return Response(message="Error: 'name' parameter required for add_concept", break_loop=False)
        
        concept = self._ConceptNode(name)
        self._atomspace.add(concept)
        
        return Response(
            message=f"Added concept node: {name}",
            break_loop=False
        )

    async def _add_fact(self, predicate="", subject="", object="", **kwargs):
        """Add a fact as an evaluation link to the AtomSpace."""
        if not all([predicate, subject, object]):
            return Response(
                message="Error: 'predicate', 'subject', and 'object' parameters required for add_fact",
                break_loop=False
            )
        
        pred_node = self._PredicateNode(predicate)
        subj_node = self._ConceptNode(subject)
        obj_node = self._ConceptNode(object)
        
        fact = self._EvaluationLink(
            pred_node,
            self._ListLink(subj_node, obj_node)
        )
        
        self._atomspace.add(fact)
        
        return Response(
            message=f"Added fact: {subject} {predicate} {object}",
            break_loop=False
        )

    async def _query(self, pattern="", **kwargs):
        """Query the AtomSpace using pattern matching."""
        if not pattern:
            return Response(message="Error: 'pattern' parameter required for query", break_loop=False)
        
        # For now, do a simple name-based search
        results = []
        for atom in self._atomspace:
            atom_str = str(atom)
            if pattern.lower() in atom_str.lower():
                results.append(atom_str)
        
        if results:
            result_text = f"Query results for '{pattern}':\n" + "\n".join(results[:10])  # Limit to 10 results
            if len(results) > 10:
                result_text += f"\n... and {len(results) - 10} more results"
        else:
            result_text = f"No results found for query: {pattern}"
        
        return Response(message=result_text, break_loop=False)

    async def _list_atoms(self, atom_type="ConceptNode", limit=20, **kwargs):
        """List atoms of a specific type."""
        try:
            type_obj = getattr(self._types, atom_type)
        except AttributeError:
            return Response(
                message=f"Error: Unknown atom type '{atom_type}'",
                break_loop=False
            )
        
        atoms = self._atomspace.get_atoms_by_type(type_obj)
        
        if not atoms:
            return Response(
                message=f"No atoms of type {atom_type} found",
                break_loop=False
            )
        
        result_lines = [f"Atoms of type {atom_type}:"]
        for i, atom in enumerate(atoms[:limit]):
            result_lines.append(f"  {i+1}. {atom}")
        
        if len(atoms) > limit:
            result_lines.append(f"... and {len(atoms) - limit} more atoms")
        
        return Response(message="\n".join(result_lines), break_loop=False)

    async def _get_atom(self, name="", **kwargs):
        """Get a specific atom by name."""
        if not name:
            return Response(message="Error: 'name' parameter required for get_atom", break_loop=False)
        
        # Search for atoms with this name
        results = []
        for atom in self._atomspace:
            if hasattr(atom, 'name') and atom.name == name:
                results.append(str(atom))
        
        if results:
            result_text = f"Found atom(s) named '{name}':\n" + "\n".join(results)
        else:
            result_text = f"No atom found with name: {name}"
        
        return Response(message=result_text, break_loop=False)

    async def _count_atoms(self, atom_type=None, **kwargs):
        """Count atoms in the AtomSpace."""
        if atom_type:
            try:
                type_obj = getattr(self._types, atom_type)
                count = len(self._atomspace.get_atoms_by_type(type_obj))
                result = f"Count of {atom_type}: {count}"
            except AttributeError:
                result = f"Error: Unknown atom type '{atom_type}'"
        else:
            count = len(self._atomspace)
            result = f"Total atoms in AtomSpace: {count}"
        
        return Response(message=result, break_loop=False)

    async def _clear_atomspace(self, **kwargs):
        """Clear all atoms from the AtomSpace."""
        initial_count = len(self._atomspace)
        self._atomspace.clear()
        
        return Response(
            message=f"AtomSpace cleared. Removed {initial_count} atoms.",
            break_loop=False
        )