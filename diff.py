#!/usr/bin/env python3

import subprocess
from difflib import SequenceMatcher

files = [
    "bernstein_vazirani.py",
    "deutsch_jozsa.py",
    "grover.py",
    "simon.py"
]

names = ['bv', 'dj', 'gr', 'si']

for i, file1 in enumerate(files):
    f1 = open(file1).read().replace('\n', '')
    for j in range(i, 4):
        if i != j:
            file2 = files[j]
            f2 = open(file2).read().replace('\n', '')
            ratio = SequenceMatcher(None, f1, f2).quick_ratio()
            print(f"{names[i]}/{names[j]} : {ratio*100:.2f}%")

"""
awk 'a[$0]++' file1 file2 | sed -e '/^\s*$/d' | wc -l

bv/dj: 86
bv/gr: 74
bv/si: 56
dj/gr: 74
dj/si: 55
gr/si: 66
"""
