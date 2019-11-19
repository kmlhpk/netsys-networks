import socket as skt
import sys
import pickle

### FUNCTION DEFINITIONS ###

def newSocket():
    client = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
    client.connect((serverHost, serverPort))
    print("Connection to host:", serverHost, "port:", serverPort, "succesful!") # MAY WANT TO GET RID OF THIS EVENTUALLY
    return client

def getBoards():
    request = ["GET_BOARDS"]
    client.send(pickle.dumps(request))
    boardList = pickle.loads(client.recv(1024))
    if not boardList:
        print("There are no message boards, and thus nothing to display or do.")
        sys.exit()
    else:
        return boardList

def getMessages(board):
    request = ["GET_MESSAGES",board]
    client.send(pickle.dumps(request))
    msgList = pickle.loads(client.recv(1024))
    if not msgList:
        print("There are no messages in this board, and thus nothing to display.")
    else:
        return msgList
    
### MAIN EXECUTABLE CODE

# Determines whether client was invoked with some input arguments after client.py
# If not, sets host and port to default values (same defaults as server.py)
if len(sys.argv) == 1:
    serverHost = '127.0.0.1'
    serverPort = 12000
    print("Attempting to connect to default host:", serverHost, "default port:", serverPort)
# If two arguments were provided, sets serverHost to the first arg and serverPort to the second arg
elif len(sys.argv) == 3 and type(sys.argv[2]) is int:
    serverHost = sys.argv[1]
    serverPort = sys.argv[2]
    print("Attempting to connect to host:", serverHost, "port:", serverPort)
# If only one, or three or more, input arguments were provided, returns an error message.
else:
    print("ERROR: You have provided an incorrect amount of arguments, or used the wrong type of argument.")
    print("Please invoke the client in one of the following formats:")
    print("    python client.py")
    print("    python client.py serverHost serverPort")
    print("Where serverHost is the IP or host you want to connect to (string or integer), and severPort is a port number (integer)")
    sys.exit()


# Welcome message
print("---Welcome to MsgBrd!---\n")
# Creates a client socket and attempts to connect to server
client = newSocket()
# Receives list of boards, prints its contents
boardList = getBoards()
print("Board list received succesfully. Here is a list of existing message boards:\n")
for i in range(0,len(boardList)):
    print (" ",i+1,":",boardList[i])
        
while True:
    client = newSocket()
    print("\nPlease select an option:")
    print(" -Enter a number between 1 and",len(boardList),"to view the corresponding board's 100 most recent messages.")
    print(" -Enter POST to post a message to a board.")
    print(" -Enter QUIT to quit the client.")
    
    command = input()
    if command == "QUIT":
        client.close()
        sys.exit()
    elif int(command) in range(1,len(boardList)+1):
        board = boardList[int(command)-1].replace(" ","_")
        msgList = getMessages(board)
        print(msgList)