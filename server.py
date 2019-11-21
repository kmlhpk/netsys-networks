import socket as skt
import sys
import pathlib
import pickle
import datetime

### FUNCTION DEFINITIONS ###

def writeLog(addr,date,req,ok): # CHANGE DATE FORMAT, CHECK WHAT'S UP WITH TAB DELIMITING
    addr = addr[0] + ":" + str(addr[1])
    if ok == True:
        status = "OK"
    else:
        status = "Error"
    log = addr+"\t"+date+"\t"+req+"\t"+status+"\n"
    path = pathlib.Path.cwd() / "server.log"
    with open(path,"a") as f:
        f.write(log)
    return
    
def makeBoardList():
    # Makes a list of paths of all directories in ./board
    path = pathlib.Path.cwd() / "board"
    boardPaths = [b for b in path.iterdir() if b.is_dir()]
    boardList = []
    for i in range(0,len(boardPaths)):
        # Makes board list from just the name of the final directory in each path
        boardList.append(boardPaths[i].name)
    return boardList

def makeMsgList(board):
    # Makes a list of paths of all files in ./board/<specified board>
    path = pathlib.Path.cwd() / "board" / board
    msgPaths = [m for m in path.iterdir() if m.is_file()]    
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
    path = pathlib.Path.cwd() / "board" / board / filename
    with open(path,"w") as f:
        f.write(msg)
    return

### MAIN CODE ###

# Determines whether server was invoked with some input arguments after server.py
# If not, sets IP and port to default values (same defaults as client.py)
if len(sys.argv) == 1:
    serverHost = '127.0.0.1'
    serverPort = 12000
    print("Using default host:", serverHost, "default port:", serverPort,"\n")
# If two arguments were provided, sets serverHost to the first arg and serverPort to the second arg
elif len(sys.argv) == 3 and type(sys.argv[2]) is int:
    serverHost = sys.argv[1]
    serverPort = sys.argv[2]
    print("Using host:", serverHost, "port:", serverPort,"\n")
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
    if request[0] == "GET_BOARDS":
        print("Received a GET_BOARDS request") # MAKE SURE TO LOG THESE!!!
        boardList = pickle.dumps(makeBoardList())
        conn.send(boardList)
        conn.close()
        writeLog(addr,str(datetime.datetime.now()),request[0],True)
        
    elif request[0] == "GET_MESSAGES":
        print("Client requests messages from board "+request[1])
        msgList = pickle.dumps(makeMsgList(request[1]))
        conn.send(msgList)
        conn.close()
        writeLog(addr,str(datetime.datetime.now()),request[0],True)
        
    elif request[0] == "POST_MESSAGE":
        print("Client wants to post message to board "+request[1])
        makeMsg(request[1],request[2],request[3])
        conn.close()
        writeLog(addr,str(datetime.datetime.now()),request[0],True)
        
        