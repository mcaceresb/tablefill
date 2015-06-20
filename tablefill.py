#!/usr/bin/env python
# encoding: utf-8

"""Fill LaTeX template files with external inputs

Description
-----------

tablefill_tex.py is a python module designed to fill LaTeX tables
with output from text files (usually output from Stata or Matlab).
The original tablefill.py does the same for LyX files.


Usage
-----

tablefill.py [-h] [-i [INPUT [INPUT ...]]] [-o OUTPUT] [-f] TEMPLATE

positional arguments:
  TEMPLATE              Code template

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         Show current version
  --help-all            Show additional documentation
  -i [INPUT [INPUT ...]], --input [INPUT [INPUT ...]]
                        Input files with tables (default: INPUT_table)
  -o OUTPUT, --output OUTPUT
                        Processed template file (default: INPUT_filled)
  -f, --force           Name input/output automatically

See examples below for details on the files and the replace engine

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

- Missing table tag in the input file or in the template file.

- Mismatch between the length of the template table and corresponding
  text table. If the template table has more entries to be filled than
  the text table has entries to fill from, this will cause an error and
  the table will not be filled.

- Use of numerical tags (e.g. #1#) to fill non-numerical data. This will
  cause an error. Non-numerical data can only be filled using "###", as
  it does not make sense to round or truncate this data.
"""

from __future__ import division
from traceback import format_exc
from decimal import Decimal, ROUND_HALF_UP
from os import linesep, path, access, W_OK
import argparse
import re

__program__   = "tablefill"
__usage__     = "[-h] [-i [INPUT [INPUT ...]]] [-o OUTPUT] [-f] TEMPLATE"
__purpose__   = "Fill tagged tables in LaTeX files with external text tables"
__author__    = "Mauricio Caceres <caceres@nber.org>"
__created__   = "Thu Jun 18"
__updated__   = "Sat Jun 20"
__version__   = __program__ + " version 0.1.0 updated " + __updated__

# ---------------------------------------------------------------------
# tablefill

def tablefill():
    fill = tablefill_internals()
    fill.get_input_parser()
    fill.get_parsed_arguments()
    fill.get_argument_strings(prints = True)
    try:
        status, msg = tablefill_tex(template = fill.template,
                                    input    = fill.input,
                                    output   = fill.output)
    except:
        print format_exc()
        print fill.parser.print_usage()

# ---------------------------------------------------------------------
# tablefill_tex

def tablefill_tex(**kwargs):
    try:
        print "Parsing arguments..."
        fill_tex = tablefill_tex_internals()
        fill_tex.get_parsed_arguments(kwargs)

        print "Parsing tables in '%s' into dictionary." % fill_tex.input
        fill_tex.get_parsed_tables()

        print "Searching for labels in template '%s'" % fill_tex.template + linesep
        fill_tex.get_filled_template()

        print "Adding warning that this was automatically generated..."
        fill_tex.get_notification_message()

        print "Writing to output file '%s'" % fill_tex.output
        outtext = fill_tex.notification_msg + fill_tex.filled_template
        fill_tex.write_to_output(outtext)

        print "Wrapping up..." + linesep
        fill_tex.get_exit_message()
        print fill_tex.exit + '!'
        print fill_tex.exit_msg
        return fill_tex.exit, fill_tex.exit_msg
    except:
        exit_msg = format_exc()
        exit     = 'ERROR'
        print exit + '!'
        print exit_msg
        return exit, exit_msg

# ---------------------------------------------------------------------
# tablefill_internals

