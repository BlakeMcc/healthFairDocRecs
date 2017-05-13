import random
import os
BASE = os.path.dirname(os.path.abspath(__file__))

with open(os.path.join(BASE,'words.txt'), 'r') as f:
    SLUG_WORDS = f.read().splitlines()

