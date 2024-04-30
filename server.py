import socket, sys, threading, os, datetime, random, string
# from pwn import log

def logs(message):
    time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    open(FILELOG_NAME, "a").write(f"[{time}] {message.strip()}\n")

def handle_client(client_socket):
    # Requires client name
    client_socket.send(b'Insert your name: ')
    client_name = client_socket.recv(1024).decode().strip()

    if len(client_name) > 20 or len(client_name) < 5:
        client_socket.send(b"Error: Incorrect name length!\n")
        client_socket.close()
    elif client_name in clients.values():
        client_socket.send(b"Error: Name already used!\n")
        client_socket.close()
    else:
        # Requires server key
        client_socket.send(b'Insert server authentication key: ')
        client_insert_key = client_socket.recv(1024).decode().strip()

        if(client_insert_key != SERVER_KEY):
            client_socket.send(b"Error: Invalid key!\nExit from the server...\n")
            client_socket.close()
        else:
            # Welcome message
            welcome_message = f'Welcome, {client_name}!\n'
            client_socket.send(welcome_message.encode())
            # log.warn(f"User logged in as {client_name}")
            # print(f"User logged in as {client_name}")
            logs(f"User logged in as {client_name}")

            # Add the client to the list
            clients[client_socket] = client_name

            while True:
                try:
                    # Receive the message sent by the client
                    data = client_socket.recv(1024).decode()
                    if not data:
                        break

                    # Prints the message with the client name
                    message_with_name = f'({client_name}) {data}'
                    # log.info(message_with_name)
                    # print(message_with_name)
                    logs(message_with_name)

                    # Send the message to all clients except the sender
                    broadcast_message(message_with_name, client_socket)
                except Exception as e:
                    # log.critical(f"Error in client management: {e}")
                    # log.warning(f"Client {client_name} has disconnected")
                    # print(f"Client {client_name} has disconnected")
                    logs(f"Client {client_name} has disconnected")
                    clients.pop(client_socket)
                    broadcast_message(f"{client_name} has disconnected\n", client_socket)
                    break

def broadcast_message(message, client_to_exclude):
    for client in clients.keys():
        if client != client_to_exclude:
            try:
                client.send(message.encode())
            except Exception as e:
                # log.warning(f"Error sending message to client: {e}")
                # print(f"Error sending message to client: {e}")
                logs(f"Error sending message to client: {e}")
                client.close()
                clients.pop(client)

def get_params():
    if len(sys.argv) == 3:
        try:
            return int(sys.argv[1]), sys.argv[2]
        except:
            return None
    elif len(sys.argv) == 2:
        return int(sys.argv[1]), random.choices(string.ascii_letters+string.digits, k=10)
    else:
        return None

if __name__ == "__main__":
    params = get_params()
    if params is None:
        print(f"Usage: python3 {os.path.basename(__file__)} <int:port> [str:server_key]")
    elif len(params[1]) < 5:
        print(f"Error: Incorrect server_key length!")
    else:
        PORT, SERVER_KEY = params
        time = datetime.datetime.now().strftime("%d.%m.%Y %H.%M.%S")
        FILELOG_NAME = f"pychat_{time}.log"

    # log.warn(f"Server random key: {SERVER_KEY.hex()}")
    print(f"Server key: {SERVER_KEY}")
    logs(f"Server key: {SERVER_KEY}")
    open("server.key", "w").write(SERVER_KEY+"\n")

    # List for all clients that will connect
    clients = {}

    # Server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', PORT))
    server.listen()

    # Max number of clients
    LIMIT = 20

    # log.info(f"Listen on {socket.gethostbyname(socket.gethostname())}:{PORT}")
    # print(f"Listen on {socket.gethostbyname(socket.gethostname())}:{PORT}")
    logs(f"Listen on {socket.gethostbyname(socket.gethostname())}:{PORT}")

    while True:
        try:
            # Accept a client connection
            client_sock, client_addr = server.accept()

            # Accepts client connection only if connected clients are less than the LIMIT
            if len(clients) < LIMIT:
                # log.success(f"Connection accepted {client_addr[0]}:{client_addr[1]}")
                # print(f"Connection accepted {client_addr[0]}:{client_addr[1]}")
                logs(f"Connection accepted {client_addr[0]}:{client_addr[1]}")

                # Thread to manage the client
                client_handler = threading.Thread(target=handle_client, args=(client_sock,))
                client_handler.start()
            else:
                client_sock.send(b"Error: Clients limit reached!\n")
                client_sock.close()
        except:
            # log.info("Server shutdown...")
            # print("Server shutdown...")
            # logs("Server shutdown...")
            # break
            pass
