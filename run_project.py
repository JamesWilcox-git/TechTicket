import socket
import subprocess

# Get the local IP address
hostname = socket.gethostname()
ip_address = socket.gethostbyname(hostname)

# Define the port you want to use
port = 8000

# Start Daphne with the determined IP address and port
subprocess.run(['daphne', '-b', ip_address, '-p', str(port), 'myproject.asgi:application'])
