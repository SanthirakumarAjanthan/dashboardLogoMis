import asyncio
import websockets

async def hello(websocket, path):
    try:
        name = await websocket.recv()
        print(f"Server received name: {name}")

        job = await websocket.recv()
        print(f"Server received job: {job}")

        greeting = f"Hello {name}! I see you're a {job}."
        await websocket.send(greeting)
        print(f"Server sent: {greeting}")
    except websockets.ConnectionClosed:
        print("Connection closed.")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        print("Shutting down connection gracefully...")

async def main():
    async with websockets.serve(hello, "localhost", 8766):  # Or your desired port
        await asyncio.Future()  # Keeps running until stopped

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Server is shutting down...")
