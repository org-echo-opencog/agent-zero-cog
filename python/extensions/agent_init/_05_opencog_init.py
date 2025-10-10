from python.helpers.extension import Extension
from python.helpers.print_style import PrintStyle

class OpenCogInit(Extension):
    """
    Initialize OpenCog integration for the agent.
    
    This extension sets up the OpenCog AtomSpace and basic knowledge structures
    when an agent is initialized, providing cognitive capabilities through OpenCog.
    """
    
    async def execute(self, **kwargs):
        try:
            # Check if OpenCog integration is enabled in settings
            from python.helpers.settings import get_settings
            settings = get_settings()
            
            if not settings.get("opencog_enabled", True):
                return  # OpenCog integration disabled in settings
            
            # Check if OpenCog is available
            try:
                from opencog.atomspace import AtomSpace
                from opencog.type_constructors import ConceptNode, set_default_atomspace
                
                # Create agent-specific data for OpenCog if it doesn't exist
                if not hasattr(self.agent, 'opencog_data'):
                    self.agent.opencog_data = {}
                
                # Initialize AtomSpace for this agent if not already done
                if 'atomspace' not in self.agent.opencog_data:
                    atomspace = AtomSpace()
                    set_default_atomspace(atomspace)
                    self.agent.opencog_data['atomspace'] = atomspace
                    
                    # Add some basic knowledge about the agent
                    agent_concept = ConceptNode(f"Agent_{self.agent.number}")
                    self.agent.opencog_data['agent_concept'] = agent_concept
                    
                    PrintStyle(font_color="green").print(f"OpenCog AtomSpace initialized for {self.agent.agent_name}")
                    
                    # Add basic facts about the agent
                    from opencog.type_constructors import PredicateNode, EvaluationLink, ListLink
                    
                    # Agent type
                    agent_type_pred = PredicateNode("agent_type")
                    agent_type_fact = EvaluationLink(
                        agent_type_pred,
                        ListLink(agent_concept, ConceptNode("AI_Agent"))
                    )
                    atomspace.add(agent_type_fact)
                    
                    # Agent capabilities
                    capability_pred = PredicateNode("has_capability") 
                    capabilities = ["reasoning", "learning", "problem_solving", "tool_usage"]
                    
                    for capability in capabilities:
                        capability_fact = EvaluationLink(
                            capability_pred,
                            ListLink(agent_concept, ConceptNode(capability))
                        )
                        atomspace.add(capability_fact)
                    
                    PrintStyle(font_color="cyan").print(f"Added basic OpenCog knowledge for {self.agent.agent_name}")
                    
                    # Load default domain knowledge if configured
                    default_domain = settings.get("opencog_default_domain", "")
                    if default_domain:
                        try:
                            from python.tools.opencog_knowledge import OpenCogKnowledge
                            # Create a temporary tool instance to load domain knowledge
                            knowledge_tool = OpenCogKnowledge(
                                agent=self.agent,
                                name="opencog_knowledge",
                                method=None,
                                args={},
                                message="init",
                                loop_data=None
                            )
                            await knowledge_tool.execute(action="load_domain", domain=default_domain)
                            PrintStyle(font_color="cyan").print(f"Loaded {default_domain} domain knowledge for {self.agent.agent_name}")
                        except Exception as domain_error:
                            PrintStyle.warning(f"Failed to load domain knowledge '{default_domain}': {domain_error}")
                
            except ImportError:
                PrintStyle.warning("OpenCog not available - skipping initialization")
                PrintStyle.info("To enable OpenCog integration, install: pip install opencog")
                
        except Exception as e:
            PrintStyle.error(f"Failed to initialize OpenCog: {e}")