"""
GeoMind AI - Multi-Agent Orchestration System
Production-grade multi-agent system with specialized geological agents,
planning, memory, and autonomous research capabilities.

Agents:
- Geologist Agent (deposit evaluation, mineral analysis)
- Mining Economics Agent (financial assessment, capex/opex)
- ESG Agent (environmental, social, governance)
- Risk Assessment Agent (technical, market, regulatory risks)
- Exploration Planning Agent (drill recommendations, survey planning)
- Data Extraction Agent (coordinate, assay, metadata extraction)
"""

from typing import Optional, List, Dict, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import asyncio
import json
import logging
from datetime import datetime
import hashlib

import yaml

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

class AgentRole(Enum):
    """Agent specialized roles."""
    GEOLOGIST = "geologist"
    ECONOMIST = "economist"
    ESG_SPECIALIST = "esg_specialist"
    RISK_ANALYST = "risk_analyst"
    EXPLORATION_PLANNER = "exploration_planner"
    DATA_EXTRACTOR = "data_extractor"
    ORCHESTRATOR = "orchestrator"


class ToolType(Enum):
    """Types of tools agents can use."""
    RAG_SEARCH = "rag_search"
    CALCULATION = "calculation"
    SIMULATION = "simulation"
    VISUALIZATION = "visualization"
    DATA_ANALYSIS = "data_analysis"
    WEB_SEARCH = "web_search"
    REPORT_GENERATION = "report_generation"


@dataclass
class Tool:
    """Represents a tool an agent can use."""
    name: str
    description: str
    tool_type: ToolType
    parameters: Dict[str, Any]
    callable_func: Optional[Callable] = None
    
    async def execute(self, **kwargs) -> Any:
        """Execute the tool."""
        if self.callable_func:
            return await self.callable_func(**kwargs)
        raise NotImplementedError(f"Tool {self.name} not implemented")


@dataclass
class AgentMemory:
    """Agent memory for conversation history and context."""
    conversation_history: List[Dict[str, str]] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    short_term: List[str] = field(default_factory=list)  # Recent facts
    long_term: Dict[str, Any] = field(default_factory=dict)  # Persistent knowledge
    
    def add_message(self, role: str, content: str):
        """Add message to conversation history."""
        self.conversation_history.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
        })
    
    def add_short_term(self, fact: str):
        """Add short-term fact."""
        self.short_term.append(fact)
        # Keep only last 10 facts
        if len(self.short_term) > 10:
            self.short_term = self.short_term[-10:]
    
    def get_context_string(self) -> str:
        """Get memory as string for LLM context."""
        context = "## Agent Memory\n\n"
        
        if self.short_term:
            context += "**Recent Facts:**\n"
            for fact in self.short_term:
                context += f"- {fact}\n"
            context += "\n"
        
        if self.context:
            context += "**Context:**\n"
            context += json.dumps(self.context, indent=2)
            context += "\n"
        
        return context


@dataclass
class AgentPlan:
    """Agent's plan for solving a task."""
    objective: str
    steps: List[Dict[str, Any]]  # [{"step": 1, "action": "...", "tool": "...", "expected_output": "..."}]
    estimated_duration: float  # seconds
    tools_needed: List[str]
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict:
        return {
            "objective": self.objective,
            "steps": self.steps,
            "estimated_duration": self.estimated_duration,
            "tools_needed": self.tools_needed,
            "created_at": self.created_at,
        }


@dataclass
class AgentAction:
    """Represents an action an agent takes."""
    action_type: str
    tool_name: str
    parameters: Dict[str, Any]
    reasoning: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class AgentResponse:
    """Response from an agent."""
    content: str
    agent_name: str
    agent_role: AgentRole
    confidence: float
    sources: List[Dict[str, Any]]
    actions_taken: List[AgentAction]
    plan: Optional[AgentPlan] = None
    next_steps: Optional[List[str]] = None
    
    def to_dict(self) -> Dict:
        return {
            "content": self.content,
            "agent_name": self.agent_name,
            "agent_role": self.agent_role.value,
            "confidence": self.confidence,
            "sources": self.sources,
            "actions_taken": [
                {
                    "action_type": a.action_type,
                    "tool_name": a.tool_name,
                    "parameters": a.parameters,
                    "reasoning": a.reasoning,
                    "timestamp": a.timestamp,
                }
                for a in self.actions_taken
            ],
            "plan": self.plan.to_dict() if self.plan else None,
            "next_steps": self.next_steps,
        }


# ============================================================================
# BASE AGENT CLASS
# ============================================================================

