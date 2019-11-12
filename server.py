import socket as skt
import sys
import pathlib
import pickle

# FUNCTION DEFINITIONS

# Mkaes a list of the board folders within ./board for client to display
def makeBoardList():
    path = pathlib.Path("./board")
    # Fills list of full pathnames
    rawList = [b for b in path.iterdir() if b.is_dir()]
    boardList = []
    for i in range(0,len(rawList)):
        # Extracts the name of the subfolder from full pathname and removes its underscores. Should be OS-agnostic re: slashes.
        name = str(rawList[i]).replace("\\","/").split("/")[-1].replace("_"," ")
        boardList.append(name)
    return boardList

# MAIN PROGRAM

# Determines whether server was invoked with some input arguments after server.py
# If not, sets IP and port to default values (same defaults as client.py)
if len(sys.argv) == 1:
    serverHost = '127.0.0.1'
    serverPort = 12000
    print("Attempting to listen on default host:", serverHost, "default port:", serverPort)
# If two arguments were provided, sets serverHost to the first arg and serverPort to the second arg
elif len(sys.argv) == 3:
    serverHost = sys.argv[1]
    serverPort = sys.argv[2]
    print("Attempting to listen on host:", serverHost, "port:", serverPort)
# If only one, or three or more, input arguments were provided, returns an error message.
else:
    print("ERROR: You have provided an incorrect amount of arguments.")
    print("Please invoke the server in one of the following formats:")
    print("    python server.py")
    print("    python server.py serverHost serverPort")
    sys.exit()

server = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
server.bind((serverHost, serverPort))
server.listen() # Provide listen() with an integer argument to limit the amount of concurrent connections
print("The server is listening for client connections on host:", serverHost, "port:", serverPort)

while True:
    conn, addr = server.accept()
    print("Connection made with client:", addr)
    boardList = pickle.dumps(makeBoardList())
    conn.send(boardList)
    conn.close()