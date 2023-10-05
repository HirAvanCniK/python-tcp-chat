from pwn import *

try:
    HOST = sys.argv[1]
    PORT = int(sys.argv[2])
except:
    print(f"Usage: python3 {os.path.basename(__file__)} <str:ip_address> <int:port>")
    exit()

server = remote(HOST, PORT)

server.interactive()