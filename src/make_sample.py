import random
print("id;natural1;natural2;float1;integer1")

for i in range(1,1000000):
    line=str() + str(i) +";"
    line=line + str(random.randint(0,1000)) + ";"
    line = line + str(random.randint(0, 10000000)) + ";"
    line = line + str(random.uniform(-10,30)) + ";"
    line = line + str(random.randint(-1000, 1000))
    print(line)

