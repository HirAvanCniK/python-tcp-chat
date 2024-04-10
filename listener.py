import socket, sys, threading, os
from pwn import log
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad

def handle_client(client_socket):
    # Requires client name
    client_socket.send(b'Insert your name: ')
    client_name = client_socket.recv(1024).decode().strip()

    if(len(client_name) > 20):
        client_socket.send(b"Name too long\n")
        client_socket.close()
    elif client_name in usernames.values():
        client_socket.send(b"Name already used\n")
        client_socket.close()
    else:
        # Requires server key
        client_socket.send(b'Insert server authentication key (hex): ')
        client_insert_key = client_socket.recv(1024).decode().strip()

        if(client_insert_key != SERVER_KEY.hex()):
            client_socket.send(b"Invalid key!\nExit from the server...\n")
            client_socket.close()
        else:
            # Welcome message
            welcome_message = f'Welcome, {client_name}!\n'
            client_socket.send(welcome_message.encode())
            log.warn(f"User logged in as {client_name}")
            usernames[client_socket] = client_name

            # Add the client to the list
            clients.append(client_socket)

            while True:
                try:
                    # Receive the message sent by the client
                    data = client_socket.recv(1024).decode()
                    if not data:
                        break

                    # Prints the message with the client name
                    message_with_name = f'({client_name}) {data}'
                    log.info(message_with_name)

                    # Send the message to all clients except the sender
                    broadcast_message(E_CIPHER.encrypt(pad(message_with_name.encode(), AES.block_size)), client_socket)
                except Exception as e:
                    # log.critical(f"Error in client management: {e}")
                    log.warning(f"Client {client_name} has disconnected")
                    clients.remove(client_socket)
                    usernames.pop(client_socket)
                    broadcast_message(E_CIPHER.encrypt(pad(f"{client_name} has disconnected\n".encode(), AES.block_size)), client_socket)
                    break

def broadcast_message(message, client_to_exclude):
    for client in clients:
        if client != client_to_exclude:
            try:
                client.send(unpad(D_CIPHER.decrypt(message), AES.block_size))
            except Exception as e:
                log.warning(f"Error sending message to client: {e}")
                client.close()
                clients.remove(client)
                usernames.pop(client)

SERVER_KEY = os.urandom(32)
log.warn(f"Server random key: {SERVER_KEY.hex()}")

# Random server encryption IV
SERVER_IV = os.urandom(16)

E_CIPHER = AES.new(SERVER_KEY, AES.MODE_CBC, SERVER_IV)
D_CIPHER = AES.new(SERVER_KEY, AES.MODE_CBC, SERVER_IV)

try:
    PORT = int(sys.argv[1])
except:
    log.error(f"Usage: python3 {os.path.basename(__file__)} <int:port>")

# Listen on all interfaces
HOST = '0.0.0.0'

# List for all clients that will connect
clients = []
usernames = {}

# Server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))

# Max clients
server.listen(20)

log.info(f"Listen on {socket.gethostbyname(socket.gethostname())}:{PORT}")

while True:
    try:
        # Accept a client connection
        client_sock, client_addr = server.accept()
        log.success(f"Connection accepted {client_addr[0]}:{client_addr[1]}")

        # Thread to manage the client
        client_handler = threading.Thread(target=handle_client, args=(client_sock,))
        client_handler.start()
    except:
        log.info("Server shutdown...")
        break
