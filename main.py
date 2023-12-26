import os
import streamlit as st
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from Bard import Chatbot

# Initialize FastAPI app within Streamlit
app = FastAPI()

# Define the Message model
class Message(BaseModel):
    session_id: str
    message: str

# Define the ask endpoint within the FastAPI app
@app.post("/ask")
async def ask(request: Request, message: Message) -> dict:
    # Handle authorization if needed
    user_auth_key = os.getenv('USER_AUTH_KEY')
    if user_auth_key and user_auth_key != request.headers.get('Authorization'):
        raise HTTPException(status_code=401, detail='Invalid authorization key')

    # Create the chatbot instance
    chatbot = Chatbot(message.session_id)

    # Get the chatbot's response
    response = chatbot.ask(message.message)
    return response

# Create the Streamlit app
def main():
    st.title("Chat with Bard")

    # Create a session_id for the user
    session_id = st.session_state.get("session_id", st.secrets.token())
    st.session_state["session_id"] = session_id

    message = st.text_input("Enter your message:")

    if message:
        try:
            # Call the FastAPI endpoint within Streamlit
            response = st.experimental_submit_to_api(
                "/ask",
                methods=["POST"],
                data=dict(session_id=session_id, message=message),
            )
            st.write(response.json())
        except HTTPException as e:
            st.error(e.detail)

if __name__ == "__main__":
    # Run the Streamlit app and FastAPI server concurrently
    import uvicorn

    uvicorn.run(app, host="localhost", port=8501)  # Adjust port if needed
    main()
