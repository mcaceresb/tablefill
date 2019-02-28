Getting Started
===============

!!! note "Note"
    This page illustrates the usage of `tablefill` with Stata.
    However, any programming language can produce output to be used by
    `tablefill`. See the [sample programs](sample-programs.md) section
    for details.

`tablefill` allows the user to update text and numbers in LaTeX,
LyX, and Markdown. Its main purpose is to aid the user in creating
reproducible reports that can be automatically updated.

Installation
------------

To install `tablefill`, run
```bash
pip install git+https://github.com/mcaceresb/tablefill
```

You can the use `tablefill` from the command-line via
```bash
tablefill -i input1.txt [input2.txt ...] -o output.tex template.tex
```

Or directly from python via
```python
from tablefill import tablefill

tablefill(
    input    = 'input1.txt input2.txt ...',
    output   = 'output.tex',
    template = 'template.tex'
)
```

If you do not wish to install `tablefill` system-wide, you can simply
download [`tablefill.py`](../tablefill/tablefill.py) and place it in
your project's folder. The above snippet will import it into python
correctly; however, the command-line call is would change to:

```bash
python paht/to/tablefill.py -i input1.txt [input2.txt ...] -o output.tex template.tex
```

Overview
--------

`tablefill` replaces named placeholders inside LaTeX, LyX, or Markdown documents. While the initial setup is more complex than, say, `estout` or `tabout`, `tablefill` is much more flexible. The workflow is typically as follows:

1. Create a LaTeX (or LyX or Markdown) document with placeholders that you want filled with numeric (or text) output.
    - Placeholders must be either inside a _labeled_ table or inside commented-out tablefill tags. More on this below.

2. Create a matrix of values that correspond to the table's placeholders.
    - Values will be read in order from the topmost row, left to right.

2. Export that matrix to a text file.
    - The matrix is preceded by a label that must match the label in your LaTeX document.
    - Numeric matrices are most common, but `tablefill` will also take text input.

4. `tablefill` replaces the placeholders with the matrix values.

The strength of this workflow is its flexibility. The user can format their documents however they see fit, without imposing any restrictions on where the values will be filled, as long as they are inside a labeled environment.  Optionally, the user can create a file with various mappings to allow multiple Stata matrices to be appended as a single LaTeX table, or different portions of a single matrix to be appended to several tables. This is covered in the [XML engine](usage/06xml-engine.md) section.

Basic Example in LaTeX
----------------------

### Template

First you need to create a file with a table that you want. This can be anything from summary statistics to regression results to paragraphs that refer to a specifics or text which need to be updated. Consider, for instance, [`template.tex`](usage/01basic/template.tex) below:

```latex
% template.tex
\documentclass{article}
\usepackage{booktabs}
\begin{document}

Tablefill will look for the label \verb'tab:example' inside
\verb'input.txt' and fill the table below:

\begin{table}
  \caption{Table caption (e.g. summary stats)}
  \label{tab:example}
  \begin{tabular}{p{4.25cm}crcc}
    Outcomes
    & N
    & Mean
    & (Std.)
    \\
    Outcomes \#\#\# & \#0,\# & \#1\# & (\#2\#) \\
    Outcomes \#\#\# & \#0,\# & \#1\# & (\#2\#) \\
    Outcomes \#\#\# & \#0,\# & \#1\# & (\#2\#) \\
    Outcomes \#\#\# & \#0,\# & \#1\# & (\#2\#) \\
    \multicolumn{4}{p{5cm}}{\footnotesize Footnotes!}
  \end{tabular}
\end{table}

However, placeholders do not need to be inside a table. You can also
have placeholders in the text:

% tablefill:start tab:paragraph

\begin{itemize}
    \item $N = \#0,\#$
    \item This is the \#\#\# sample.
\end{itemize}

Note \verb'% tablefill:start tab:paragraph' tells tablefill to start
looking for placeholders using the matrix labeled \verb'tab:paragraph'
in the input file. \verb'% tablefill:end' will tell tablefill to stop.

Tablefill provides several placeholders types (more on this below), but
advanced users can use any format allowed by python via \verb'{}'. For
example: \#{}\#. Here is another table, using python-style formatting:

% tablefill:end

\begin{table}
  \caption{Table caption (e.g. regression results)}
  \label{tab:anotherExample} % must match label in input.txt
  \begin{tabular}{p{4.25cm}c}
    Outcomes
    & Coef
    & (SE)
    \\
    Variable 1 & \#{:.1f}\# (\#{:.2f}\#)\#*\# \\
    Variable 2 & \#{:.1f}\# (\#{:.2f}\#)\#*\# \\
    Variable 3 & \#{:.1f}\# (\#{:.2f}\#)\#*\# \\
    \midrule
             N & \#{:,.0f}\# \\
    \multicolumn{4}{p{5cm}}{\footnotesize Footnotes!}
  \end{tabular}
\end{table}
\end{document}
```

