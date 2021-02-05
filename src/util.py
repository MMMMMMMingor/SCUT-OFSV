import time
import numpy as np
import pandas as pd

OKGREEN = '\033[92m'
ENDC = '\033[0m'


class my_timer():
    def __init__(self, str):
        print(str)

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print(f"    cost: {time.time() - self.start} seconds")
