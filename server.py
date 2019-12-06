import socket as skt
import sys
import pathlib
import pickle
import datetime

############################
### FUNCTION DEFINITIONS ###
############################

def writeLog(addr,req,ok):
    # Makes message consisting of...
    # ...client connection socket's details
    addr = addr[0] + ":" + str(addr[1])
    # ...date and time of request
    date = datetime.datetime.now()
    date = date.strftime("%Y-%m-%d")+"@"+date.strftime("%H:%M:%S")
    # ...and result of request
    if ok == True:
        status = "OK"
    else:
        status = "Error"
    # Concatenates info into single string, with tab delimiting
    log = addr+"\t"+date+"\t"+req+"\t"+status+"\n"
    path = pathlib.Path.cwd() / "server.log"
    print(type(path))
    print(path)
    # Attempts to append log to server.log
    try:
        with open(path,"a") as f:
            f.write(log)
    except:
        print("There was an error attempting to write a log.")
    return

def makeBoardList():
    # Makes a list of paths of directories in ./board
    path = pathlib.Path.cwd() / "board"
    boardPaths = [b for b in path.iterdir() if b.is_dir()]
    boardList = []
    for i in range(0,len(boardPaths)):
        # Makes board list from just the name of the final directory in each path
        boardList.append(boardPaths[i].name)
    return boardList

def makeMsgList(board):
    # Makes a list of paths of files in ./board/<specified board>
    path = pathlib.Path.cwd() / "board" / board
    msgPaths = [m for m in path.iterdir() if m.is_file()]
    print(msgPaths)
    msgList = []
    for i in range(0,len(msgPaths)):
        try:
            # Checks if filename is delimited correctly
            fullTitle = msgPaths[i].stem.split("-")
            # Checks if there are >=3 parts to filename by trying to pull out title
            title = fullTitle[2].replace("_"," ")
            # Checks for YYYYMMDD-HHMMSS formatting by trying to convert into integers and making a date obj
            dateInt = [int(fullTitle[0][0:4]), int(fullTitle[0][4:6]), int(fullTitle[0][6:])]
            timeInt = [int(fullTitle[1][0:2]), int(fullTitle[1][2:4]), int(fullTitle[1][4:])]
            date = datetime.datetime(dateInt[0],dateInt[1],dateInt[2],timeInt[0],timeInt[1],timeInt[2])
            # Appends relevant data to array
            with open(msgPaths[i],"r") as f:
                msgList.append([date,title,f.read()])
        except:
            print("Message title has invalid format. Skipping message.")
            continue
    # Makes a key function for sorting the messages by date
    def takeDate(lst):
        return lst[0]
    # Sorts messages by date
    msgList.sort(key=takeDate)
    # Limits to 100 messages
    msgList = msgList[:100]
    return msgList

def makeMsg(board,filename,msg):
    # Creates a file with appropriate name and content, and places in correct position, based on arguments
    path = pathlib.Path.cwd() / "board" / board / filename
    with open(path,"w") as f:
        f.write(msg)
    return

#################
### MAIN CODE ###
#################

# Determines whether server was invoked with some input arguments after server.py
# If not, sets IP and port to default values (same defaults as client.py)
if len(sys.argv) == 1:
    serverHost = '127.0.0.1'
    serverPort = 12000
    print("Using default host:", serverHost, "default port:", serverPort,"\n")
# If two arguments were provided, sets serverHost to the first arg and serverPort to the second arg
elif len(sys.argv) == 3 and sys.argv[2].isdigit():
    serverHost = sys.argv[1]
    serverPort = int(sys.argv[2])
    print("Using host:", serverHost, "port:", serverPort,"\n")
# If only one, or three or more, or invalid input arguments were provided, returns an error message.
else:
    print("ERROR: You have provided an incorrect amount of arguments, or used the wrong type of argument.")
    print("Please invoke the server in one of the following formats:")
    print("    python server.py")
    print("    python server.py serverHost serverPort")
    print("Where serverHost is the IP or host you want to listen on (string or integer), and severPort is a port number (integer)")
    sys.exit()

try:
    # If no boards exist, server quits
    if not makeBoardList():
        print("No message boards have been defined. Exiting server.")
        sys.exit()
except:
    # If the ./board folder doesn't exist, or there's some other error with calling makeBoardList, server quits
    print("Unable to create board list. Exiting server.")
    sys.exit()

# Attempts to bind server to socket with provided host and port
try:
    server = skt.socket(skt.AF_INET, skt.SOCK_STREAM)
    server.bind((serverHost, serverPort))
    server.listen() # Provide listen() with an integer argument to limit the amount of concurrent connections
    print("The server is listening for client connections on host:", serverHost, "port:", serverPort)
except:
    print("The IP or Port are invalid, unavailable or busy. Exiting server.")
    sys.exit()

# Constantly waits for connections with client
while True:
    conn, addr = server.accept()
    print("Connection made with client:", addr)
    try:
        request = pickle.loads(conn.recv(2048))
    except:
        print("Error receiving request - either it's too long, or something else went wrong.")
        conn.close
        continue
    
    # Checks if request is in a list-like data structure
    if isinstance(request,list) or isinstance(request,tuple):
        pass
    else:
        print("Server expected a request of type list or tuple, but did not receive it - closing connection.")
        conn.close()
        continue
    
    # Interprets request and tries to execute it
    if request[0] == "GET_BOARDS":
        print("Client requests a list of boards")
        try:
            boardList = makeBoardList()
            if not boardList:
                print("No message boards have been defined. Exiting server.")
                conn.send(pickle.dumps(boardList)) # NB: An empty boardList is treated as an exit condition by the client
                conn.close()
                writeLog(addr,request[0],True)
                sys.exit(1)
            else:
                conn.send(pickle.dumps(boardList))
                conn.close()
                writeLog(addr,request[0],True)
        except Exception:
            print("Failed to acquire boards.")
            writeLog(addr,request[0],False)
            conn.send(pickle.dumps("Error"))
            conn.close()
            
    elif request[0] == "GET_MESSAGES":
        try:
            print("Client requests messages from board "+request[1])
            msgList = pickle.dumps(makeMsgList(request[1]))
            conn.send(msgList)
            conn.close()
            writeLog(addr,request[0],True)
        except:
            print("Failed to acquire messages - either the board doesn't exist, or another error has occured.")
            writeLog(addr,request[0],False)
            conn.send(pickle.dumps("Error"))
            conn.close()
    elif request[0] == "POST_MESSAGE":
        try:
            print("Client wants to post message to board "+request[1])
            makeMsg(request[1],request[2],request[3])
            writeLog(addr,request[0],True)
            conn.send(pickle.dumps("OK"))
            conn.close()
        except:
            print("Request came with too few arguments, or another error has occured.")
            writeLog(addr,request[0],False)
            conn.send(pickle.dumps("Error"))            
            conn.close()
    else:
        # If the request is not recognised, closes socket
        print("Invalid or unrecognised request.")
        conn.close()
        writeLog(addr,"UNKNOWN",False)
        
        
        