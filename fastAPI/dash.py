import streamlit as st
import asyncio
import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

async def connect_websocket(uri):
    try:
        async with websockets.connect(uri) as websocket:
            st.session_state['websocket'] = websocket
            st.session_state['connected'] = True
            st.success("Connected to WebSocket")
            while True:  # Keep the connection alive
                message = await websocket.recv()
                st.write(f"Received: {message}")
    except ConnectionClosedOK:
        st.session_state['connected'] = False
        st.warning("WebSocket connection closed gracefully.")
    except ConnectionClosedError:
        st.session_state['connected'] = False
        st.error("WebSocket connection closed with an error.")
    except Exception as e:
        st.session_state['connected'] = False
        st.error(f"Failed to connect: {e}")

def send_message(message):
    try:
        if st.session_state.get('connected', False):
            asyncio.run(st.session_state['websocket'].send(message))
            st.success(f"Sent: {message}")
        else:
            st.error("WebSocket not connected")
    except ConnectionClosedOK:
        st.warning("Cannot send message, WebSocket connection closed.")
    except ConnectionClosedError:
        st.error("WebSocket connection closed with an error.")
    except Exception as e:
        st.error(f"Error sending message: {e}")

# Streamlit app layout
st.title("Streamlit WebSocket Example")

if st.button("Connect to WebSocket"):
    if not st.session_state.get('connected', False):
        asyncio.run(connect_websocket("ws://localhost:8000/ws"))
    else:
        st.info("Already connected.")

message = st.text_input("Message")
if st.button("Send Message"):
    send_message(message)

# Display connection status
if st.session_state.get('connected', False):
    st.write("WebSocket is connected.")
else:
    st.write("WebSocket is not connected.")
