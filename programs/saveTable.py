# saveTable("test.txt", "<tab:testPython1>", np.arange(4).reshape(2, 2))
# saveTable("test.txt", "<tab:testPython2>", np.random.uniform(size = (2, 2)))

from os import linesep
import numpy as np


def saveTable(outfile, tag, outmatrix):
    with open(outfile, "a") as fh:
        fh.write(tag)
        fh.write(linesep)
        np.savetxt(fh, outmatrix, delimiter = '\t')
