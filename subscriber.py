import socket
import random
import string

SERVER_HOST = 'localhost'
SERVER_PORT = 2023

# Create a subscriber socket
subscriber_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Connect to the server
subscriber_socket.connect((SERVER_HOST, SERVER_PORT))

# Generate a random subscriber ID
subscriber_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Send the subscriber type ('SUB') and ID to the server
subscriber_socket.send(f"SUB {subscriber_id}".encode())

try:
    while True:
        print("Enter 'SUB' to subscribe to stocks, 'BID' to bid, or 'exit' to quit:")
        user_input = input().strip().upper()
        
        if user_input == 'EXIT':
            break
        elif user_input == 'SUB':
            symbols = input("Enter stock symbols separated by space (e.g., AAL AAPL): ")
            symbol_list = symbols.split()
            for symbol in symbol_list:
                subscriber_socket.send(f"SUB {symbol}".encode())
                response = subscriber_socket.recv(1024).decode()
                if response.startswith("Successfully Subscribed!"):
                    print(response)  # Output successful subscription message
                elif response.startswith("Invalid Code"):
                    print(response)  # Output invalid code message
        elif user_input == 'BID':
            symbols = input("Enter bid symbols separated by space (e.g., AAL AAPL): ")
            symbol_list = symbols.split()
            subscriber_socket.send(f"BID {' '.join(symbol_list)}".encode())
            response = subscriber_socket.recv(1024).decode()
            if response.startswith("Successfully Bid"):
                print(response)  # Output successful bid message
            elif response.startswith("Invalid Code"):
                print(response)  # Output invalid code message
        else:
            print("Invalid input. Please enter 'SUB', 'BID', or 'EXIT'.")

except KeyboardInterrupt:
    print("Subscriber terminated.")
finally:
    subscriber_socket.close()
