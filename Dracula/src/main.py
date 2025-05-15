import os
import sys

# 将当前目录添加到库路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))


import xtquantai

if __name__ == "__main__":
    xtquantai.server.run_server()
