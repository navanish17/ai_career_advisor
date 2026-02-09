"""
Career Counselor Agent using LangGraph
Stateful, multi-turn conversation agent with tool calling
"""
from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from sqlalchemy.ext.asyncio import AsyncSession
from ai_career_advisor.core.logger import logger
from ai_career_advisor.core.config import settings
from ai_career_advisor.core.model_manager import ModelManager
import operator


class AgentState(TypedDict):
    """State schema for the agent graph"""
    messages: Annotated[List[BaseMessage], operator.add]
    user_email: str
    session_id: str
    intent: str
    language: str  # "en" or "hi"
    model_preference: str  # "auto", "sonar-pro", "gemini-..."
    tool_outputs: Dict[str, Any]
    db: Any  # Database session


class CareerAgent:
    """
    LangGraph-based Career Counselor Agent
    """
    
    def __init__(self, db: AsyncSession = None):
        self.db = db
        # LLM initialization moved to ModelManager
        self.graph = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Build the agent graph"""
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("intent_detection", self.intent_node)
        workflow.add_node("greeting", self.greeting_node)
        workflow.add_node("rejection", self.rejection_node)
        workflow.add_node("tool_selection", self.tool_selection_node)
        workflow.add_node("synthesis", self.synthesis_node)
        
        # Add edges
        workflow.add_edge(START, "intent_detection")
        workflow.add_conditional_edges(
            "intent_detection",
            self.router,
            {
                "greeting": "greeting",
                "rejected": "rejection",
                "career_query": "tool_selection",
                "roadmap_request": "tool_selection",
                "default": "tool_selection"  # Fallback for any other intent
            }
        )
        workflow.add_edge("greeting", END)
        workflow.add_edge("rejection", END)
        workflow.add_edge("tool_selection", "synthesis")
        workflow.add_edge("synthesis", END)
        
        return workflow.compile()
    
    async def intent_node(self, state: AgentState) -> AgentState:
        """Classify user intent using existing DistilBERT classifier"""
        try:
            from ai_career_advisor.services.intentfilter import IntentFilter
            
            last_message = state["messages"][-1].content
            intent_result = IntentFilter.is_career_related(last_message)
            
            # Determine intent
            if intent_result.get("is_greeting"):
                state["intent"] = "greeting"
            elif not intent_result["is_career"]:
                state["intent"] = "rejected"
            else:
                # Check for roadmap keywords
                query_lower = last_message.lower()
                roadmap_keywords = [
                    "want to become", "how to become", "kaise bane",
                    "roadmap", "path to become", "steps to become"
                ]
                if any(kw in query_lower for kw in roadmap_keywords):
                    state["intent"] = "roadmap_request"
                else:
                    state["intent"] = intent_result.get("intent", "career_query")
            
            logger.info(f"Intent detected: {state['intent']}")
            return state
            
        except Exception as e:
            logger.error(f"Intent detection error: {e}")
            state["intent"] = "career_query"  # Default fallback
            return state
    
    def router(self, state: AgentState) -> str:
        """Route to appropriate node based on intent"""
        intent = state.get("intent", "default")
        
        # Return the intent as-is since our conditional edges use intent names as keys
        valid_intents = ["greeting", "rejected", "career_query", "roadmap_request"]
        
        if intent in valid_intents:
            return intent
        else:
            return "default"  # Fallback
    
    async def greeting_node(self, state: AgentState) -> AgentState:
        """Handle greetings"""
        if state["language"] == "hi":
            response = """👋 **Namaste! Main aapka AI Career Counselor hoon!**

Main Indian students ko education aur career guidance deta hoon. 🎓

**Aap mujhse puch sakte ho:**
- 💼 Career options (Engineering, Medical, Commerce, Arts)
- 🏫 College selection (IITs, NITs, Private colleges)
- 📝 Entrance exams (JEE, NEET, CUET, CAT, GATE)
- 💰 Fees, placements, salaries
- 📚 Study tips aur career roadmaps

Apna question poocho! 😊"""
        else:
            response = """👋 **Hello! I'm your AI Career Counselor!**

I help Indian students with education and career guidance. 🎓

**You can ask me about:**
- 💼 Career options (Engineering, Medical, Commerce, Arts)
- 🏫 College selection (IITs, NITs, Private colleges)
- 📝 Entrance exams (JEE, NEET, CUET, CAT, GATE)
- 💰 Fees, placements, and salaries
- 📚 Study tips and career roadmaps

Ask me your question! 😊"""
        
        state["messages"].append(AIMessage(content=response))
        return state
    
    async def rejection_node(self, state: AgentState) -> AgentState:
        """Handle non-career queries"""
        if state["language"] == "hi":
            response = """🎓 Main ek **AI Career Counselor** hoon for Indian students!

Main sirf **education aur career** related questions answer karta hoon:
- ✅ Career guidance (after 10th/12th)
- ✅ College selection (IITs, NITs, top colleges)
- ✅ Entrance exams (JEE, NEET, CUET)
- ✅ Career roadmaps (Software Engineer, Doctor, CA)
- ✅ Salary & job prospects

Koi career ya education-related question poocho! 😊"""
        else:
            response = """🎓 I'm an **AI Career Counselor** for Indian students!

I only answer **education and career** related questions:
- ✅ Career guidance (after 10th/12th)
- ✅ College selection (IITs, NITs, top colleges)
- ✅ Entrance exams (JEE, NEET, CUET)
- ✅ Career roadmaps (Software Engineer, Doctor, CA)
- ✅ Salary & job prospects

