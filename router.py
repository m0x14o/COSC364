import sys
import socket
import select
import time
import random

HOST = "127.0.0.1"

class Router:
    def __init__(self, routerid, inputports, outputports):
        self.id = routerid
        self.input_ports = inputports
        self.output_ports = outputports
        self.in_sock = []
        self.table = {}

    def print_table(self):
        print("ID: " + str(self.id))
        print("Dest|Cost|First|Timeout")
        for entry in sorted(self.table.keys()):
            print(" {:>2} | {:>2} | {:>3} | {:>5} ".format(entry, self.table[entry][0], self.table[entry][1], str(time.time()-float(self.table[entry][2]))[:6]))
        

    def create_socks(self):
        for port in self.input_ports:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.bind((HOST, port))
            self.in_sock.append(s)
        return self.in_sock

    def listen(self, timeout):
        r, w, e = select.select(self.in_sock, [], [], timeout)
        if r != []:
            recvs = []
            for s in r:
                packet = s.recvfrom(1024)
                recvs.append(packet[0].decode(encoding = 'utf-8'))
            return recvs


    def update_table(self, message):
        lines = message.split('\n')
        #print(lines)
        for line in lines:
            line = line.split('-')
            #print(line)
            if (line[0] == "2") and (line[1] == "2.0"):
                source = int(line[2])
                timer = line[5]
                data = self.output_ports[source]
                self.table[source]=(int(line[4]), source, float(timer))
            elif (line[0] != ''):
                dst = int(line[0])
                #print(line)
                if (dst != self.id):
                    metric = int(line[1]) + data[1]
                    entry = self.table.get(dst)
                    if (entry == None):
                        if (int(line[1]) < 16):
                            self.table[dst]=(int(line[1]), source, float(timer))
                    elif (int(entry[1]) == source):
                        if (metric > 16):
                            metric = 16
                        self.table[dst]=(metric, source, float(timer))
                    elif (metric < int(entry[0])):
                        self.table[dst]=(int(line[1]), source, float(timer))
        self.print_table()
        return None


    def send_msg(self, dest, data):
        cmd = "2"
        vrs = "2.0"
        src = str(self.id)
        dst = str(dest)
        mtc = str(self.output_ports[dest][1])
        timer = str(time.time())#[:4]
        msg = cmd + '-' + vrs + '-' + src + '-' + dst + '-' + mtc + '-' + timer + '\n'
        for entry in self.table.keys():
            metric = self.table[entry][0]
            if (self.table[entry][1] == dest):
                metric = 16
            msg += str(entry) + '-' + str(metric) + '\n'

        self.in_sock[0].sendto(msg.encode('utf-8'),(HOST,self.output_ports[dest][0]))
        #print(msg)

        
    def multicast(self):
        for dest in self.output_ports.keys():
            self.send_msg(dest, self.output_ports[dest])

    def refresh_table(self, expiry):
        for entry in self.table.copy():
            if ((time.time()-float(self.table[entry][2])) > expiry):
                self.table.pop(entry)
                #self.table[entry][0] = 16
                self.multicast()
                self.print_table()
        print()
            






def main():
    config_data = []
    router_id = 0
    input_ports = set()
    output_ports = {}
    t = time.time()
    period = 6
    entry_timeout = 6 * 6 



    config = open(sys.argv[1],'r')
    for line in config.readlines():
        var = line.split(',')
        config_data.append(var)
    router_id = int(config_data[0][1])
    for i in range(1,len(config_data[1])):
        if (int(config_data[1][i]) >= 1024) and (int(config_data[1][i]) <= 64000):
                input_ports.add(int(config_data[1][i])) 
    for i in range(1,len(config_data[2])):
        temp_s = config_data[2][i]
        temp_s = temp_s.split('-')
        output_ports[int(temp_s[2])] = (int(temp_s[0]),int(temp_s[1]))
    

    #print(router_id,input_ports,output_ports)
    router = Router(router_id, input_ports, output_ports)
    router.create_socks()
    router.print_table()
    router.multicast()

    while 1:
        if ((time.time()-t) > period):
            period = period + 2 * (random.random() - 0.5)
            t = time.time()
            router.multicast()
            router.print_table()
            print()
        packets = router.listen(2)
        if packets:
            for packet in packets:
                router.update_table(packet)
        for entry in router.table.copy():
            if (time.time()-float(router.table[entry][2]) > entry_timeout):
                router.refresh_table(entry_timeout)



if __name__=="__main__":
    if len(sys.argv) == 2:
        main()
    else:
        print("wrong format!")
