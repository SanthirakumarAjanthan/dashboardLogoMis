import os
import socket

# Create a socket object
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Correct the connect method to pass a tuple with the host and port
client.connect(("localhost", 9999))

# Open the file in binary mode
file = open("image.png", "rb")
file_size = os.path.getsize("image.png")

# Send the file name and file size to the server
client.send("received_image.png".encode())  # Send the filename
client.send(str(file_size).encode())        # Send the file size (corrected missing parentheses)

# Read and send the file data
data = file.read()
client.sendall(data)

# Send an end-of-file marker
client.send(b"<END>")

# Close the file and socket
file.close()
client.close()
