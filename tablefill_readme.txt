Supplementary readme for tablefiil.py; see script for use details

LIMITATIONS
-----------

1. New lines of the table must be on new lines of the .tex file
2. Checks for #(#|\d+,*)# inside tables, not tabular. Sorry!
3. Currently, soft warnings are given for the following
    - #(#|\d+,*)# is found on a line outside a table environment
    - #(#|\d+,*)# is on a table environment with no label
    - A tabular environment's label has no match in tables.txt
    The original tablefill.py ignores these cases


Notes
-----

I simplified several steps from tablefill. However, this function is
more complicated because
    - The function now checks inputs are correct (names and type)
    - The function now checks if input files exist
    - The function gives soft warnings for the cases mentioned above
    - labels in LaTeX can be anywhere in the table environment
    - .tex can have several matches of the pattern in the same line
    - # is a special character in TeX and is escaped by \#; hence I
        wrote regexps to match both #(#|\d+,*)# and \#(\#|\d+,*)\#

The way the funtion operates is
    1. Per line, the program searches for a \begin{table}
    2. If found, it searches for a \label{tab:(.+)} BEFORE an \end{table}
    3. If a label is found, search the parsed table input(s) for a match
    4. Find all occurrences of ###, #\d+,*# in the line and replace
        input value <- output value
        ###         <- same value
        #\d+#       <- rounded to \d+ digits
        #\d+,#      <- rounded to \d+ digits w/thousands comma separator
    5. Repeat 3 and 4 until an \end{table}


Examples (input)
----------------

Note: This section was adapted from the readme for the original tablefill.py

Input files must be tab-delimited rows of numbers or characters,
preceded by <label>. The numbers can be arbitrarily long, can be
negative, and can also be in scientific notation.

<tab:Test>
1	2	3
2	3	1
3	1	2


<tab:FunnyMat>
1	2	3	23	2
2	3
3	1	2	2
1

(The rows do not need to be of equal length.)

Completely blank (no tab) lines are ignored. If a "cell" is merely "."
or "[space]", then it is treated as missing. That is, in the program:

<tab:Test>
1	2	3
2	.	1	3
3	    1	2

is equivalent to:

<tab:Test>
1	2	3
2	1	3
3	1	2

This feature is useful as Stata outputs missing values in numerical
variables as ".", and missing values in string variables as "[space]".

Scientific notation is of the form: [numbers].[numbers]e(+/-)[numbers]
23.2389e+23
-2.23e-2
-0.922e+3


Examples (template)
-------------------

Note: This section was adapted from the readme for the original tablefill.py

The template determines the where the numbers from the input files are
and how they will be displayed. Every table in the template file (if it
is to be filled) must appear within a table environment. There can be
several tabular environments within the table environment, but only ONE
label per table environment. This is also a LaTeX limitation.

While label names may appear more than once in both the template and
input files, only the last instance of the label in the input files will
be used. This because of the way the system is set up: The last label in
the input file should be the most up to date version of that table. In
the template file, repeated labels are filled with the same data.

By design, labels are NOT case-sensitive.

The values in the template file are parsed as follows:
    ###         <- same value
    #\d+#       <- rounded to \d+ digits
    #\d+,#      <- rounded to \d+ digits w/thousands comma separator

Consider the following examples

