tablefill
=========

Automatically update LaTeX, LyX, and Markdown tables using a placeholder system.

Quickstart
----------

```bash
pip install git+https://github.com/mcaceresb/tablefill
tablefill --help
```

Documentation
-------------

`tablefill` is a program that uses a generic placeholder system to
fill LaTeX, LyX, and Markdown tables using formatted output from any
programming language.

- [Getting Started](https://mcaceresb.github.io/tablefill/getting-started.html) gives a a basic example of
  how the system works.

- [Sample Workflow](https://mcaceresb.github.io/tablefill/sample-workflow.html) guides the user on how to
  automate LaTeX table updating.

- The usage section details the [input](https://mcaceresb.github.io/tablefill/usage/02matrix-input.html)
  required by `tablefill`, the format of the [placeholders](https://mcaceresb.github.io/tablefill/usage/03placeholders.html)
  that are allowed, and documents the `tablefill` usage options.

- Last, we provide examples of how to generate the type of input
  required by `tablefill` in the [sample programs](https://mcaceresb.github.io/tablefill/sample-programs.html)
  page.

Background
----------

The original idea for this workflow comes from [GSLab](https://github.com/gslab-econ).
[The original tablefill](https://github.com/gslab-econ/gslab_python/blob/master/gslab_fill/tablefill.py)
in particular was made to automatically update LyX files with Stata output.
However, I expanded this system to work with LaTeX and added several features.
The workflow is as follows:

1. Create a LaTeX, LyX, or Markdown document using placeholders in your tables.
   Label or tab each table appropriately.

2. Print a matrix (or any array) to a delimited text file. The output
   is preceded by the tag of the table you want to fill, and the matrix
   or array's entries correspond to the placeholders.

3. Run `tablefill` to update the placeholders in the template document.

The original tablefill only worked with LyX and assumed the tables came
from Stata (or Matlab). This project initially aimed to extend the system
to work with LaTeX, but over time it re-wrote the entire code base and
added several features:

- The input tables can be generated by any program as long as they
  write missing values as blank, a dot, or NA (the "." and "NA" are
  exceptions made for Stata and R).

- The format is to print a tag on the line prior to the table,
  `<tab:table_label>`, and then print a tab-delimited table (typically
  a matrix, but it can be any flat array and have rows or varying length).

- For compatibility with scripts using GSLab's tablefill, the script can
  be run from the command line or imported as a python module.

- Several soft-warnings and error checks were added.

Installation
------------

```bash
pip install git+https://github.com/mcaceresb/tablefill
tablefill --help
```

This was created specifically to run in a server that only had Python
2.6 available. The function should be compatible with Python 2.6, Python
2.7, and Python 3.X without requiring the installation of any additional
packages (the `--numpy-syntax` option is available if the function can
successfully run `import numpy`; however, `numpy` is not required for
normal use).


Features
--------

- Several error and consistency checks
    - Checks inputs are correct (names and type)
    - Checks if input files exist
    - Soft warning when placeholder outside proper environment
    - Soft warning when placeholder in environment with no label
    - Soft warning when placeholder in environment with unmatched label
    - Soft warning when more placeholders than table entries
- Can fill LaTeX templates
    - There can be several placeholders in one line
    - However, there must be at most one table line per code line
    - Environment must be a table environment, not tabular
    - Placeholders can be either `#` or `\#` (note the former is a
      special character in LaTeX so while the filled output will
      compile, the template will not).
    - Labels in LaTeX can be anywhere in the table environment
    - Can have several matches of the pattern in the same line
- Can be run from the command line directly or imported to a python script.
- Can choose whether to fill commented out lines.
- Adds placeholder modifiers % and ||; added placeholder type `#*#`
    - Adding the % before closing a placeholder causes tablefill to
      interpret it as a percentage (i.e. multiplies the number by 100).
    - Enclosing the contents of a placeholder in pipes, `||`, causes
      tablefill to take the absolute value of the input.
    - The placeholder `#*#` causes the entry to be interpreted as a
      p-value. The user can specify the p-value levels and symbols
      to replace them with (anything that LaTeX will compile can be
      passed). Default is `* 0.1, **0.05, ***0.01`.
- Basic LaTeX compilation via the `--compile` and/or `--bibtex` flags.
- Added XML-based ad-hoc table combination engine.
    - The user can combine arbitrary entries of existing tables in
      the provided templates to create new tables. This is useful if
      generating new tables is costly. It is also useful to quote
      table statistics in a summary elsewhere in the text (the LaTeX
      engine can parse the placeholders as long as they are in a table
      environment, which can be regular text).

Contributors
------------

- The original idea for tablefill comes from [GSLab](https://github.com/gslab-econ)'s [tablefill](https://github.com/gslab-econ/gslab_python/blob/master/gslab_fill/tablefill.py).
- [Kyle Barron](https://github.com/kylebarron) made the project into a pip-installable package.

License
-------

MIT
