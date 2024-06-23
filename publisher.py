import socket

SERVER_HOST = 'localhost'
SERVER_PORT = 2023

# Create a publisher socket
publisher_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
publisher_socket.connect((SERVER_HOST, SERVER_PORT))

try:
    while True:
        sym = input("Enter stock symbol (or 'exit' to quit): ")
        if sym.lower() == 'exit':
            break
        info = input("Enter stock information: ")
        security = input("Enter security code: ")

        # Send the publish request to the server
        message = f'PUB [{sym}] ({info}) [{security}]'
        publisher_socket.send(message.encode())
        response = publisher_socket.recv(1024).decode()

        # Check the server's response and print accordingly
        if response.startswith("Successfully Published!"):
            print(response)  # Output successful publishing message
        elif response.startswith("Invalid Stock Code") or response.startswith("Invalid Security Code"):
            print(response)  # Output invalid stock code or security code message

except KeyboardInterrupt:
    print("Publisher terminated.")
finally:
    publisher_socket.close()

