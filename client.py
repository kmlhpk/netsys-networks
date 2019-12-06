import socket as skt
import sys
import pickle
import datetime

############################
### FUNCTION DEFINITIONS ###
############################

def newSocket():
    # Creates a new socket with a timeout of 10s
    client = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
    client.settimeout(10)
    client.connect((serverHost, serverPort))
    return client

def getBoards():
    # Requests a board list from the server
    request = ["GET_BOARDS"]
    client.sendall(pickle.dumps(request))
    # Deals with large incoming data by forming data first, then unpickling    
    data = b""
    while True:
        packet = client.recv(4096)
        if not packet:
            break
        data += packet
    boardList = pickle.loads(data)
    if not boardList: # ie. If the board list is empty
        print("There are no message boards, and thus nothing to display or do. Exiting client.")
        sys.exit()
    elif boardList == "Error":
        print("The server failed to provide a boardlist. Exiting client.")
        sys.exit()
    else: # If everything went well:
        return boardList

def getMessages(boardNum):
    # Requests a list of messages in a board from the server
    board = boardList[int(boardNum)-1]
    request = ["GET_MESSAGES",board]
    client = newSocket()
    client.sendall(pickle.dumps(request))
    # Deals with large incoming data by forming data first, then unpickling
    data = b""
    while True:
        packet = client.recv(4096)
        if not packet:
            break
        data += packet
    msgList = pickle.loads(data)
    if not msgList: # ie. If there are no messages in that board
        print("\nThere are no messages in this board, and thus nothing to display.")
    elif msgList == "Error":
        print("\nThere has been an error in retrieving messages. Awaiting further input.")
    else: # If everything went well:
        # Prints the messages, their titles and their dates with a bit of formatting.
        print("\nThese are the last",len(msgList),"message(s) in the board " + board + "\n")
        for i in range(0,len(msgList)):
            print("Date: ",msgList[i][0])
            print("Title: "+msgList[i][1])
            print("Body:  " + msgList[i][2]+"\n")
    return

def sendMessage():
    # Prompts the user for input
    boardInt = input("Enter a number between 1 and "+str(len(boardList))+" to select a board to post your message to.\n")
    try:
        # If user didn't provide integer for their board number/if another input causes some sort of error, it will be caught
        # Otherwise, takes and formats user input
        board = boardList[int(boardInt)-1]
        title = input("Give your message a title.\n").replace(" ","_")
        msg = input("Write your message.\n")
        date = datetime.datetime.now()
        date = date.strftime("%Y%m%d")+"-"+date.strftime("%H%M%S")
    except:
        print("Invalid input - please try again.")
        return
    filename = date +"-"+ title
    request = ["POST_MESSAGE",board,filename,msg]
    # Attempts to post message to specified board
    client = newSocket()
    client.sendall(pickle.dumps(request))
    result = pickle.loads(client.recv(4096))
    if result == "OK":
        print("Message posted successfully.")
    else:
        print("There was a problem posting your message - perhaps you used inappropriate characters in your title?")
    
#################
### MAIN CODE ###
#################

# Determines whether client was invoked with some input arguments after client.py
# If not, sets host and port to default values (same defaults as server.py)
if len(sys.argv) == 1:
    serverHost = '127.0.0.1'
    serverPort = 12000
    print("Using default host:", serverHost, "default port:", serverPort,"\n")
# If two arguments were provided, sets serverHost to the first arg and serverPort to the second arg
elif len(sys.argv) == 3 and sys.argv[2].isdigit():
    serverHost = sys.argv[1]
    serverPort = int(sys.argv[2])
    print("Using host:", serverHost, "port:", serverPort,"\n")
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
try:
    # Creates a client socket and attempts to connect to server
    client = newSocket()
except:
    # If client cannot connect to server for some reason, exit client
    print("Cannot establish connection with server. Exiting client.")
    sys.exit()
    
# Asks for a list of boards, prints its contents
try:
    boardList = getBoards()
    print("Board list received succesfully. Here is a list of existing message boards:\n")
    for i in range(0,len(boardList)):
        print (" ",i+1,":",boardList[i])
except Exception:
    print("The server took too long to respond, or there was another error. Exiting client.")
    sys.exit(1)

# Always prompts the user for input after successful completion of a request
while True:
    print("\nPlease select an option:")
    print(" -Enter a number between 1 and "+str(len(boardList))+" to view the corresponding board's 100 most recent messages.")
    print(" -Enter POST to post a message to a board.")
    print(" -Enter QUIT to quit the client.")
    command = input()
    # Interprets command and tries to execute it
    if command == "QUIT":
        client.close()
        sys.exit()
    elif command == "POST":
        try:
            sendMessage()
        except Exception:
            print("The server took too long to respond, or there was another error. Exiting client.")
            sys.exit(1)
    else:
        if command.isdigit():
            if int(command) in range(1,len(boardList)+1):
                try:
                    getMessages(command)
                except Exception:
                    print("The server took too long to respond, or there was another error. Exiting client.")
                    sys.exit(1)
            else:
                print("\nPlease enter a valid number.")
        else:
            print("\nPlease enter a valid command.")