class tablefill_internals:
    def __init__(self):
        pass

    def get_input_parser(self):
        """
        Parse command-line arguments using argparse; return parser
        """
        parser_desc    = __purpose__
        parser_prog    = __program__
        parser_use     = __program__ + ' ' + __usage__
        parser_version = __version__
        parser = argparse.ArgumentParser(prog  = parser_prog,
                                         description = parser_desc,
                                         usage = parser_use)
        parser.add_argument('-v', '--version',
                            action   = 'version',
                            version  = parser_version,
                            help     = "Show current version")
        parser.add_argument('--help-all',
                            action   = 'help',
                            help     = "Show additional documentation")
        parser.add_argument('template',
                            nargs    = 1,
                            type     = str,
                            metavar  = 'TEMPLATE',
                            help     = "Code template")
        parser.add_argument('-i', '--input',
                            dest     = 'input',
                            type     = str,
                            nargs    = '*',
                            metavar  = 'INPUT',
                            default  = None,
                            help     = "Input files with tables" +
                            " (default: INPUT_table)",
                            required = False)
        parser.add_argument('-o', '--output',
                            dest     = 'output',
                            type     = str,
                            nargs    = 1,
                            metavar  = 'OUTPUT',
                            default  = None,
                            help     = "Processed template file" +
                            " (default: INPUT_filled)",
                            required = False)
        parser.add_argument('-f', '--force',
                            action   = 'store_true',
                            help     = "Name input/output automatically",
                            required = False)
        self.parser = parser

    def get_parsed_arguments(self):
        """
        Get arguments; if input and output names are missing, guess them
        """
        args = self.parser.parse_args()
        missing_args  = []
        missing_args += ['INPUT'] if args.input is None else []
        missing_args += ['OUTPUT'] if args.output is None else []
        if missing_args != []:
            if not args.force:
                isare = ' is ' if len(missing_args) == 1 else ' are '
                missing_args_msg   = ' and '.join(missing_args)
                missing_args_msg  += isare + 'missing without --force option.'
                raise KeyError(missing_args_msg)
            else:
                template_name = path.basename(args.template[0])
                if 'INPUT' in missing_args:
                    args.input = self.rename_file(template_name, '_table', 'txt')
                if 'OUTPUT' in missing_args:
                    args.output = self.rename_file(template_name, '_filled')
        self.args = args

    def rename_file(self, base, add, ext = None):
        out  = path.splitext(base)
        add += out[-1] if ext is None else '.' + ext
        return [out[0] + add]

    def get_argument_strings(self, prints = False):
        """
        Get arguments as strings to pass to tablefill_tex
        """
        self.template = path.abspath(self.args.template[0])
        self.input    = ' '.join([path.abspath(f) for f in self.args.input])
        self.output   = path.abspath(self.args.output[0])
        if prints:
            print linesep + "I found these arguments:"
            print 'template = %s' % self.template
            print 'input    = %s' % self.input
            print 'output   = %s' % self.output
            print ''

# ---------------------------------------------------------------------
# tablefill_tex_internals

