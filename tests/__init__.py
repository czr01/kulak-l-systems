import sys
from os.path import dirname, abspath

d = dirname(dirname(abspath(__file__))) + "/PyLRender"
sys.path.append(d)