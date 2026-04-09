import os
from dotenv import load_dotenv
from typing import TypedDict
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from pydantic import BaseModel

load_dotenv()

# 1. DEFINE THE STATE
# This is the shared memory object passed between our nodes (Agents).
# Think of it like a Redux store or a Context object.
class GraphState(TypedDict):
    topic: str
    rough_notes: str
    final_email: str

# 2. DEFINE OUR LLM
# We use LangChain's wrapper around OpenAI for easier integration
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)

# 3. DEFINE NODE 1: THE RESEARCHER
# This agent's ONLY job is to brainstorm and take messy notes.
def researcher_agent(state: GraphState):
    print("\n[Node 1] 🕵️‍♂️ Researcher Agent is analyzing the topic...")
    topic = state["topic"]
    
    prompt = f"You are a brainstorming assistant. Write 3 quick, messy bullet points of ideas about: {topic}"
    response = llm.invoke(prompt)
    
    # Update the state with the new information
    return {"rough_notes": response.content}

# 4. DEFINE NODE 2: THE WRITER
# This agent's ONLY job is to take notes and write a clean email.
def writer_agent(state: GraphState):
    print("\n[Node 2] ✍️ Writer Agent is formatting the notes into an email...")
    notes = state["rough_notes"]
    
    prompt = f"You are a professional copywriter. Turn these messy notes into a short, punchy 3-sentence email:\n{notes}"
    response = llm.invoke(prompt)
    
    # Update the state with the final product
    return {"final_email": response.content}

# 5. BUILD THE GRAPH (The State Machine)
def build_graph():
    print("\n⚙️ Assembling the LangGraph State Machine...")
    
    # Initialize the graph with our State schema
    workflow = StateGraph(GraphState)

    # Add our agent functions as nodes
    workflow.add_node("researcher", researcher_agent)
    workflow.add_node("writer", writer_agent)

    # Define the flow (Edges)
    # START -> Researcher -> Writer -> END
    workflow.set_entry_point("researcher")
    workflow.add_edge("researcher", "writer")
    workflow.add_edge("writer", END)

    # Compile it into an executable application
    return workflow.compile()

if __name__ == "__main__":
    # Compile the graph
    app = build_graph()
    
    # The initial input data
    initial_state = {
        "topic": "Why software engineers should wake up 1 hour earlier to build micro-SaaS",
        "rough_notes": "",
        "final_email": ""
    }
    
    # Execute the graph!
    print(f"\n🚀 Executing Graph with topic: '{initial_state['topic']}'")
    
    # app.invoke runs the state machine from START to END
    final_state = app.invoke(initial_state)
    
    print("\n" + "="*50)
    print("✅ FINAL STATE OUTPUT:")
    print("="*50)
    print(final_state["final_email"])
    print("="*50 + "\n")