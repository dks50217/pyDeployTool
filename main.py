from pydeploytool.control.ctr_main import Ctr_Main
import multiprocessing
import sys

if __name__ == '__main__':
    multiprocessing.freeze_support()
    ctrMain = Ctr_Main()
    sys.exit()