from fastapi import FastAPI
from pydantic import BaseModel
from analyst_agent_chat.controller.chat_controller import ChatController

app = FastAPI()

chat_controller = ChatController()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str

@app.post("/chat", response_model=ChatResponse)
def chat_entrypoint(request: ChatRequest):
    try:
        result = chat_controller.handle_message(request.message)

        if isinstance(result, dict):
            response = result.get("final_output", "")
        else:
            response = result

        return ChatResponse(response=response)
    
    except Exception as e:
        return ChatResponse(f"Error: {str(e)}")