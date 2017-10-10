import sys
import socket
import time

des = sys.argv[1]
serv = []
port = []
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
yes = 0
good = 1
print "Scanning ", des, "\n", "------------------------"
start = time.time()
for i in range(65536):
  #  print i 
    
    if i % 15 != 0:
        good = s.connect_ex((des, i))
   # print 2 * i
    if good == 0:
        port.append(i)
        serv.append(socket.getservbyport(i))

good = 1
for i in range(65536):
  #  print i
    if i % 15 == 0:
        good = s.connect_ex((des, i))
    if good == 0:
        port.append(i)
        serv.append(socket.getservbyport(i))

count = 0
for i in range(65536):
    if i % 4096 == 0:
        sys.stdout.write("\n" + str(i) + "\t")
    if count < len(port) and i == port[count]:
        count = count + 1
        yes = 1
    
    if yes == 1 and i % 256 == 0:
        sys.stdout.write("!")
        yes = 0 
    if i % 256 == 0:
        sys.stdout.write(".")

end = time.time()
print "\n\nScan Finished!"
print "------------------------"
print len(port), "\t\tports found"
print end - start, "\tseconds elapsed"
print 65536 / (end - start), "\tports per second"
print "Open Ports: "
print "------------------------"
for i in range(len(port)):
    print port[i], ":\t", serv[i] 

print "\nTerminating Normally"


   




