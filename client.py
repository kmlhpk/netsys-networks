import socket as skt
import sys
import pickle

# Determines whether client was invoked with some input arguments after client.py
# If not, sets host and port to default values (same defaults as server.py)
if len(sys.argv) == 1:
    serverHost = '127.0.0.1'
    serverPort = 12000
    print("Attempting to connect to default host:", serverHost, "default port:", serverPort)
# If two arguments were provided, sets serverHost to the first arg and serverPort to the second arg
elif len(sys.argv) == 3:
    serverHost = sys.argv[1]
    serverPort = sys.argv[2]
    print("Attempting to connect to host:", serverHost, "port:", serverPort)
# If only one, or three or more, input arguments were provided, returns an error message.
else:
    print("ERROR: You have provided an incorrect amount of arguments.")
    print("Please invoke the client in one of the following formats:")
    print("    python client.py")
    print("    python client.py serverHost serverPort")
    sys.exit()


# Creates a client socket and attempts to connect to server
clientSocket = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
clientSocket.connect((serverHost, serverPort))
print("Connection to host:", serverHost, "port:", serverPort, "succesful!\n")

# Welcome messages
print("---Welcome to MsgBrd!---\n")

### IMPLEMENT GET_BOARDS!!!!!!!!!!!!!

# Receives list of boards, prints its contents
boardList = pickle.loads(clientSocket.recv(1024))
if not boardList:
    print("There are no message boards, and thus nothing to do.")
    sys.exit()
else:
    print("Board list received succesfully. Here is a list of existing message boards:\n")
    for i in range(0,len(boardList)):
        print (" ",i+1,":",boardList[i])

print("\nPlease select an option:")
print(" -Enter a number between 1 and",len(boardList),"to view the corresponding board's 100 most recent messages.")
print(" -Enter POST to post a message to a board.")
print(" -Enter QUIT to quit the client.")
        
clientSocket.close()