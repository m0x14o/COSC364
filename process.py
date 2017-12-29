#!/usr/bin/env python3

import sys


# Get filename and open file for reading
if (len(sys.argv) > 1):
    filename = sys.argv[1]
else:
    filename = input("File?: ")
f = open(filename, 'r')



demandflows = []
transit_loads = {}
max_cap = 0
nonzero_cap = 0
time = 0

start = False
l = f.readline()
while (l != ''):
    if (not start):
        if l.startswith("Variable Name"):
            start = True
    elif l.startswith("real"): # run time "user"
        time = l.strip('s\n').split('m')[-1]
    elif l.startswith('r'): # Objective value - r
        r = l.strip('\n').split(' ')[-1]
    elif l.startswith('x'): # Flow volume for path - Xikj
        l = l.strip('\n').split(' ')
        demandflows.append((l[0], float(l[-1])))
    elif l.startswith('u'): # Decision variable - Uikj
        pass
    elif (l.startswith('c') or l.startswith('d')): # Link capacity - Cik or Dkj
        cap = float(l.strip('\n').split(' ')[-1])
        max_cap = max(cap, max_cap)
        nonzero_cap += 1
    elif l.startswith("all"): # Has zero capacity links
        pass
    elif l.startswith("CPLEX>"): # End of output
        pass
    l = f.readline()
    
if (not start): # No solution was found
    print("No solution was found.")
else:
    for demandflow in demandflows:
        Tnode = demandflow[0][2]
        flow = demandflow[1]
        load = transit_loads.get(Tnode)
        if (load == None):
            transit_loads.update({Tnode:flow})
        else:
            transit_loads.update({Tnode:load + flow})

    #print(transit_loads)
    for load in sorted(transit_loads.keys()):
        print("Load {}: {}".format(load, transit_loads.get(load)))
    print("Maximum capacity link: {}".format(max_cap))
    print("Non-zero capacity links: {}".format(nonzero_cap))
    print("Time: {}".format(time))
