Sample Programs
===============

Here we illustrate how to export a matrix into the preferred format of
`tablefill` in several programming languages.

R
-

[Download script `saveTable.R`](programs/saveTable.R)

```R
saveTable <- function (outfile, tag, outmatrix) {
    cat(tag,
        sep    = "\n",
        file   = outfile,
        append = TRUE)

    write.table(outmatrix,
                file      = outfile,
                sep       = "\t",
                append    = TRUE,
                quote     = FALSE,
                col.names = FALSE,
                row.names = FALSE)
}

saveTable("test.txt", "<tab:testR1>", matrix(1:4, 2, 2))
saveTable("test.txt", "<tab:testR2>", matrix(runif(4), 2, 2))
```

Stata
-----

[Download script `saveTable.ado`](programs/saveTable.ado)

```stata
capture program drop saveTable
program saveTable
    version 13
    syntax using/, tag(str) OUTMatrix(name) [fmt(str)]
    mata: saveTable()
end

capture mata: mata drop saveTable()
mata:
void function saveTable()
{
    real scalar i, j, fh
    real matrix outmatrix
    outmatrix = st_matrix(st_local("outmatrix"))
    fmt = st_local("fmt")
    if ( fmt == "" ) {
        fmt = "%21.9f"
    }
    fmt = "\t" + fmt
    fh  = fopen(st_local("using"), "a")
    fwrite(fh, sprintf("%s\n", st_local("tag")))
    for(i = 1; i <= rows(outmatrix); i++) {
        for(j = 1; j <= cols(outmatrix); j++) {
            fwrite(fh, sprintf(fmt, outmatrix[i, j]))
        }
        fwrite(fh, sprintf("\n"))
    }
    fclose(fh)
}
end

matrix test = (1, 2 \ 3, 4)
saveTable using "test.txt", tag("<tab:testStata1>") outmatrix(test)

mata: st_matrix("test", runiform(2, 2))
saveTable using "test.txt", tag("<tab:testStata2>") outmat(test)
```

Python
------

[Download script `saveTable.py`](programs/saveTable.py)

```python
from os import linesep
import numpy as np


def saveTable(outfile, tag, outmatrix):
    with open(outfile, "a") as fh:
        fh.write(tag)
        fh.write(linesep)
        np.savetxt(fh, outmatrix, delimiter = '\t')

saveTable("test.txt", "<tab:testPython1>", np.arange(4).reshape(2, 2))
saveTable("test.txt", "<tab:testPython2>", np.random.uniform(size = (2, 2)))
```

Julia
-----

[Download script `saveTable.jl`](programs/saveTable.jl)

```julia
using DelimitedFiles

function saveTable(outfile, tag, outmatrix)
    open(outfile, "a") do file
        write(file, "$(tag)\n")
        writedlm(file, outmatrix, "\t")
    end
end

saveTable("test.txt", "<tab:testJulia1>", [[1 2]; [3 4]])
saveTable("test.txt", "<tab:testJulia2>", rand(2, 2))
```


Matlab
------

Save [`saveTable.m`](programs/saveTable.m) with

```matlab
function saveTable(outfile, tag, outmatrix)
    fh = fopen(outfile, "a");
    fprintf(fh, '%s\n', tag);
    fclose(fh);
    dlmwrite(outfile, outmatrix, '-append', 'delimiter', '\t');
end
```

Then run

```matlab
saveTable("test.txt", "<tab:testMatlab1>", [[1 2]; [3 4]])
saveTable("test.txt", "<tab:testMatlab2>", rand(2, 2))
```