class BaseAgent(ABC):
    """Base agent class."""
    
    def __init__(
        self,
        name: str,
        role: AgentRole,
        llm_client,
        rag_engine,
        system_prompt: str = "",
    ):
        self.name = name
        self.role = role
        self.llm = llm_client
        self.rag = rag_engine
        self.system_prompt = system_prompt
        self.memory = AgentMemory()
        self.tools: Dict[str, Tool] = {}
        self.created_at = datetime.now()
    
    def register_tool(self, tool: Tool):
        """Register a tool the agent can use."""
        self.tools[tool.name] = tool
        logger.info(f"Agent {self.name} registered tool: {tool.name}")
    
    @abstractmethod
    async def process(self, query: str, context: Optional[str] = None) -> AgentResponse:
        """Process a query and return response."""
        pass
    
    async def think_step_by_step(self, query: str) -> AgentPlan:
        """Create a step-by-step plan for solving the query."""
        prompt = f"""You are {self.name}, a {self.role.value} expert.
Create a detailed step-by-step plan to answer this query:

Query: {query}

Your available tools are:
{self._format_tools()}

Return a JSON object with:
{{
    "objective": "Clear statement of what we're solving",
    "steps": [
        {{"step": 1, "action": "...", "tool": "tool_name", "expected_output": "..."}}
    ],
    "estimated_duration": 10.0,
    "tools_needed": ["tool1", "tool2"]
}}"""
        
        try:
            response = await self.llm.agenerate(prompt)
            
            # Parse JSON response
            import json
            import re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                plan_dict = json.loads(json_match.group())
                return AgentPlan(
                    objective=plan_dict.get("objective", query),
                    steps=plan_dict.get("steps", []),
                    estimated_duration=plan_dict.get("estimated_duration", 10.0),
                    tools_needed=plan_dict.get("tools_needed", []),
                )
        except Exception as e:
            logger.error(f"Planning failed: {e}")
        
        # Fallback simple plan
        return AgentPlan(
            objective=query,
            steps=[{"step": 1, "action": "Search for information", "tool": "rag_search", "expected_output": "Relevant documents"}],
            estimated_duration=5.0,
            tools_needed=["rag_search"],
        )
    
    async def use_tool(self, tool_name: str, **kwargs) -> Any:
        """Use a registered tool."""
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not registered for {self.name}")
        
        tool = self.tools[tool_name]
        logger.info(f"Agent {self.name} using tool: {tool_name}")
        
        return await tool.execute(**kwargs)
    
    def _format_tools(self) -> str:
        """Format available tools for LLM prompt."""
        tool_list = []
        for name, tool in self.tools.items():
            tool_list.append(f"- {name}: {tool.description}")
        return "\n".join(tool_list)
    
    def _update_memory(self, role: str, content: str):
        """Update agent memory."""
        self.memory.add_message(role, content)
    
    def _hash_query(self, query: str) -> str:
        """Hash a query for caching."""
        return hashlib.md5(query.encode()).hexdigest()[:8]


# ============================================================================
# SPECIALIZED AGENTS
# ============================================================================

class GeologistAgent(BaseAgent):
    """Geological specialist agent for deposit evaluation."""
    
    def __init__(self, llm_client, rag_engine):
        super().__init__(
            name="Dr. Geologist",
            role=AgentRole.GEOLOGIST,
            llm_client=llm_client,
            rag_engine=rag_engine,
            system_prompt="""You are an expert geologist with 20+ years of mining experience.
You specialize in:
- Mineral deposit evaluation
- Geological mapping and interpretation
- Drill core logging and analysis
- Mineral system understanding

Always cite geological evidence and be precise with technical terminology."""
        )
    
    async def process(self, query: str, context: Optional[str] = None) -> AgentResponse:
        """Process geological query."""
        self._update_memory("user", query)
        
        # Create plan
        plan = await self.think_step_by_step(query)
        
        actions = []
        
        # Execute plan steps
        search_results = []
        for step in plan.steps[:3]:  # Limit to 3 steps
            if step.get("tool") == "rag_search":
                try:
                    result = await self.rag.retrieve(query, top_k=5)
                    search_results.extend(result)
                    
                    actions.append(AgentAction(
                        action_type="rag_search",
                        tool_name="rag_search",
                        parameters={"query": query, "top_k": 5},
                        reasoning=step.get("action", "Search for relevant geological data"),
                    ))
                except Exception as e:
                    logger.error(f"RAG search failed: {e}")
        
        # Generate response
        context_text = "\n".join([r.content[:300] for r in search_results]) if search_results else ""
        
        prompt = f"""{self.system_prompt}

Query: {query}

{context or ""}

Relevant geological data:
{context_text}

Provide a detailed geological analysis. Include:
1. Geological interpretation
2. Relevant evidence from the documents
3. Key mineral indicators
4. Recommended next steps for exploration"""
        
        try:
            response = await self.llm.agenerate(prompt)
        except Exception as e:
            response = f"Unable to generate response: {e}"
        
        self._update_memory("assistant", response)
        
        return AgentResponse(
            content=response,
            agent_name=self.name,
            agent_role=self.role,
            confidence=0.85,
            sources=[{"document": r.source_document, "page": r.source_page} for r in search_results],
            actions_taken=actions,
            plan=plan,
            next_steps=["Request additional geological survey", "Analyze core samples"],
        )


