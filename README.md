tablefill
=========

Automatically update LaTeX, LyX, and Markdown tables and numbers using a placeholder system.

Quickstart
----------

```bash
pip install git+https://github.com/mcaceresb/tablefill
tablefill --help
```

See the [getting started](https://mcaceresb.github.io/tablefill/getting-started.html) section of the documentation for an example in LaTeX of how to use this system.

Documentation
-------------

`tablefill` is a program that uses a generic placeholder system to update LaTeX, LyX, and Markdown documents.  While it's original use was to fill in tables (hence the name) placeholders are replaced anywhere in a table environment or anywhere within commented-out `tablefill` tags. Hence any text or numbers anywhere in the document can be updated using this system.

The name and idea for this workflow comes from [GSLab](https://github.com/gslab-econ/gslab_python).  This version was written to update LaTeX files in the same fashion, and later expanded to include Markdown and [several features](#features).

- [Getting Started](https://mcaceresb.github.io/tablefill/getting-started.html) gives a basic example of how the system works, and guides the user through updating a template using Stata-generated input files (this example can be replicated with any programming language, however, not just Stata).

- The usage section details the [input](https://mcaceresb.github.io/tablefill/usage/02matrix-input.html) required by `tablefill`, the format of the [placeholders](https://mcaceresb.github.io/tablefill/usage/03placeholders.html) that are allowed, and documents the `tablefill` usage options.

- Last, we provide examples of how to generate the type of input required by `tablefill` in the [sample programs](https://mcaceresb.github.io/tablefill/sample-programs.html) page.

Background
----------

When I came across [the original `tablefill`](https://github.com/gslab-econ/gslab_python/blob/master/gslab_fill/tablefill.py) it could only update LyX files with Stata output (though I believe LaTeX support has been added in the time since). The idea was to expand the system to work with LaTeX, but over time I re-wrote the code base and added [several features](#features), including Markdown support.  For compatibility with scripts using GSLab's `tablefill`, the script can be run from the command line or imported as a python module.  The workflow is as follows:

1. Create a LaTeX, LyX, or Markdown document using placeholders. Label or tag each table appropriately.

2. Print a matrix (or any array) into a tab-delimited text file. The output is preceded by the label or tag of the table you want to fill, and the matrix or array entries correspond to the placeholders.

3. Run `tablefill` to update the placeholders in the template document.

Installation
------------

```bash
pip install git+https://github.com/mcaceresb/tablefill
tablefill --help
```

This was created specifically to run in a server that only had Python 2.6 available. The function should be compatible with Python 2.6, Python 2.7, and Python 3.X without requiring the installation of any additional packages (the `--numpy-syntax` option is available if the function can successfully run `import numpy`; however, `numpy` is not required for normal use).

Features
--------

As mentioned above, the original idea for tablefill comes from [GSLab](https://github.com/gslab-econ). However, this version has enough distinct features to merit calling itself a separate program. These include:

- Ability to fill LaTeX and Markdown templates
    - Placeholders can also be placed between commented-out tablefill tags, so updating is not restricted to literal tables.
    - There can be several placeholders in one line (however, there must be at most one table line per code line).
    - Labels in LaTeX can be anywhere in the table environment.
    - Placeholders can be either `#` or `\#` (note the former is a special character in LaTeX so while the filled output will compile, the template will not).
    - Can have several matches of the pattern in the same line.
    - LaTeX tables can be filled inside Markdown documents.
    - The user can choose whether or not to fill in placeholders in commented-out lines.

- Several error and consistency checks
    - Checks inputs are correct (names and type)
    - Checks if input files exist
    - Soft warning when placeholder outside proper environment
    - Soft warning when placeholder in environment with no label
    - Soft warning when placeholder in environment with unmatched label
    - Soft warning when more placeholders than table entries

- Several new placeholder types:
    - Arbitrary python formatting via `#{.*}#` (note that in python 2.6 this must be `#{0:.*}#`).
    - `#*#` interprets the input as a p-value and replaces it with significance symbols (default is `* 0.1, **0.05, ***0.01`; however, anything that LaTeX, LyX, or Markdown will compile can be passed).
    - Modifier `%` reads the input as percentage (multiplies by 100).
    - Modifier `||` outputs the absolute value of the input.

- The input tables can be generated by any program as long as they write missing values as blank, a dot, NA, or NaN.

- `tablefill` can be run from the command line directly _or_ imported to a python script.

- Basic compilation support via the `--compile` and/or `--bibtex` flags.

- XML-based ad-hoc table combination engine.
    - The user can combine arbitrary entries of existing tables in the provided templates to create new tables. This is useful if generating new tables is costly. It is also useful to quote table statistics in a summary elsewhere in the text (the LaTeX engine can parse the placeholders as long as they are in a table environment, which can be regular text).

Contributors
------------

- [Kyle Barron](https://github.com/kylebarron) has made several additions and improvements to this projects.
- The idea behind this system came from from [GSLab](https://github.com/gslab-econ)'s [tablefill](https://github.com/gslab-econ/gslab_python/blob/master/gslab_fill/tablefill.py).

License
-------

MIT
