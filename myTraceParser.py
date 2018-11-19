#! /usr/bin/python3
import subprocess
import networkx as nx
import matplotlib.pyplot as plt
import sys

# Parse output of traceroute and visualize the path from source to destination


# define each hop in traceroute path
# each hop has a list of 3 probe
class Hop():
    # note: constructor, pass instance of class as argument, like 'this' in java
    def __init__(self, index, name = ''):
        self.index = index # Hop count, starting at 1
        self.probe_list = [] # Series of Probe instances
        self.name = ''

    def add_probe(self, probe):
        self.probe_list.append(probe)

    def set_name(self, name):
        self.name = name


# Merge the round trip time of 3 probe to represent a hop
class Avg_Hop():
    def __init__(self, index, name, ip, avg_rtt):
        self.index = index # Hop count, starting at 1
        self.ip = ip
        self.name = name
        self.avg_rtt = avg_rtt


# each probe has ip = ip addr that it is sent to
# same for name
class Probe():
    def __init__(self, name = None, ip = None, rtt = None):
        self.name = name
        self.ip = ip
        self.rtt = rtt # rtt: round trip time

    def __str__(self):
        return('Probe: name = ' + self.name + ' ip = ' + self.ip + ' rtt = ' + str(float(self.rtt)))

    def set_name(self, name):
        self.name = name

    def set_ip(self, ip):
        self.ip = ip

    def set_rtt(self, rtt):
        self.rtt = rtt

    # copy a probe, in case same probe is sent to the hop
    def copy(self):
        copy = Probe()
        copy.ip = self.ip
        copy.name = self.name
        return copy


# Run the traceroute command line and parse the result
output = subprocess.run(["traceroute", sys.argv[1]], stdout=subprocess.PIPE)
output = output.stdout.decode('utf-8')
output = output.strip()
output = output.split('\n')
for line in output:
    print(line)

print("------------------------")
hop_list = []  # list of hop
hop_count = 0    # number of hops
dest_name = ''     # destination name
dest_ip = ''    # destination ip
for line in output:
    word_list = line.split(' ')
    word_list = [x for x in word_list if x != '']
    if line.lower().startswith('traceroute'):
        dest_name = word_list[2]
        dest_ip = word_list[3]
        print('Dest name = ', dest_name)
        print('Dest ip = ', dest_ip.strip('(').strip(',').strip(')'))
    elif (word_list[1] == '*'):
        hop_count = hop_count + 1
        new_hop = Hop(hop_count)
        hop_list.append(new_hop)
    else:
        hop_count = hop_count + 1
        new_hop = Hop(hop_count)
        i = 1
        check_new_path = True
        current_probe = Probe()
        while (i < len(word_list)):
            # probe name and ip
            if check_new_path:
                current_probe.set_name(word_list[i])
                current_probe.set_ip(word_list[i + 1].strip('(').strip(',').strip(')'))
                new_probe = current_probe.copy()
                new_probe.set_rtt(round(float(word_list[i + 2]), 3))
                new_hop.add_probe(new_probe)
                if ((i + 5) < len(word_list)):
                    if (word_list[i + 5] != 'ms'):
                        check_new_path = True
                    else:
                        check_new_path = False
                i = i + 4
            else:
                new_probe = current_probe.copy()
                new_probe.set_rtt(round(float(word_list[i]), 3))
                new_hop.add_probe(new_probe)
                if ((i + 3) < len(word_list)):
                    if (word_list[i + 3] != 'ms'):
                        check_new_path = True
                    else:
                        check_new_path = False
                i = i + 2
        hop_list.append(new_hop)


print("------------------")

# Merge round trip time statistic of probes for each hop
for h in hop_list:
    print("HOP " + str(h.index))
    print("length = ", len(h.probe_list))
    # merge
    if (len(h.probe_list) > 0):
        # 0 = 1 = 2
        if (h.probe_list[0].name == h.probe_list[1].name) and (h.probe_list[1].name == h.probe_list[2].name):
            avg_rtt = (h.probe_list[0].rtt + h.probe_list[1].rtt + h.probe_list[2].rtt) / 3
            h.probe_list[0].set_rtt(round(float(avg_rtt), 3))
            h.probe_list.pop(1)
            h.probe_list.pop(1)
        # 0 = 1 != 2
        elif (h.probe_list[0].name == h.probe_list[1].name) and (h.probe_list[1].name != h.probe_list[2].name):
            avg_rtt = (h.probe_list[0].rtt + h.probe_list[1].rtt) / 2
            h.probe_list[0].set_rtt(round(float(avg_rtt), 3))
            h.probe_list.pop(1)
        # 0 = 2 != 1
        elif (h.probe_list[0].name == h.probe_list[2].name) and (h.probe_list[1].name != h.probe_list[2].name):
            avg_rtt = (h.probe_list[0].rtt + h.probe_list[2].rtt) / 2
            h.probe_list[0].set_rtt(round(float(avg_rtt), 3))
            h.probe_list.pop(2)
        # 0 != 2 = 1
        elif (h.probe_list[1].name == h.probe_list[2].name) and (h.probe_list[1].name != h.probe_list[0].name):
            avg_rtt = (h.probe_list[1].rtt + h.probe_list[2].rtt) / 2
            h.probe_list[1].set_rtt(round(float(avg_rtt), 3))
            h.probe_list.pop(2)

        for i in h.probe_list:
            print(i)
    else:
        h.set_name('* * * NO DATA' + "_" + str(h.index))
        print(h.name)
    print("------------------")


# Draw the path from source to destination
# edges are  latency between nodes
source = Hop(0)
source.set_name('SOURCE')
hop_list.insert(0, source)

# Initilize edges with latency between each hop
edges = []
edge_labels  = {}
for i in range(len(hop_list) - 1):
    if (len(hop_list[i + 1].probe_list) == 0):
        for p1 in hop_list[i].probe_list:
            edges.append([p1.name, hop_list[i + 1].name])
    elif (len(hop_list[i].probe_list) == 0):
        for p1 in hop_list[i + 1].probe_list:
            edges.append([hop_list[i].name, p1.name])
    elif (i == len(hop_list) - 2):
        for p1 in hop_list[i].probe_list:
            for p2 in hop_list[i + 1].probe_list:
                edges.append([p1.name, 'DESTINATION: ' + sys.argv[1]])
                edge_labels[(p1.name, 'DESTINATION: ' + sys.argv[1])] = str(round(p2.rtt - p1.rtt, 3))
    else:
        for p1 in hop_list[i].probe_list:
            for p2 in hop_list[i + 1].probe_list:
                edges.append([p1.name, p2.name])
                edge_labels[(p1.name, p2.name)] = str(round(p2.rtt - p1.rtt, 3))
                # print("EDGE = ", edge_labels)

# Draw
G = nx.Graph()
G.add_edges_from(edges)
pos = nx.spring_layout(G)
plt.figure()
nx.draw(G, pos, edge_color='black', width = 1, linewidths = 1, node_size=500, node_color='pink', alpha=0.9, labels={node: node for node in G.nodes()})
nx.draw_networkx_edge_labels(G, pos, edge_labels, font_color='red')
plt.axis('off')
plt.show()
