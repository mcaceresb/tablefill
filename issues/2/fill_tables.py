#! /usr/bin/env python2

import glob
import os
from tablefill import tablefill

filled_names = glob.glob('filled/*.tex')
for i in filled_names:
    os.remove(i)

# Fill all latex tables in template/ except master.tex
names = [os.path.basename(x) for x in glob.glob('template/*.tex')]
for name in names:
    tablefill(template = os.path.join("template", name),
              output   = os.path.join("filled", name),
              fillc    = True,
              input    = "tables1.txt tables2.txt tables3.txt")