class EconomicsAgent(BaseAgent):
    """Mining economics specialist agent."""
    
    def __init__(self, llm_client, rag_engine):
        super().__init__(
            name="Dr. Economics",
            role=AgentRole.ECONOMIST,
            llm_client=llm_client,
            rag_engine=rag_engine,
            system_prompt="""You are a mining economist with deep expertise in:
- Project economics and NPV analysis
- Operating cost estimation (opex)
- Capital cost estimation (capex)
- Commodity price forecasting
- Market analysis

Provide rigorous financial analysis with industry benchmarks."""
        )
    
    async def process(self, query: str, context: Optional[str] = None) -> AgentResponse:
        """Process economic query."""
        self._update_memory("user", query)
        
        # Search for cost and price data
        search_results = await self.rag.retrieve(
            f"mining costs capex opex {query}",
            top_k=5
        )
        
        actions = [AgentAction(
            action_type="rag_search",
            tool_name="rag_search",
            parameters={"query": f"mining costs {query}", "top_k": 5},
            reasoning="Search for cost and economic data",
        )]
        
        prompt = f"""{self.system_prompt}

Economic Analysis Query: {query}

{context or ""}

Document data:
{chr(10).join([r.content[:200] for r in search_results])}

Provide comprehensive economic analysis including:
1. Capital requirements
2. Operating costs breakdown
3. Revenue potential
4. Project economics (NPV, IRR)
5. Sensitivity analysis
6. Market context"""
        
        try:
            response = await self.llm.agenerate(prompt)
        except Exception as e:
            response = f"Unable to generate response: {e}"
        
        self._update_memory("assistant", response)
        
        return AgentResponse(
            content=response,
            agent_name=self.name,
            agent_role=self.role,
            confidence=0.80,
            sources=[{"document": r.source_document} for r in search_results],
            actions_taken=actions,
            next_steps=["Update commodity price assumptions", "Refine cost estimates"],
        )


class RiskAssessmentAgent(BaseAgent):
    """Risk analysis specialist agent."""
    
    def __init__(self, llm_client, rag_engine):
        super().__init__(
            name="Dr. Risk",
            role=AgentRole.RISK_ANALYST,
            llm_client=llm_client,
            rag_engine=rag_engine,
            system_prompt="""You are a mining risk analyst specializing in:
- Technical risk assessment
- Market and price risk
- Regulatory and permitting risk
- Environmental and social risk
- Operational risk

Identify, quantify, and prioritize risks with mitigation strategies."""
        )
    
    async def process(self, query: str, context: Optional[str] = None) -> AgentResponse:
        """Process risk query."""
        self._update_memory("user", query)
        
        # Search for risk-related data
        search_results = await self.rag.retrieve(
            f"risk assessment challenges {query}",
            top_k=5
        )
        
        prompt = f"""{self.system_prompt}

Risk Analysis Query: {query}

{context or ""}

Document data:
{chr(10).join([r.content[:200] for r in search_results])}

Provide comprehensive risk assessment:
1. Identify key risks
2. Rate risk severity (high/medium/low)
3. Probability assessment
4. Potential impact
5. Mitigation strategies
6. Residual risk after mitigation"""
        
        try:
            response = await self.llm.agenerate(prompt)
        except Exception as e:
            response = f"Unable to generate response: {e}"
        
        self._update_memory("assistant", response)
        
        return AgentResponse(
            content=response,
            agent_name=self.name,
            agent_role=self.role,
            confidence=0.82,
            sources=[{"document": r.source_document} for r in search_results],
            actions_taken=[],
            next_steps=["Develop risk register", "Create mitigation plan"],
        )


# ============================================================================
# MULTI-AGENT ORCHESTRATOR
# ============================================================================

