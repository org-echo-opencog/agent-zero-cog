from python.helpers.tool import Tool, Response
from python.helpers.print_style import PrintStyle
import json

class OpenCogReasoning(Tool):
    """
    Tool for performing logical reasoning using OpenCog's reasoning engines.
    
    This tool provides access to OpenCog's reasoning capabilities including:
    - Forward chaining reasoning
    - Backward chaining reasoning  
    - Pattern matching and unification
    - Probabilistic reasoning
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._atomspace = None
        self._reasoning_engine = None
        self._initialize_reasoning()

    def _initialize_reasoning(self):
        """Initialize OpenCog reasoning components."""
        try:
            from opencog.atomspace import AtomSpace, types
            from opencog.type_constructors import (
                ConceptNode, PredicateNode, VariableNode,
                EvaluationLink, InheritanceLink, ImplicationLink, 
                AndLink, OrLink, NotLink, ListLink
            )
            
            # Try to import reasoning components
            try:
                from opencog.pln import PLNReasoner
                self._pln_available = True
            except ImportError:
                self._pln_available = False
                PrintStyle.warning("PLN (Probabilistic Logic Networks) not available")
            
            # Get or create atomspace (share with opencog_atomspace tool if it exists)
            self._atomspace = AtomSpace()
            from opencog.type_constructors import set_default_atomspace
            set_default_atomspace(self._atomspace)
            
            # Store constructors for easy access
            self._types = types
            self._ConceptNode = ConceptNode
            self._PredicateNode = PredicateNode
            self._VariableNode = VariableNode
            self._EvaluationLink = EvaluationLink
            self._InheritanceLink = InheritanceLink
            self._ImplicationLink = ImplicationLink
            self._AndLink = AndLink
            self._OrLink = OrLink
            self._NotLink = NotLink
            self._ListLink = ListLink
            
        except ImportError as e:
            PrintStyle.error(f"OpenCog reasoning not available: {e}")
            self._atomspace = None

    async def execute(self, action="info", **kwargs):
        """
        Execute OpenCog reasoning operations.
        
        Actions:
        - info: Get information about reasoning capabilities
        - add_rule: Add an inference rule
        - add_inheritance: Add inheritance relationship
        - add_implication: Add implication rule
        - forward_chain: Perform forward chaining inference
        - backward_chain: Perform backward chaining inference
        - pattern_match: Perform pattern matching
        - infer: General inference on a query
        """
        
        if not self._atomspace:
            return Response(
                message="OpenCog reasoning is not available. Please install OpenCog with reasoning components.",
                break_loop=False
            )

        try:
            if action == "info":
                return await self._get_reasoning_info()
            elif action == "add_rule":
                return await self._add_rule(**kwargs)
            elif action == "add_inheritance":
                return await self._add_inheritance(**kwargs)
            elif action == "add_implication":
                return await self._add_implication(**kwargs)
            elif action == "forward_chain":
                return await self._forward_chain(**kwargs)
            elif action == "backward_chain":
                return await self._backward_chain(**kwargs)
            elif action == "pattern_match":
                return await self._pattern_match(**kwargs)
            elif action == "infer":
                return await self._infer(**kwargs)
            else:
                available_actions = ["info", "add_rule", "add_inheritance", "add_implication", 
                                   "forward_chain", "backward_chain", "pattern_match", "infer"]
                return Response(
                    message=f"Unknown action '{action}'. Available actions: {', '.join(available_actions)}",
                    break_loop=False
                )
                
        except Exception as e:
            PrintStyle.error(f"OpenCog reasoning operation failed: {e}")
            return Response(
                message=f"Reasoning operation failed: {str(e)}",
                break_loop=False
            )

    async def _get_reasoning_info(self):
        """Get information about reasoning capabilities."""
        atom_count = len(self._atomspace)
        
        # Count different types of reasoning-related atoms
        concept_count = len(self._atomspace.get_atoms_by_type(self._types.ConceptNode))
        inheritance_count = len(self._atomspace.get_atoms_by_type(self._types.InheritanceLink))
        implication_count = len(self._atomspace.get_atoms_by_type(self._types.ImplicationLink))
        
        info = f"""OpenCog Reasoning Engine Information:
- Total atoms in AtomSpace: {atom_count}
- Concept nodes: {concept_count}
- Inheritance relationships: {inheritance_count}
- Implication rules: {implication_count}
- PLN (Probabilistic Logic Networks): {'Available' if self._pln_available else 'Not available'}

