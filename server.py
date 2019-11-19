import socket as skt
import sys
import pathlib
import pickle

### FUNCTION DEFINITIONS ###

def makeBoardList():
    path = pathlib.Path("./board")
    boardPaths = [b for b in path.iterdir() if b.is_dir()]
    boardList = []
    for i in range(0,len(boardPaths)):
        name = str(boardPaths[i]).replace("\\","/").split("/")[-1].replace("_"," ")
        boardList.append(name)
    return boardList

def makeMsgList(board):
    path = pathlib.Path.cwd() / "board" / board
    msgPaths = [m for m in path.iterdir() if m.is_file()]
    msgList = [[],[]]
    for i in range(0,len(msgPaths)):
        with open(msgPaths[i],"r") as f:
            msgList[1].append(f.read())
    return msgList

### MAIN EXECUTABLE CODE ###

# Determines whether server was invoked with some input arguments after server.py
# If not, sets IP and port to default values (same defaults as client.py)
if len(sys.argv) == 1:
    serverHost = '127.0.0.1'
    serverPort = 12000
    print("Attempting to listen on default host:", serverHost, "default port:", serverPort)
# If two arguments were provided, sets serverHost to the first arg and serverPort to the second arg
elif len(sys.argv) == 3 and type(sys.argv[2]) is int:
    serverHost = sys.argv[1]
    serverPort = sys.argv[2]
    print("Attempting to listen on host:", serverHost, "port:", serverPort)
# If only one, or three or more, input arguments were provided, returns an error message.
else:
    print("ERROR: You have provided an incorrect amount of arguments, or used the wrong type of argument.")
    print("Please invoke the server in one of the following formats:")
    print("    python server.py")
    print("    python server.py serverHost serverPort")
    print("Where serverHost is the IP or host you want to listen on (string or integer), and severPort is a port number (integer)")
    sys.exit()
    

server = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
server.bind((serverHost, serverPort))
server.listen() # Provide listen() with an integer argument to limit the amount of concurrent connections
print("The server is listening for client connections on host:", serverHost, "port:", serverPort)

while True:
    conn, addr = server.accept()
    print("Connection made with client:", addr)
    request = pickle.loads(conn.recv(1024))
    print(request)
    if request[0] == "GET_BOARDS":
        print("Received a GET_BOARDS request") # MAKE SURE TO LOG THIS!!!
        boardList = pickle.dumps(makeBoardList())
        conn.send(boardList)
        conn.close()
    elif request[0] == "GET_MESSAGES":
        print(request[1])
        msgList = pickle.dumps(makeMsgList(request[1]))
        conn.send(msgList)
        conn.close()