class MultiAgentOrchestrator:
    """Orchestrate multiple specialized agents."""
    
    def __init__(self, llm_client, rag_engine):
        self.llm = llm_client
        self.rag = rag_engine
        self.agents: Dict[str, BaseAgent] = {}
        self.execution_history: List[Dict] = []
        self.planning_agent = None
        
        # Initialize agents
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize all specialized agents."""
        self.agents["geologist"] = GeologistAgent(self.llm, self.rag)
        self.agents["economist"] = EconomicsAgent(self.llm, self.rag)
        self.agents["risk"] = RiskAssessmentAgent(self.llm, self.rag)
        
        logger.info(f"Initialized {len(self.agents)} agents")
    
    async def route_query(self, query: str) -> str:
        """Determine which agent(s) should handle the query."""
        classification_prompt = f"""Classify this exploration query and determine which agents should analyze it.

Query: "{query}"

Available agents:
- geologist: For geological analysis, deposit evaluation, mineral systems
- economist: For financial analysis, costs, project economics
- risk: For risk assessment, challenges, regulatory issues

Return JSON:
{{"primary_agent": "agent_name", "secondary_agents": ["agent1", "agent2"], "confidence": 0.9}}"""
        
        try:
            response = await self.llm.agenerate(classification_prompt)
            import json, re
            json_match = re.search(r'\{.*\}', response, re.DOTALL)
            if json_match:
                routing = json.loads(json_match.group())
                return routing.get("primary_agent", "geologist")
        except Exception as e:
            logger.error(f"Routing failed: {e}")
        
        return "geologist"  # Default
    
    async def process_query(
        self,
        query: str,
        enable_planning: bool = True,
        multi_agent: bool = False,
    ) -> Dict[str, Any]:
        """Process query using agents."""
        
        logger.info(f"Processing query: {query[:100]}...")
        
        # Route to appropriate agent(s)
        primary_agent_name = await self.route_query(query)
        primary_agent = self.agents.get(primary_agent_name, self.agents["geologist"])
        
        # Get response from primary agent
        primary_response = await primary_agent.process(query)
        
        responses = [primary_response.to_dict()]
        
        # Get secondary agent responses if enabled
        if multi_agent:
            secondary_agents = [name for name in self.agents.keys() if name != primary_agent_name]
            
            for agent_name in secondary_agents[:2]:  # Limit to 2 secondary agents
                agent = self.agents[agent_name]
                try:
                    secondary_response = await agent.process(query)
                    responses.append(secondary_response.to_dict())
                except Exception as e:
                    logger.error(f"Secondary agent {agent_name} failed: {e}")
        
        # Record execution
        execution_record = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "primary_agent": primary_agent_name,
            "responses": responses,
        }
        self.execution_history.append(execution_record)
        
        return {
            "query": query,
            "primary_agent": primary_agent_name,
            "responses": responses,
            "execution_timestamp": datetime.now().isoformat(),
        }
    
    async def autonomous_research(
        self,
        topic: str,
        max_iterations: int = 5,
    ) -> Dict[str, Any]:
        """Run autonomous research mode."""
        
        logger.info(f"Starting autonomous research on: {topic}")
        
        research_log = []
        
        for iteration in range(max_iterations):
            # Generate research question
            question_prompt = f"""Based on this topic and previous research:

Topic: {topic}

Previous research:
{chr(10).join([f"- {log['question']}" for log in research_log[-3:]])}

Generate the next specific research question to explore this topic further.
Return only the question."""
            
            try:
                next_question = await self.llm.agenerate(question_prompt)
            except Exception as e:
                logger.error(f"Question generation failed: {e}")
                break
            
            # Process question
            response = await self.process_query(next_question, multi_agent=True)
            
            research_log.append({
                "iteration": iteration + 1,
                "question": next_question,
                "response": response,
            })
            
            logger.info(f"Iteration {iteration + 1}: {next_question[:80]}...")
            
            # Check if we've covered the topic sufficiently
            if iteration >= 2:
                completion_prompt = f"""Based on this research log about "{topic}", 
have we sufficiently explored the topic? Answer yes or no.

Research:
{chr(10).join([log['question'] for log in research_log[-3:]])}"""
                
                completion_check = await self.llm.agenerate(completion_prompt)
                if "yes" in completion_check.lower():
                    break
        
        return {
            "topic": topic,
            "iterations": len(research_log),
            "research_log": research_log,
        }
    
    def get_execution_history(self) -> List[Dict]:
        """Get execution history."""
        return self.execution_history


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

async def main():
    """Example usage."""
    
    class DummyLLM:
        async def agenerate(self, prompt: str) -> str:
            return "Generated response based on geological expertise."
    
    class DummyRAG:
        async def retrieve(self, query: str, top_k: int = 5) -> List:
            return []
    
    llm = DummyLLM()
    rag = DummyRAG()
    
    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator(llm, rag)
    
    # Process a query
    result = await orchestrator.process_query(
        "What are the nickel and copper grades at Sumayau?",
        multi_agent=True
    )
    
    print(json.dumps(result, indent=2, default=str))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