Available reasoning operations:
- Add inheritance: action="add_inheritance", parent="parent_concept", child="child_concept"
- Add implication: action="add_implication", antecedent="condition", consequent="result"
- Forward chaining: action="forward_chain", premises=["premise1", "premise2"]
- Pattern matching: action="pattern_match", pattern="pattern_to_match"
- General inference: action="infer", query="what_to_infer"
"""
        return Response(message=info, break_loop=False)

    async def _add_rule(self, rule_type="implication", **kwargs):
        """Add a general reasoning rule."""
        if rule_type == "implication":
            return await self._add_implication(**kwargs)
        elif rule_type == "inheritance":
            return await self._add_inheritance(**kwargs)
        else:
            return Response(
                message=f"Unknown rule type '{rule_type}'. Use 'implication' or 'inheritance'.",
                break_loop=False
            )

    async def _add_inheritance(self, parent="", child="", **kwargs):
        """Add an inheritance relationship between concepts."""
        if not all([parent, child]):
            return Response(
                message="Error: Both 'parent' and 'child' parameters required for inheritance",
                break_loop=False
            )
        
        parent_node = self._ConceptNode(parent)
        child_node = self._ConceptNode(child)
        
        inheritance = self._InheritanceLink(child_node, parent_node)
        self._atomspace.add(inheritance)
        
        return Response(
            message=f"Added inheritance: {child} inherits from {parent}",
            break_loop=False
        )

    async def _add_implication(self, antecedent="", consequent="", **kwargs):
        """Add an implication rule."""
        if not all([antecedent, consequent]):
            return Response(
                message="Error: Both 'antecedent' and 'consequent' parameters required for implication",
                break_loop=False
            )
        
        # Create concept nodes for the antecedent and consequent
        ant_node = self._ConceptNode(antecedent)
        cons_node = self._ConceptNode(consequent)
        
        # Create implication link
        implication = self._ImplicationLink(ant_node, cons_node)
        self._atomspace.add(implication)
        
        return Response(
            message=f"Added implication: {antecedent} → {consequent}",
            break_loop=False
        )

    async def _forward_chain(self, premises=None, max_steps=10, **kwargs):
        """Perform forward chaining inference from given premises."""
        if not premises:
            premises = []
        
        if not isinstance(premises, list):
            premises = [premises]
        
        # Add premises to atomspace if not already present
        premise_atoms = []
        for premise in premises:
            premise_atom = self._ConceptNode(premise)
            self._atomspace.add(premise_atom)
            premise_atoms.append(premise_atom)
        
        # Simple forward chaining: look for implications that can be triggered
        implications = self._atomspace.get_atoms_by_type(self._types.ImplicationLink)
        inferred_facts = []
        
        for step in range(max_steps):
            new_inferences = []
            
            for impl in implications:
                if len(impl.out) >= 2:
                    antecedent = impl.out[0]
                    consequent = impl.out[1]
                    
                    # Check if antecedent matches any of our current facts
                    current_facts = premise_atoms + [self._ConceptNode(fact) for fact in inferred_facts]
                    
                    for fact in current_facts:
                        if str(antecedent) == str(fact) and str(consequent) not in [str(f) for f in current_facts]:
                            new_inferences.append(str(consequent))
                            break
            
            if not new_inferences:
                break
                
            inferred_facts.extend(new_inferences)
        
        result = f"Forward chaining from premises: {premises}\n"
        if inferred_facts:
            result += f"Inferred facts: {inferred_facts}"
        else:
            result += "No new facts could be inferred."
        
        return Response(message=result, break_loop=False)

    async def _backward_chain(self, goal="", max_depth=5, **kwargs):
        """Perform backward chaining to prove a goal."""
        if not goal:
            return Response(
                message="Error: 'goal' parameter required for backward chaining",
                break_loop=False
            )
        
        goal_atom = self._ConceptNode(goal)
        
        # Simple backward chaining: look for rules that could prove the goal
        implications = self._atomspace.get_atoms_by_type(self._types.ImplicationLink)
        proof_steps = []
        
        def find_proofs(target, depth=0):
            if depth >= max_depth:
                return []
            
            proofs = []
            
            # Check if target is directly provable by any implication
            for impl in implications:
                if len(impl.out) >= 2:
                    antecedent = impl.out[0] 
                    consequent = impl.out[1]
                    
                    if str(consequent) == str(target):
                        # Found a rule that proves our target
                        # Now try to prove the antecedent
                        sub_proofs = find_proofs(antecedent, depth + 1)
                        if sub_proofs or str(antecedent) in [str(atom) for atom in self._atomspace.get_atoms_by_type(self._types.ConceptNode)]:
                            proofs.append(f"To prove {target}, need to prove {antecedent}")
                        
            return proofs
        
        proof_steps = find_proofs(goal_atom)
        
        result = f"Backward chaining to prove: {goal}\n"
        if proof_steps:
            result += "Proof steps:\n" + "\n".join(proof_steps)
        else:
            result += f"Could not find a proof for: {goal}"
        
        return Response(message=result, break_loop=False)

    async def _pattern_match(self, pattern="", **kwargs):
        """Perform pattern matching in the AtomSpace."""
        if not pattern:
            return Response(
                message="Error: 'pattern' parameter required for pattern matching",
                break_loop=False
            )
        
        # Simple pattern matching - find atoms that match the pattern string
        matches = []
        for atom in self._atomspace:
            atom_str = str(atom)
            if pattern.lower() in atom_str.lower():
                matches.append(atom_str)
        
        result = f"Pattern matches for '{pattern}':\n"
        if matches:
            result += "\n".join(matches[:10])  # Limit to 10 matches
            if len(matches) > 10:
                result += f"\n... and {len(matches) - 10} more matches"
        else:
            result += "No matches found"
        
        return Response(message=result, break_loop=False)

    async def _infer(self, query="", method="forward", **kwargs):
        """Perform general inference on a query."""
        if not query:
            return Response(
                message="Error: 'query' parameter required for inference",
                break_loop=False
            )
        
        if method == "forward":
            return await self._forward_chain(premises=[query], **kwargs)
        elif method == "backward":
            return await self._backward_chain(goal=query, **kwargs)
        elif method == "pattern":
            return await self._pattern_match(pattern=query, **kwargs)
        else:
            return Response(
                message=f"Unknown inference method '{method}'. Use 'forward', 'backward', or 'pattern'.",
                break_loop=False
            )