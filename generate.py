#!/usr/bin/env python3

#
# Invocation:   $ python3 generate.py X Y Z > out.lp
#               $ ./generate.py X Y Z > out.lp
#
# Prints to standard out. Pipe into file to run in cplex.
#

import sys

def getXYZ():
    if (len(sys.argv) == 3):
        X, Y, Z = int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3])
    else:
        X = int(input("X?: "))
        Y = int(input("Y?: "))
        Z = int(input("Z?: "))
    return (X, Y, Z)



#### Printers ####

def printObjective():
    print("Minimize")
    print("    obj:    ", end='')
    print("r") # TODO

def printDVconstraints(x, y, z):
    # Demand Volume Constraints
    for i in range(1, x+1):
        for j in range(1, z+1):
            print("    ", end='')
            print("h{}{}:   ".format(i,j), end='')
            for k in range(1, y+1):
                e = (' + ', " = {}\n".format(i + j))[k == y]
                print("x{}{}{}".format(i,k,j), end=e)

def printBNconstraints(x, y, z, n):
    # Utilization Constraints
    for i in range(1, x+1):
        for j in range(1, z+1):
            print("    ", end='')
            print("u{}{}:   ".format(i,j), end='')
            for k in range(1, y+1):
                e = (' + ', " = {}\n".format(n))[k == y]
                print("u{}{}{}".format(i,k,j), end=e)

def printDFconstraints(x, y, z, n):
    # Demand Flow Constraints
    for i in range(1, x+1):
        for j in range(1, z+1):
            for k in range(1, y+1):
                l = "{}{}{}".format(i,k,j)
                print("    ", end='')
                print("df{}: {} x{} - {} u{} = 0".format(l,n,l,i+j,l))

def printSrcLCconstraints(x, y, z):
    for i in range(1, x+1):
        for k in range(1, y+1):
            print("    ", end='')
            print("cs{}{}:  ".format(i,k), end='')
            for j in range(1, z+1):
                e = (' + ', " - c{}{} = 0\n".format(i,k))[j == z]
                print("x{}{}{}".format(i,k,j), end=e)
            

def printDstLCconstraints(x, y, z):
    for j in range(1, z+1):
        for k in range(1, y+1):
            print("    ", end='')
            print("cd{}{}:  ".format(k,j), end='')
            for i in range(1, x+1):
                e = (' + ', " - d{}{} = 0\n".format(k,j))[i == x]
                print("x{}{}{}".format(i,k,j), end=e)
    
def printLCconstraints(x, y, z):
    printSrcLCconstraints(x,y,z)
    printDstLCconstraints(x,y,z)

def printXVconstraints(x, y, z):
    for k in range(1, y+1):
        print("    ", end='')
        print("r{}:    ".format(k), end='')
        for i in range(1, x+1):
            for j in range(1, z+1):
                e = (' + ', " - r <= 0\n")[i == x and j == z]
                print("x{}{}{}".format(i,k,j), end=e)

def printConstraints(x, y, z, n=3):
    print("Subject To")
    printDFconstraints(x,y,z,n)
    printLCconstraints(x,y,z)
    printXVconstraints(x,y,z)
    printDVconstraints(x,y,z)
    printBNconstraints(x,y,z,n)

def printBounds(x, y, z):
    # All links must be non-zero
    print("Bounds")
    for i in range(1, x+1):
        for j in range(1, z+1):
            for k in range(1, y+1):
                l = "{}{}{}".format(i,k,j)
                print("    x{} >= 0".format(l,l))
    for i in range(1, x+1):
        for k in range(1, y+1):
            print("    c{2}{3} >= 0".format(i,k,i,k))
    for j in range(1, z+1):
        for k in range(1, y+1):
            print("    d{2}{3} >= 0".format(k,j,k,j))
    print("    r >= 0")

def printBinaries(x, y, z):
    print("Binaries")
    for i in range(1, x+1):
        for k in range(1, y+1):
            print("    ", end='')
            for j in range(1, z+1):
                print("u{0}{1}{2}".format(i,k,j), end=' ')
            print()

def printEnd():
    print("End")

def printnodes(x,y,z):
    print("Source  X: {0}\nTransit Y: {1}\nDest    Z: {2}".format(X,Y,Z))


if (__name__ == "__main__"):
    X, Y, Z = getXYZ()
    
    if (len(sys.argv) < 3):
        printnodes(X,Y,Z)
        print("\n\n{0}{1}{2}.lp".format(X,Y,Z))

    printObjective()
    printConstraints(X,Y,Z)
    printBounds(X,Y,Z)
    printBinaries(X,Y,Z)
    printEnd()
    
    

