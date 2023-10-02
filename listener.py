import socket, sys, threading, os

def handle_client(client_socket):
    # Requires client name
    client_socket.send(b'Insert your name: ')
    client_name = client_socket.recv(1024).decode().strip()

    # Welcome message
    welcome_message = f'Welcome, {client_name}!\n'
    client_socket.send(welcome_message.encode())

    while True:
        try:
            # Receive the message sent by the client
            data = client_socket.recv(1024).decode()
            if not data:
                break

            # Prints the message with the client name
            message_with_name = f'({client_name}) {data}'
            print(message_with_name)

            # Send the message to all clients except the sender
            broadcast_message(message_with_name, client_socket)

        except Exception as e:
            print(f"Error in client management: {e}")
            break

def broadcast_message(message, client_to_exclude):
    for client in clients:
        if client != client_to_exclude:
            try:
                client.send(message.encode())
            except Exception as e:
                print(f"Error sending message to client: {e}")
                client.close()
                clients.remove(client)

HOST = '0.0.0.0'  # Listen on all interfaces
try:
    PORT = int(sys.argv[1])
except:
    print(f"Usage: python3 {os.path.basename(__file__)} <int:port>")
    exit()

# List for all clients that will connect
clients = []

# Server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(20) # Max clients

print(f"Listen on {socket.gethostbyname(socket.gethostname())}:{PORT}")

while True:
    try:
        # Accept a client connection
        client_sock, client_addr = server.accept()
        print(f"Connection accepted {client_addr[0]}:{client_addr[1]}")

        # Add the client to the list
        clients.append(client_sock)

        # Thread to manage the client
        client_handler = threading.Thread(target=handle_client, args=(client_sock,))
        client_handler.start()

    except KeyboardInterrupt:
        print("Server shutdown...")
        break