abc + ### = abc
2309.2093 + ###     = 2309.2093
2309.2093 + #4#     = 2309.2093
2309.2093 + #5#     = 2309.20930
2309.2093 + #20#    = 2309.20930000000000000000
2309.2093 + #3#     = 2309.209
2309.2093 + #2#     = 2309.21
2309.2093 + #0#     = 2309
2309.2093 + #0,#    = 2,309
-2.23e-2  + #2#     = -0.0223 + #2#             = -0.02
-2.23e-2  + #7#     = -0.0223 + #7#             = -0.0223000
-2.23e+10 + #7,#    = -22300000000 + #7,#       = -22,300,000,000.000000
2309.2093 + (#2#)   = (2309.21)
2309.2093 + #2#**   = 2309.21**
2309.2093 + ab#2#cd = ab2309.21cd

Note that there can be ANYTHING around the pattern and the engine will
only match the pattern. Further, in LaTeX, the # character must be
escaped, so the engine also matches \#. Consider:

3234.43241 + \\beta Hi \$(\#\#\#)\%*    = \\beta Hi \$(3234.43241)\%*
3234.43241 + & \\beta Hi \$(\##\#)\%*   = \\beta Hi \$(3234.43241)\%*
3234.43241 + & \\beta Hi \$(\#\##)\%*   = \\beta Hi \$(3234.43241)\%*
3234.43241 + & \\beta Hi \$(#\#\#)\%    = \\beta Hi \$(3234.43241)\%
3234.43241 + & \\beta Hi \$(\###)*\%    = \\beta Hi \$(3234.43241)*\%
3234.43241 + & \\beta Hi \$(\#0,\#)\%*  = \\beta Hi \$(3,234)\%*
3234.43241 + & \\beta Hi \$(\#0,\#)\%*  = \\beta Hi \$(3,234)\%*
3234.43241 + & \\beta Hi \$(\#0,#*      = \\beta Hi \$(3,234*
3234.43241 + & \\beta Hi \$(#0,\#*      = \\beta Hi \$(3,234*
3234.43241 + & \\beta Hi \$(\#0,#*      = \\beta Hi \$(3,234*


Examples (both)
---------------

Note: This section was adapted from the readme for the original tablefill.py

Input:
<tab:Test>
1	2	3
2	1	3
3	1	2

Template:
\label{tab:test}
\#\#\# & \#\#\# & \#\#\# \\\\
\#\#\# & \#\#\# & \#\#\# \\\\
\#\#\# & \#\#\# & \#\#\# \\\\

Output:
\label{tab:test}
1	2	3
2	1	3
3	1	2


Input:
<tab:Test>
1	.	3
2e-5	1	3.023
.	-1	2	3

Template:
\label{tab:test}
(\#\#\#) & 2      & \#\#\# & \\\\
\#3\#    & \#\#\# & \#1\#  & \\\\
NA       & \#\#\# & \#\#\# & \#\#\# \\\\

Output:
\label{tab:test}
(1)	2	3
0.000	1	3.0
NA	-1	2	3

IMPORTANT: Missing values in input and template need not line up.

Input:
<tab:Test>
1	.	3
2e-5	.	3.023
.	-1	2

Template:
\label{tab:test}
\#\#\# & \#\#\# & abc    \\\\
abc    & \#2\#  & \#3\#  \\\\
NA     & \#\#\# & \#\#\# \\\\

Output:
\label{tab:test}
1	3	abc
abc	0.00	3.023
NA	-1	2


Input:
<tab:Test>
1	1	2
1	1	3
2	-1	2

Template:
\label{tab:test}
\#\#\# & \#\#\# & \#\#\# \\\\
abc    & abc    & abc    \\\\
\#\#\# & \#2\#  & \#3\#  \\\\
\#\#\# & \#\#\# & \#\#\# \\\\

Output:
\label{tab:test}
1	1	2
abc	abc	abc
1	1.00	3.000
2	-1	2


Error Logging
-------------

The program indicates
- When it finds a table environment
    - If it finds a label within that environment
    - If the label matches one in the input file(s)
    - Whether it finds the #(#|\d+,*)# pattern but no label
    - When it finds the end of the table environment
    - How many substitutions it made in the table
- When it finds the #(#|\d+,*)# pattern outside a table environment
- When it finds an error (and if so it terminates)

Common Mistakes
---------------

Note: This section was adapted from the readme for the original tablefill.py

- Missing table tag in the input file or in the template file.

- Mismatch between the length of the template table and corresponding
text table. If the template table has more entries to be filled than
the text table has entries to fill from, this will cause an error and
the table will not be filled.

- Use of numerical tags (e.g. #1#) to fill non-numerical data. This will
cause an error. Non-numerical data can only be filled using "###", as
it does not make sense to round or truncate this data.
