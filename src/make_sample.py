import random

import sys

print("id;natural1;natural2;float1;integer1")
size = 1000*1000*100
if len(sys.argv)>1:
    size=int(sys.argv[1])


for i in range(0,size):
    line=str(i) +";"
    line=line + str(random.randint(0,1000)) + ";"
    line = line + str(random.randint(0, 10000000)) + ";"
    line = line + str(random.uniform(-10,30)) + ";"
    line += str(random.randint(-1000, 1000))

    print(line)