### Placeholders

- Placeholders are of the form `###` or `\#\#\#` (the latter since LaTeX requires the `#` character to be escaped), with the middle placeholder varying depending on whether you wish to customize the printing format. The following constructs are available:

Placeholder Format  | Description
------------------- | -----------
`###`               | Replace as is; input can be text (all other placeholders require numbers).
`#\d+#`             | Round to `\d+` digits.
`#\d+,#`            | Round to `\d+` digits; add thousands comma separator.
`#*#`               | Interpret input as p-value and replce with a star corresponding so significance. Detault is `* 0.1, **0.05, ***0.01`.
`#\d+%#`            | Round to `\d+` digits; interpret as percentage.
`#|#|#`             | Get the absolute value of the number.
`#{.*}#`            | Arbitrary python format. Anything that `string.format()` will accept is allowed. In Python 2.6, you must prepend `0:`, that is `{0:.+}`.

- Each table contains somewhere in it a `label{tab:...}` statement.
    - This is _required_ and will be used to identify the input to use to fill in that table.
    - It must match an entry in `input.txt` ([created below](#exporting-matrices-in-stata)) **_or_** it must match a name provided in the optional mapping file.

- There must be at most one table line per code line (hence all the `\\`, but that also makes the table more readable).

- The LaTeX environment must be a table environment, not tabular. See the [LyX](#basic-example-in-lyx) and [Markdown](#basic-example-in-markdown) sections below for details on how to set up tables in those formats.

### Input

In order to fill this template, we need data. Consider this example input file, called [`input.txt`](usage/01basic/input.txt)

```
<tab:paragraph>
    5708
    'tablefill example'
    'python formatting'

<tab:example>
    1 	  1237.1234 	 1 	  	 2
    2 	  2234.4    	 3 	  	 2.4
    3 	  3.345345  	 2 	  	 2.456
    4 	  2234.4    	 3 	  	 2.4

<tab:anotherExample>
     -1.25	       -1.18	 0.1447266
     2.756	       -0.53	 9.964426e-08
      1.13	     0.57235	 0.02417291
      5708
```

See [below](exporting-matrices-in-stata) for an example of how to create this file directly from Stata. Note that the matrices do not have to be in the same order they appear in the template. As long as the label matches, tablefill will correctly match it to the template.

### Output

To get the filled output, run
```bash
tablefill -i input.txt -o filled.tex template.tex
```

This produces [`input.txt`](usage/01basic/input.txt):
```latex
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This file was produced by 'tablefill.py'
% 	Template file: /home/mauricio/Documents/projects/dev/code/archive/2015/tablefill/docs/usage/01basic/template.tex
% 	Input file(s): ['/home/mauricio/Documents/projects/dev/code/archive/2015/tablefill/docs/usage/01basic/input.txt']
% To make changes, edit the input and template files.
% %

% DO NOT EDIT THIS FILE DIRECTLY.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
\documentclass{article}
\usepackage{booktabs}
\begin{document}

Regular placeholders:
\begin{table}
  \caption{Table caption (e.g. summary stats)}
  \label{tab:example} % name must match label in input1.txt
  \begin{tabular}{p{4.25cm}crcc}
    Outcomes
    & N
    & Mean
    & (Std.)
    \\
    Outcomes 1 & 1,237 & 1.0 & (2.00) \\
    Outcomes 2 & 2,234 & 3.0 & (2.40) \\
    Outcomes 3 & 3 & 2.0 & (2.46) \\
    Outcomes 4 & 2,234 & 3.0 & (2.40) \\
    \multicolumn{4}{p{5cm}}{\footnotesize Footnotes!}
  \end{tabular}
\end{table}

% tablefill:start tab:paragraph
Placeholders do not need to be inside a table. You can also have
placeholders in the text:
\begin{itemize}
    \item $N = 5,708$
    \item This is the 'tablefill example' sample.
\end{itemize}

Note \verb'% tablefill:start tab:paragraph' tells tablefill to start
looking for placeholders using the matrix labeled \verb'tab:paragraph'
in the input file. \verb'% tablefill:end' tells tablefill to stop.

Tablefill provides several placeholders types (more on this below),
but advanced users can use any format allowed by python via \verb'{}':
'python formatting'. Here is another table, using python-style formatting:
% tablefill:end

\begin{table}
  \caption{Table caption (e.g. regression results)}
  \label{tab:anotherExample} % must match label in input.txt
  \begin{tabular}{p{4.25cm}c}
    Outcomes
    & Coef
    & (SE)
    \\
    Variable 1 & -1.2 (-1.18) \\
    Variable 2 & 2.8 (-0.53)*** \\
    Variable 3 & 1.1 (0.57)** \\
    \midrule
             N & 5,708 \\
    \multicolumn{4}{p{5cm}}{\footnotesize Footnotes!}
  \end{tabular}
\end{table}
\end{document}
```

### Explanation

The following replacements were made:

Placeholder   | Replacement
------------- | ------------------------------------------
`\#\#\#`      | replaced as is; mainly used for text input
`\#0,\#`      | round to 0 decimal places, add thousands comma-separator
`\#1\#`       | round to 1 decimal places
`\#2\#`       | round to 2 decimal places
`\#*\#`       | Input is a p-value; replaced with significance stars
`\#{}\#`      | Passes input to `"{}".format()` (print as is)
`\#{:.1f}\#`  | Passes input to `"{:.1f}".format()` (round to 1 decimal places)
`\#{:,.0f}\#` | Passes input to `"{:,.0f}".format()` (thousands comma-separator, round to 0 decimal places)

The way `tablefill` operates is:

1. Per line, the program searches for the start of a table or tablefill delimiter. In LaTeX, a table starts with `\begin{table}`. A tablefill delimiter starts with `% tablefill:start`.
2. If found, it searches for a label **_before_** the the table ends. In LaTeX `\label{tab:(.+)}` can appear anywhere _before_ `\end{table}`. With tablefill delimiters, `% tablefill:start tab:label` _must_ appear on the same line.
3. If a label is found, it searches the input files for a label a match.
4. Find all occurrences of placeholders (note that in LaTeX, `#` is a special character, so `tablefill` will match both `#` and `\#` as part of a placeholder construct; this is so that templates can be compiled before using `tablefill` to fill in the values).
5. Repeat 3 and 4 until reaching `\end{table}` or  `% tablefill:end`.
6. Move on to next table: Repeat 1 to 5 until reaching the end of the document.

Exporting Matrices in Stata
---------------------------

We provide code snippets in [several programming languages](sample-programs.md) to illustrate the format required by `tablefill` as input. For this example, we will use a Stata program named `saveTable`. We keep a copy in this repository, and you can install it from Stata by running:

```stata
local gh_repo https://raw.githubusercontent.com/mcaceresb/tablefill
net install tablefill_example, from("`gh_repo'/master/docs/programs'")
```

Now you should be able to run `saveTable` from any Stata session.  As a simple example, we create a random matrix with four rows and three columns:

```stata
matrix x = (1, 1237.1234, 1, 2)     \ ///
           (2, 2234.4,    3, 2.4)   \ ///
           (3, 3.345345,  2, 2.456)
           (4, 2234.4,    3, 2.4)

saveTable using "input.txt", outmatrix(x) tag("<tab:example>")
```

### `saveTable` arguments

- `using`: _required_, provide the filename to write to.

- `OUTMatrix`: _required_, provide the name of the matrix intended for exporting. The capitalization `OUTMatrix` means that at this command can be abbreviated up to `outmat`, that is

```stata
saveTable using "matrix.txt", outm(x) tag("<tab:example_matrix>")
```

- `tag`: _required_, string for tag for outputted matrix. Note that the format is `<tab:label>`. To append a matrix to the last tag in the file, provide a blank tag.

```stata
saveTable using "matrix.txt", outm(x) tag("<tab:example_matrix>")
saveTable using "matrix.txt", outm(y) tag(" ")
```

```
<tab:example_matrix>
    entries of x

    entries of y
```

- `Format`: _optional_, string for numerical format for outputted data. By default the output format is `%21.9f`

We give the example of a numeric matrix, as this is the most common usage, but as we saw above any text that is appended after the label can be filled by `tablefill` (entries must be tab-delimited or appear in a separate line). To produce the `input.txt` file we use earlier, run the [following `do` file](usage/01basic/example.do):

```stata
file open fh using "input.txt", write text append
file write fh "<tab:paragraph>"     _n ///
         _tab "5708"                _n ///
         _tab "'tablefill example'" _n ///
         _tab "'python formatting'" _n
file close fh

matrix x = (1, 1237.1234, 1, 2)     \ ///
           (2, 2234.4,    3, 2.4)   \ ///
           (3, 3.345345,  2, 2.456) \ ///
           (4, 2234.4,    3, 2.4)

matrix y = (-1.25,   -1.18, 0.1447266)    \ ///
           (2.756,   -0.53, 9.964426e-08) \ ///
           (1.13,  0.57235, 0.02417291)   \ ///
           (5708,        ., .)

saveTable using "input.txt", outmatrix(x) f(%12.0g) tag("<tab:example>")
saveTable using "input.txt", outmatrix(y) f(%12.0g) tag("<tab:anotherExample>")
```

Now you can run

```
tablefill -i input.txt -o filled.tex template.tex
```

Basic Example in Markdown
-------------------------

Consider the file [`template.md`](usage/01basic/template.md)

```markdown
<!-- tablefill:start tab:paragraph -->

Sample paragraph
- $N = #0,#$
- This is the ### sample.

Python-style formatting: #{}#.

<!-- tablefill:end -->

<!-- tablefill:start tab:example -->

| Outcomes     | N    | Mean | (Std.) |
| ------------ | ---- | ---- | ------ |
| Outcomes ### | #0,# | #1,# | (#2,#) |
| Outcomes ### | #0,# | #1,# | (#2,#) |
| Outcomes ### | #0,# | #1,# | (#2,#) |
| Outcomes ### | #0,# | #1,# | (#2,#) |

<!-- tablefill:end -->

`pandoc` will compile raw LaTeX inside markdown documents, so
`tablefill` will also replace placeholders in LaTeX tables inside
markdown files. The replacement rules for LaTeX also apply here.

\begin{table}
  \caption{Table caption (e.g. regression results)}
  \label{tab:anotherExample}
  \begin{tabular}{p{4.25cm}c}
    Outcomes
    & Coef
    & (SE)
    \\
    Variable 1 & \#{:.1f}\# (\#{:.2f}\#)\#*\# \\
    Variable 2 & \#{:.1f}\# (\#{:.2f}\#)\#*\# \\
    Variable 3 & \#{:.1f}\# (\#{:.2f}\#)\#*\# \\
    \midrule
             N & \#{:,.0f}\# \\
    \multicolumn{4}{p{5cm}}{\footnotesize Footnotes!}
  \end{tabular}
\end{table}
\end{document}
```

Using the same [`input.txt`](usage/01basic/input.txt) file as above, run
```basb
tablefill.py -i input.txt -o filled.md template.md
```

This produces [`filled.md`](usage/01basic/filled.md)
```markdown
<!-- This file was produced by 'tablefill.py'
	Template file: /home/mauricio/Documents/projects/dev/code/archive/2015/tablefill/docs/usage/01basic/template.md
	Input file(s): ['/home/mauricio/Documents/projects/dev/code/archive/2015/tablefill/docs/usage/01basic/input.txt']
To make changes, edit the input and template files.


DO NOT EDIT THIS FILE DIRECTLY.
 -->

<!-- tablefill:start tab:paragraph -->

Sample paragraph
- $N = 5,708$
- This is the 'tablefill example' sample.

Python-style formatting: 'python formatting'.

<!-- tablefill:end -->

<!-- tablefill:start tab:example -->

| Outcomes     | N    | Mean | (Std.) |
| ------------ | ---- | ---- | ------ |
| Outcomes 1 | 1,237 | 1.0 | (2.00) |
| Outcomes 2 | 2,234 | 3.0 | (2.40) |
| Outcomes 3 | 3 | 2.0 | (2.46) |
| Outcomes 4 | 2,234 | 3.0 | (2.40) |

<!-- tablefill:end -->

`pandoc` will compile raw LaTeX inside markdown documents, so
`tablefill` will also replace placeholders in LaTeX tables inside
markdown files. The replacement rules for LaTeX also apply here.

\begin{table}
  \caption{Table caption (e.g. regression results)}
  \label{tab:anotherExample}
  \begin{tabular}{p{4.25cm}c}
    Outcomes
    & Coef
    & (SE)
    \\
    Variable 1 & -1.2 (-1.18) \\
    Variable 2 & 2.8 (-0.53)*** \\
    Variable 3 & 1.1 (0.57)** \\
    \midrule
             N & 5,708 \\
    \multicolumn{4}{p{5cm}}{\footnotesize Footnotes!}
  \end{tabular}
\end{table}
\end{document}
```

Basic Example in LyX
--------------------

!!! info "Warning"
    This section is under construction

Comparison with other methods
-----------------------------

There are good reasons to use tablefill, and good reasons not to.

For example, if exporting your results quickly is more important than the format in which they are presented, then the additional complexity of `tablefill` is probably not worth the hassle. I think [`estout`](http://repec.sowi.unibe.ch/stata/estout/) can be very helpful for these scenarios, but it does impose a specific process to create the matrix of values that underlies the table displayed in your document. It is very good if you just want to export your results, but when you want to format them, add notes around them, or customize them in any way, all this must be done from Stata, rather than LaTeX, LyX, or Markdown.

Stata is mainly made for data analysis, not text fomatting. The main idea behind `tablefill` is that it allows the user to do all of the formatting in LaTeX, which is what LaTeX is built for, and all the analysis in Stata. To get the data back and forth between the two, minimal structure is required (labeled output that is tab-delimited). The key idea is flexibility: `tablefill` allows the user to put placeholders anywhere as long as they are inside a labeled environment. You can update titles, notes, entire paragraphs, and so on.

`tablefill` is also great if you want to plan out your document _before_ generating all of your results. You can create and compile a document and see exactly how it will look before adding in results (you will just see placeholders instead of your data).
