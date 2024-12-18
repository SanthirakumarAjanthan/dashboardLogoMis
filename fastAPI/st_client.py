import asyncio
import websockets
import streamlit as st

# WebSocket client
async def hello(name):
    uri = "ws://localhost:8765"
    async with websockets.connect(uri) as websocket:
        await websocket.send(name)
        greeting = await websocket.recv()
        return greeting

# Streamlit UI
st.title('WebSocket Client')

name_input = st.text_input('Enter your name:')

if st.button('Send'):
    if name_input:
        # Run the WebSocket client and display the result
        greeting = asyncio.run(hello(name_input))
        st.success(greeting)
    else:
        st.error('Please enter a name.')