class tablefill_tex_internals:
    def __init__(self):
        self.warn_msg  = {'nomatch': '', 'notable': '', 'nolabel': ''}
        self.warnings  = {'nomatch': [], 'notable': [], 'nolabel': []}
        self.tags      = '^<Tab:(.+)>' + linesep
        self.begin     = r'.*\\begin{table}.*'
        self.end       = r'.*\\end{table}.*'
        self.label     = r'.*\\label{tab:(.+)}'
        self.matcha    = r'\\*#\\*#\\*#'      # Matches ### and \#\#\#
        self.matchb    = r'\\*#(\d+)(,*)\\*#' # Matches #\d+,*# and \#\d+,*\#
        self.matchc    = '(-*\d+)(\.*\d*)'    # Matches (-)integer(.decimal)

    def get_parsed_arguments(self, kwargs):
        """
        Gets template, input, and output from kwargs with checks for
            - All arguments are there as strings
            - All files exist
            - Output directory exists and is writable
        """
        args = ['input', 'template', 'output']

        missing_args = filter(lambda arg: arg not in kwargs.keys(), args)
        if missing_args != []:
            isare = " is " if len(missing_args) == 1 else " are "
            missing_args_msg  = " and ".join(missing_args)
            missing_args_msg += isare + "missing. Check function call."
            raise KeyError(missing_args_msg)

        m = filter(lambda t: not isinstance(t[1], basestring), kwargs.items())
        mismatched_types = m
        if mismatched_types != []:
            msg = "Expected str for '%s' but got type '%s'"
            msg = [msg % (k, v.__class__.__name__) for k, v in mismatched_types]
            mismatched_msg = linesep.join(msg)
            raise TypeError(mismatched_msg)

        self.template = path.abspath(kwargs['template'])
        self.output   = path.abspath(kwargs['output'])
        self.input    = [path.abspath(ins) for ins in kwargs['input'].split()]

        infiles = [self.template] + self.input
        missing_files = filter(lambda f: not path.isfile(f), infiles)
        if missing_files != []:
            missing_files_msg  = 'Please check the following are available:'
            missing_files_msg += linesep + linesep.join(missing_files)
            raise IOError(missing_files_msg)

        outdir = path.split(self.output)[0]
        missing_path = not path.isdir(outdir)
        if missing_path:
            missing_outdir_msg  = 'Please check the following directory exists: '
            missing_outdir_msg += outdir
            raise IOError(missing_outdir_msg)

        cannot_write = not access(outdir, W_OK)
        if cannot_write:
            cannot_write_msg  = 'Please check you have write access to: '
            cannot_write_msg += outdir
            raise IOError(cannot_write_msg)

    def get_parsed_tables(self):
        """
        Parse table file(s) into a dictionary with tags as keys and
        lists of table entries as values
        """
        read_data  = [open(file, 'rU').readlines() for file in self.input]
        parse_data = sum(read_data, [])
        tables = {}
        for row in parse_data:
            if re.match(self.tags, row, flags = re.IGNORECASE):
                tag = re.findall(self.tags, row, flags = re.IGNORECASE)
                tag = tag[0].lower()
                tables[tag] = []
            else:
                clean_row_entries = [entry.strip() for entry in row.split('\t')]
                tables[tag] += clean_row_entries
        self.tables = {k: self.filter_missing(v) for k, v in tables.items()}

    def filter_missing(self, string_list):
        return filter(lambda a: a != '.' and a != '', string_list)

    def get_filled_template(self):
        """
        Fill template file using table input(s)
        """
        read_template = open(self.template, 'rU').readlines()
        table_start   = -1
        table_search  = False
        table_tag     = ''
        table_entry   = 0

        for n in range(len(read_template)):
            line = read_template[n]
            if not table_search and re.search(self.begin, line):
                table_search, table_tag  = self.search_label(read_template, n)
                table_start  = n
                search_msg   = self.get_search_msg(table_search, table_tag, n)
                print search_msg

            if re.search(self.matcha, line) or re.search(self.matchb, line):
                if table_search:
                    table  = self.tables[table_tag]
                    update = self.replace_line(line, table, table_entry)
                    read_template[n], table_entry = update
                elif table_start == -1:
                    self.warnings['notable'] += [str(n)]
                    warn_notable  = "Line %d matches #(#|\d+,*)#"
                    warn_notable += " but is not in begin/end table statements."
                    warn_notable += " Skipping..."
                    print warn_notable % n
                elif table_tag == '':
                    self.warnings['nolabel'] += [str(n)]
                    warn_nolabel  = "Line %d matches #(#|\d+,*)#"
                    warn_nolabel += " but couldn't find \\label{tab:.+}."
                    warn_nolabel += " Skipping..."
                    print warn_nolabel % n

            if re.search(self.end, line):
                search_msg   = "Table '%s' in line %d ended in line %d."
                search_msg  += " %d replacements were made." % table_entry
                search_msg   = search_msg % (table_tag, table_start, n)
                print search_msg + linesep

                table_start  = -1
                table_search = False
                table_tag    = ''
                table_entry  = 0

        self.filled_template = read_template

    def search_label(self, intext, start):
        """
        Search for label in list 'intext' from position 'start' until an
        \end{table} statement. Returns label value ('' if none is found)
        and whether it matches a tag in the tables file
        """
        N = start
        searchline  = intext[N]
        searchmatch = re.search(self.label, searchline, flags = re.IGNORECASE)
        searchend   = re.search(self.end, searchline)
        while not searchmatch and not searchend:
            N += 1
            searchline  = intext[N]
            searchmatch = re.search(self.label, searchline, flags = re.IGNORECASE)
            searchend   = re.search(self.end, searchline)
        if not searchend and searchmatch:
            label = re.findall(self.label, searchline, flags = re.IGNORECASE)[0]
            label = label.strip('{}').lower()
            return label in self.tables, label
        else:
            return False, ''

    def get_search_msg(self, search, tag, start):
        warn_nomatch = ''
        search_msg   = "Found table in line %d. " % start
        if tag == '':
            search_msg += "No label. Skipping..."
        else:
            search_msg += "Found label '%s'... " % tag
            if search:
                search_msg += "Found match!"
            else:
                self.warnings['nomatch']  += [tag]
                warn_nomatch  = linesep + "NO MACHES FOR '%s' IN '%s'!"
                warn_nomatch += " Please check input file(s)"
                warn_nomatch  = warn_nomatch % (tag, self.input)
        return search_msg + warn_nomatch

    def replace_line(self, line, table, tablen):
        """
        Replaces all matches of #(#|\d+,*)#. Splits by & because that's
        how LaTeX delimits tables. Returns how many values it replaced
        because LaTeX can have any number of entries per line.
        """
        linesep = line.split('&')
        for i in range(len(linesep)):
            cell = linesep[i]
            if re.search(self.matcha, cell):
                entry      = table[tablen]
                linesep[i] = re.sub(self.matcha, entry, cell)
                tablen    += 1
            elif re.search(self.matchb, cell):
                entry      = table[tablen]
                linesep[i] = self.round_and_format(cell, entry)
                tablen    += 1
        line = '&'.join(linesep)
        return line, tablen

    def round_and_format(self, cell, entry):
        """
        Rounds entry according to the format in cell. Note Decimal's
        quantize makes the object have the same number of significant
        digits as the input passed. format(str, ',d') returns str with
        comma as thousands separator
        """
        precision, comma = re.findall(self.matchb, cell)[0]
        precision = int(precision)
        roundas   = 0 if precision == 0 else pow(10, -precision)
        roundas   = Decimal(str(roundas))
        rounded   = str(Decimal(entry).quantize(roundas, rounding = ROUND_HALF_UP))
        if ',' in comma:
            integer_part, decimal_part = re.findall(self.matchc, rounded)[0]
            rounded = format(int(integer_part), ',d') + decimal_part
        return re.sub(self.matchb, rounded, cell)

    def get_notification_message(self):
        """
        Inserts a message atop the LaTeX file that this was created by
        Intablefill_tex. cludes the following warnings, when applicable
            - #(#|\d+,*)# is found on a line outside a table environment
            - #(#|\d+,*)# is on a table environment with no label
            - A tabular environment's label has no match in tables.txt
        """
        for key in self.warnings.keys():
            self.warnings[key] = ','.join(self.warnings[key])

        self.warning = True in [v != '' for v in self.warnings.values()]
        if self.warning:
            fill   = (self.template, self.input)
            imtags = "WARNING: These tags were in '%s' but not in '%s':" % fill
            imhead = "WARNING: Lines in '%s' maching #(#|\d+,*)#" % self.template
            imend  = linesep + "Output '%s' may not compile!" % self.output

        if self.warnings['nomatch'] != '':
            self.warn_msg['nomatch']  = imtags
            self.warn_msg['nomatch'] += self.warnings['nomatch'] + imend

        if self.warnings['notable'] != '':
            self.warn_msg['notable']  = imhead
            self.warn_msg['notable'] += " but were not in a table environment: "
            self.warn_msg['notable'] += self.warnings['notable'] + imend

        if self.warnings['nolabel'] != '':
            self.warn_msg['nolabel']  = imhead
            self.warn_msg['nolabel'] += " but the environment had no label: "
            self.warn_msg['nolabel'] += self.warnings['nolabel'] + imend

        head = 3 * [72 * '%' + linesep]
        msg  = ["This file was produced by 'tablefill.py'" + linesep]
        msg += ["    Template file: %s" % self.template + linesep]
        msg += ["    Input file(s): %s" % self.input + linesep]
        msg += ["To make changes, edit the input and template files." + linesep]

        if self.warning:
            msg += [linesep + "THERE WAS AN ISSUE CREATING THIS FILE!" + linesep]
            msg += [s + linesep for s in self.warn_msg.values()]
        else:
            msg += [linesep + "DO NOT EDIT THIS FILE DIRECTLY." + linesep]
        msg  = linesep.join(msg).split(linesep)
        self.notification_msg = head + ['% ' + m + linesep for m in msg] + head

    def write_to_output(self, text):
        outfile = open(self.output, 'wb')
        outfile.write(''.join(text))
        outfile.close()

    def get_exit_message(self):
        if self.warning:
            msg  = ["The following issues were found:"]
            msg += filter(lambda wm: wm != '', self.warn_msg.values())
            self.exit_msg = linesep.join(msg)
            self.exit     = 'WARNING'
        else:
            msg  = "All tags in '%s' successfully filled by 'tablefill.py'"
            msg += linesep + "Output can be found in '%s'" + linesep
            self.exit_msg = msg % (self.template, self.output)
            self.exit     = 'SUCCESS'

# ---------------------------------------------------------------------
# Run function

if __name__ == "__main__":
    tablefill()
