from typing import TypedDict, Annotated, Literal
from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
import operator
from .rag import RAGPipeline
from .tools import SERPTool
from .llm import get_llm

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    query: str
    route: Literal["rag","serp","both","unknown"]
    rag_context: str
    serp_results: str
    final_answer: str

def route_query(state):
    llm = get_llm()
    prompt = f"""Classify this query into one word: rag | serp | both | unknown
- rag: questions about Debales AI company/product/features
- serp: external/general knowledge questions
- both: mix of Debales and external info
- unknown: unclear queries

Query: {state["query"]}
Reply with ONE word only:"""
    response = llm.invoke([HumanMessage(content=prompt)])
    route = response.content.strip().lower()
    if route not in ("rag","serp","both","unknown"):
        route = "serp"
    print(f"  [Router] → {route}")
    return {**state, "route": route}

def retrieve_rag(state):
    context = RAGPipeline().retrieve(state["query"])
    print(f"  [RAG] Retrieved {len(context)} chars")
    return {**state, "rag_context": context}

def search_serp(state):
    results = SERPTool().search(state["query"])
    print(f"  [SERP] Retrieved {len(results)} chars")
    return {**state, "serp_results": results}

def generate_answer(state):
    llm = get_llm()
    parts = []
    if state.get("rag_context"):
        parts.append(f"[Debales AI Knowledge]\n{state['rag_context']}")
    if state.get("serp_results"):
        parts.append(f"[Web Search]\n{state['serp_results']}")
    context = "\n\n".join(parts)
    prompt = f"""You are the Debales AI assistant. Answer using the context below.
Be accurate and helpful. If context is insufficient, say so honestly.

{"Context:\n" + context if context else "No context available."}

Question: {state["query"]}
Answer:"""
    response = llm.invoke([HumanMessage(content=prompt)])
    answer = response.content.strip()
    return {**state, "final_answer": answer, "messages": [AIMessage(content=answer)]}

def decide_retrieval(state):
    route = state["route"]
    if route == "rag": return ["retrieve_rag"]
    if route == "serp": return ["search_serp"]
    if route == "both": return ["retrieve_rag","search_serp"]
    return ["generate_answer"]

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("route_query", route_query)
    graph.add_node("retrieve_rag", retrieve_rag)
    graph.add_node("search_serp", search_serp)
    graph.add_node("generate_answer", generate_answer)
    graph.set_entry_point("route_query")
    graph.add_conditional_edges("route_query", decide_retrieval,
        {"retrieve_rag":"retrieve_rag","search_serp":"search_serp","generate_answer":"generate_answer"})
    graph.add_edge("retrieve_rag","generate_answer")
    graph.add_edge("search_serp","generate_answer")
    graph.add_edge("generate_answer", END)
    return graph.compile()

def run_agent(query, history=None):
    app = build_graph()
    result = app.invoke({"messages": history or [], "query": query, "route": "unknown", "rag_context": "", "serp_results": "", "final_answer": ""})
    return result["final_answer"]
