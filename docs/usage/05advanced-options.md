Advanced Options
================

!!! info "Warning"
    This page is under construction

`tablefill` can be used both as a command line program and a python module:

Command-line use
----------------

```c
tablefill [-h] [-v] [FLAGS] [-i [INPUT [INPUT ...]]] [-o OUTPUT]
          [--pvals [PVALS [PVALS ...]]] [--stars [STARS [STARS ...]]]
          [--xml-tables [INPUT [INPUT ...]]] [-t {auto,lyx,tex}]
          TEMPLATE

Fill tagged tables in LaTeX and LyX files with external text tables

positional arguments:
  TEMPLATE              Code template

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Show current version
  -i [INPUT [INPUT ...]], --input [INPUT [INPUT ...]]
                        Input files with tables (default: INPUT_table)
  -o OUTPUT, --output OUTPUT
                        Processed template file (default: INPUT_filled)
  -t {auto,lyx,tex}, --type {auto,lyx,tex}
                        Template file type (default: auto)
  --pvals [PVALS [PVALS ...]]
                        Significance thresholds
  --stars [STARS [STARS ...]]
                        Stars for sig thresholds (enclose each entry in quotes)
  --xml-tables [INPUT [INPUT ...]]
                        Files with custom xml combinations.

flags:
  -f, --force           Name input/output automatically
  -c, --compile         Compile output
  -b, --bibtex          Run bibtex on .aux file and re-compile
  -fc, --fill-comments  Fill in commented out placeholders.
  --numpy-syntax        Numpy syntax for custom XML tables.
  --use-floats          Force floats when passing objects to custom XML python.
  --ignore-xml          Ignore XML in template comments.
  --verbose             Verbose printing (for debugging)
  --silent              Try to say nothing
```

Python use
----------

Options are analogous to their command-lien counterparts:

```python
from tablefill import tablefill

exit, exit_msg = tablefill(template,  # required
                           input,     # required
                           output,    # required
                           filetype,
                           verbose,
                           silent,
                           pvals,
                           stars,
                           fillc,
                           numpy_syntax,
                           use_floats,
                           ignore_xml,
                           xml_tables)
```