Please ask a career or education-related question! 😊"""
        
        state["messages"].append(AIMessage(content=response))
        return state
    
    async def tool_selection_node(self, state: AgentState) -> AgentState:
        """Select and execute appropriate tools"""
        intent = state["intent"]
        user_query = state["messages"][-1].content
        
        tool_outputs = {}
        
        try:
            # For roadmap requests
            if intent == "roadmap_request":
                career_name = self._extract_career(user_query)
                if career_name and self.db:
                    from ai_career_advisor.services.backward_roadmap_service import BackwardRoadmapService
                    roadmap = await BackwardRoadmapService.get_by_career(
                        db=self.db,
                        career_name=career_name
                    )
                    if roadmap:
                        tool_outputs["roadmap"] = {
                            "career": roadmap.normalized_career,
                            "description": roadmap.career_description,
                            "exams": roadmap.entrance_exams[:3] if roadmap.entrance_exams else [],
                            "colleges": roadmap.top_colleges[:3] if roadmap.top_colleges else []
                        }
            
            # For general career queries, try RAG first
            from ai_career_advisor.RAG.retriever import retriever
            rag_result = await retriever.search_and_build_context(user_query, top_k=5)
            
            if rag_result["found"]:
                tool_outputs["rag"] = {
                    "context": rag_result["context"],
                    "sources": rag_result.get("sources", [])
                }
            else:
                # Fallback to web search
                tool_outputs["web_search_needed"] = True
                
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            tool_outputs["error"] = str(e)
        
        state["tool_outputs"] = tool_outputs
        return state
    
    async def synthesis_node(self, state: AgentState) -> AgentState:
        """Synthesize final response using LLM"""
        user_query = state["messages"][-1].content
        tool_outputs = state.get("tool_outputs", {})
        language = state["language"]
        
        # Build context from tool outputs
        context_parts = []
        
        if "roadmap" in tool_outputs:
            roadmap = tool_outputs["roadmap"]
            context_parts.append(f"Career: {roadmap['career']}")
            context_parts.append(f"Description: {roadmap['description']}")
            if roadmap.get("exams"):
                context_parts.append(f"Key Exams: {', '.join(roadmap['exams'])}")
            if roadmap.get("colleges"):
                context_parts.append(f"Top Colleges: {', '.join(roadmap['colleges'])}")
        
        if "rag" in tool_outputs:
            context_parts.append(f"Knowledge Base: {tool_outputs['rag']['context']}")
        
        context = "\n\n".join(context_parts) if context_parts else "No specific data available."
        
        # Create system prompt
        lang_instruction = "Answer in Hindi/Hinglish." if language == "hi" else "Answer in English only."
        
        system_prompt = f"""You are an AI Career Counselor for Indian students.

CONTEXT:
{context}

INSTRUCTIONS:
- {lang_instruction}
- Be concise (under 200 words)
- Use the context provided
- If context is insufficient, say so
- Be encouraging and helpful
- Use these links for features:
  * College Finder: [College Finder](/college-finder)
  * Career Roadmap: [Career Roadmap](/roadmap/backward)
  * Stream Finder: [Stream Finder](/stream-finder)"""

        try:
            # Combine system and user prompt for ModelManager
            full_prompt = f"{system_prompt}\n\nUser Query: {user_query}"
            
            # Use ModelManager with preference
            model_pref = state.get("model_preference", "auto")
            response_text = await ModelManager.generate(full_prompt, preference=model_pref)
            
            state["messages"].append(AIMessage(content=response_text))
            
        except Exception as e:
            logger.error(f"LLM synthesis error: {e}")
            fallback = f"I cannot generate a response right now. Error: {str(e)}"
            state["messages"].append(AIMessage(content=fallback))
        
        return state
    
    def _extract_career(self, query: str) -> str:
        """Extract career name from query"""
        import re
        query_lower = query.lower().strip()
        
        patterns = [
            r"(?:i want to become|become|be) (?:a |an )?(.+?)(?:\?|$|\.)",
            r"(?:how to become|kaise bane|kaise banu) (?:a |an )?(.+?)(?:\?|$|\.)",
            r"roadmap (?:for|to become) (?:a |an )?(.+?)(?:\?|$|\.)",
        ]
        
        for pattern in patterns:
            match = re.search(pattern, query_lower)
            if match:
                career = match.group(1).strip()
                return career.title()
        
        return None
    
    async def run(self, query: str, user_email: str, session_id: str, language: str = "en", model_preference: str = "auto") -> Dict[str, Any]:
        """Run the agent graph"""
        initial_state = {
            "messages": [HumanMessage(content=query)],
            "user_email": user_email,
            "session_id": session_id,
            "intent": "",
            "language": language,
            "model_preference": model_preference,
            "tool_outputs": {},
            "db": self.db
        }
        
        try:
            final_state = await self.graph.ainvoke(initial_state)
            
            # Extract response
            response_message = final_state["messages"][-1]
            
            return {
                "success": True,
                "response": response_message.content,
                "intent": final_state.get("intent", "unknown"),
                "tool_outputs": final_state.get("tool_outputs", {})
            }
            
        except Exception as e:
            logger.error(f"Agent execution error: {e}")
            return {
                "success": False,
                "response": "I apologize, but I encountered an error. Please try again.",
                "error": str(e)
            }
