import socket, sys, threading, os

def handle_client(client_socket):
    # Richiede il nome del client
    client_socket.send(b'Inserisci il tuo nome: ')
    client_name = client_socket.recv(1024).decode().strip()

    # Messaggio di benvenuto
    welcome_message = f'Benvenuto, {client_name}!\n'
    client_socket.send(welcome_message.encode())

    while True:
        try:
            # Ricevi il messaggio inviato dal client
            data = client_socket.recv(1024).decode()
            if not data:
                break

            # Stampa il messaggio con il nome del client
            message_with_name = f'({client_name}) {data}'
            print(message_with_name)

            # Manda il messaggio a tutti i client tranne al mittente
            broadcast_message(message_with_name, client_socket)

        except Exception as e:
            print(f"Errore nella gestione del client: {e}")
            break

def broadcast_message(message, client_to_exclude):
    for client in clients:
        if client != client_to_exclude:
            try:
                client.send(message.encode())
            except Exception as e:
                print(f"Errore nell'invio del messaggio a un client: {e}")
                client.close()
                clients.remove(client)

HOST = '0.0.0.0'  # Ascolta su tutte le interfacce
try:
    PORT = int(sys.argv[1])
except:
    print(f"Usage: python3 {os.path.basename(__file__)} <int:port>")
    exit()

# Lista per tutti i client che si connetteranno
clients = []

# Server socket
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(20)

print(f"In ascolto su {socket.gethostbyname(socket.gethostname())}:{PORT}")

while True:
    try:
        # Accetta la connessione di un client
        client_sock, client_addr = server.accept()
        print(f"Connessione accettata da {client_addr[0]}:{client_addr[1]}")

        # Aggiungi il client alla lista
        clients.append(client_sock)

        # Thread per gestire il client
        client_handler = threading.Thread(target=handle_client, args=(client_sock,))
        client_handler.start()

    except KeyboardInterrupt:
        print("Chiusura del server.")
        break
