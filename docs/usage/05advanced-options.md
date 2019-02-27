Advanced Options
================

!!! info "Warning"
    This page is under construction

`tablefill` can be used both as a command line program and a python module:

Command-line use
----------------

```
tablefill [-h] [-v] [FLAGS] [-i [INPUT [INPUT ...]]] [-o OUTPUT]
          [--pvals [PVALS [PVALS ...]]] [--stars [STARS [STARS ...]]]
          [--xml-tables [INPUT [INPUT ...]]] [-t {auto,lyx,tex}]
          TEMPLATE

positional arguments:
  TEMPLATE              Code template

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Show current version
  -i [INPUT [INPUT ...]], --input [INPUT [INPUT ...]]
                        Input files with tables (default: TEMPLATE_table)
  -o OUTPUT, --output OUTPUT
                        Processed template file (default: TEMPLATE_filled)
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

exit, exit_msg = tablefill(template,     # required
                           input,        # required
                           output,       # required
                           filetype,     # default: True
                           verbose,      # default: 'auto'
                           silent,       # default: [0.1, 0.05, 0.01]
                           pvals,        # default: ['*', '**', '***']
                           stars,        # default: False
                           fillc,        # default: False
                           numpy_syntax, # default: False
                           use_floats,   # default: False
                           ignore_xml,   # default: False
                           xml_tables)   # default: None
```

### Required Input

```
template : str
    Name of user-written document to use as basis for update

input : str
    Space-separated list of files with tables to be used in update.

output : str
    Filled template to be produced.
```

### Optional Input

```
verbose : bool
    print a lot of info

silent : bool
    try to print nothing at all

filetype : str
    auto, lyx, or tex

pvals : list
    p-value thresholds

stars : list
    symbols to replace p-values with

fillc : bool
    whether to fill in commented out lines

xml_tables : str or list
    file or list of files with XML combination tables

numpy_syntax : bool
    use numpy syntax for XML engine

use_floats : bool
    force floats when passing arguments to XML engine

ignore_xml : bool
    whether to ignore XML in commented out lines
```

### Output

```
exit : str
    One of SUCCESS, WARNING, ERROR

exit_msg : str
    Details on the exit status
```

### Example

```
exit, exit_msg = tablefill(template = 'template_file',
                           input    = 'input_file(s)',
                           output   = 'output_file')
```
