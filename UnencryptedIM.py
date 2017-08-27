import sys
import socket
import signal
import select



if len(sys.argv) != 3:
    print "Usage: UnencryptedIM -s|-c hostname"
else:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def cchandler(signal, frame):
        sys.stdout.write("\nProgram terminated\n")
        sys.exit()
        s.close
    
    signal.signal(signal.SIGINT, cchandler)
    wlist = []
    xlist = []

    if sys.argv[1] == "-c":
        rlist = [sys.stdin, s]
        s.connect((sys.argv[2], 9999))
        while(1):
            (rready, wready, xready) = select.select(rlist, wlist, xlist)
            for rfile in rready:
                if rfile is sys.stdin:
                    s.send(sys.stdin.readline())
          #          print sys.stdin.readline(), "123"
                else:
                    data = s.recv(1024)
                    sys.stdout.write(data)
            
    elif sys.argv[1] == "-s":
        s.bind((sys.argv[2], 9999))
        s.listen(1)
        conn, addr = s.accept()
        rlist = [conn, sys.stdin]
        print 'Connected by', addr
        while(1):
             (rready, wready, xready) = select.select(rlist, wlist, xlist)
             for rfile in rready:
                if rfile is sys.stdin:
                    conn.send(sys.stdin.readline())
                 #   print sys.stdin.readline()
                else:
                    data = conn.recv(1024)
                    sys.stdout.write(data)  
        

       

            

