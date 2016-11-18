import random
import numpy.random as rdm
import sys

#print header of the file
print("id;natural1;natural2;float1;integer1")

#set row-count
size = 1000*1000*10
if len(sys.argv)>1:
    size=int(sys.argv[1])

#set size of randomly generated Chunks
CHUNK_SIZE=10000
nat1=list()
nat2=list()
int1=list()
float1=list()

for i in range(0,size):
    if i%CHUNK_SIZE == 0:
        nat1 = rdm.random_integers(0, 1000, size)
        nat2 = rdm.random_integers(0,10*1000*1000,CHUNK_SIZE)
        int1 = rdm.random_integers(-1000, 1000, CHUNK_SIZE)
        float1=-10 + 40*rdm.random_sample(CHUNK_SIZE)
    print(i,nat1[i%CHUNK_SIZE], nat2[i%CHUNK_SIZE], float1[i%CHUNK_SIZE], int1[i%CHUNK_SIZE],sep=";")
#    line=';'.join([str(i), str(nat1[i%CHUNK_SIZE]), str(nat2[i%CHUNK_SIZE]), str(float1[i%CHUNK_SIZE]), str(int1[i%CHUNK_SIZE])])


 #   print(line)

