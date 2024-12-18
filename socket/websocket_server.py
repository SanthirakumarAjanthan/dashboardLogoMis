import streamlit as st
import asyncio
import websockets

async def fetch_data():
    uri = "ws://localhost:6789"
    async with websockets.connect(uri) as websocket:
        data = await websocket.recv()
        return data

# Use Streamlit's caching to avoid setting up the WebSocket connection on each rerun
@st.cache(ttl=600, allow_output_mutation=True)
def get_data():
    return asyncio.run(fetch_data())

data = get_data()
# Visualize the data
st.write(data)