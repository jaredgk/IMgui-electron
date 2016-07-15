import sys
import random
import os


print os.getcwd()
f = open('t.txt','w')


f.write(str(random.randint(0,10000)))
