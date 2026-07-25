import asyncio
import json
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from langchain_core.messages import HumanMessage
from langgraph_orchestrator.workflow import app as workflow_app
from api.contracts import ChatRequest

app = FastAPI(title="Pramiti OS API Bridge")

# Allow Next.js frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def stream_langgraph_response(message: str):
    """
    Streams updates from the LangGraph workflow back to the client as SSE.
    """
    inputs = {"messages": [HumanMessage(content=message)]}
    config = {"configurable": {"thread_id": "api-thread-1"}}
    
    try:
        # Use astream with stream_mode="updates" to get state changes per node
        async for event in workflow_app.astream(inputs, config, stream_mode="updates"):
            for node, state in event.items():
                if "messages" in state and len(state["messages"]) > 0:
                    last_message = state["messages"][-1]
                    
                    requires_approval = state.get("requires_approval", False)
                    
                    payload = {
                        "node": node,
                        "content": last_message.content,
                        "requires_approval": requires_approval
                    }
                    
                    yield {
                        "event": "message",
                        "data": json.dumps(payload)
                    }
                    await asyncio.sleep(0.01)
                    
    except Exception as e:
        # Error Translation Interceptor (RM-friendly errors)
        error_msg = str(e)
        if "Adversarial input detected" in error_msg:
            friendly_msg = "⚠️ This request violates compliance guardrails and cannot be processed. Incident logged. Please rephrase your query without system command syntax."
        elif "Could not parse tool input" in error_msg:
            friendly_msg = "⚠️ Clarification needed to proceed with this request."
        else:
            friendly_msg = "⚠️ The system is currently unavailable. Please try again."
            
        payload = {
            "node": "error_interceptor",
            "content": friendly_msg,
            "requires_approval": False
        }
        yield {
            "event": "error",
            "data": json.dumps(payload)
        }

@app.post("/chat/stream")
async def chat_stream_endpoint(request: ChatRequest):
    return EventSourceResponse(stream_langgraph_response(request.message))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api.server:app", host="0.0.0.0", port=8000, reload=True)
