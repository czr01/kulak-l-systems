import sys
from os.path import dirname, abspath

d = dirname(dirname(abspath(__file__))) + "/pylrender"
print(d)
sys.path.append(d)