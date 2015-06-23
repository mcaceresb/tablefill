#!/usr/bin/env python
# encoding: utf-8

"""Fill LaTeX template files with external inputs

Description
-----------

tablefill.py is a python module designed to fill LaTeX and Lyx tables
with output from text files (usually output from Stata or Matlab). The
original tablefill.py does the same for LyX files only, and has fewer
error checks.


Usage
-----

tablefill.py [-h] [-v] [-i [INPUT [INPUT ...]]] [-o OUTPUT]
             [-t {auto,lyx,tex}] [-f] [-c] TEMPLATE

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

flags:
  -f, --force           Name input/output automatically
  -c, --compile         Compile output

See tablefill_readme.txt for details on the files and the replace engine

Notes
-----

Several try-catch pairs and error checks are redundant because right now
this may also be run from python and not just from the command line
"""

# NOTE: For all my personal projects I import the print function from
# the future, but it would break existing code so I don't do it here.

from __future__ import division
from traceback import format_exc
from decimal import Decimal, ROUND_HALF_UP
from os import linesep, path, access, W_OK
import argparse
import re

__program__   = "tablefill.py"
__usage__     = """[-h] [-v] [-i [INPUT [INPUT ...]]] [-o OUTPUT]
                    [-t {auto,lyx,tex}] [-f] [-c] TEMPLATE"""
__purpose__   = "Fill tagged tables in LaTeX files with external text tables"
__author__    = "Mauricio Caceres <caceres@nber.org>"
__created__   = "Thu Jun 18"
__updated__   = "Sat Jun 20"
__version__   = __program__ + " version 0.1.0 updated " + __updated__

def main():
    """
    WARNING: This function expects command-line inputs to exist.
    """
    exit   = 'PARSE'
    fill   = tablefill_internals_cliparse()
    fill.get_input_parser()
    try:
        fill.get_parsed_arguments()
        fill.get_argument_strings(prints = True)
        fill.get_file_type()
        exit     += " SUCCESS"
        exit_msg  = "Arguments correctly parsed. Will run tablefill."
        print exit_msg
    except:
        exit     += ' ERROR'
        exit_msg  = format_exc()
        print exit + '!'
        print exit_msg
        fill.parser.print_usage()

    exit, exit_msg = tablefill(template = fill.template,
                               input    = fill.input,
                               output   = fill.output,
                               filetype = fill.ext)

    if exit == 'SUCCESS':
        fill.get_compiled()
    elif exit == 'WARNING':
        print "Exit status came with a warning"
        print "Do you really want to continue?"
        fill.get_compiled()
    elif exit == 'ERROR':
        fillerror_msg  = 'ERROR while filling table.'
        fillerror_msg += ' Check function call.' + linesep
        print fillerror_msg
        fill.parser.print_usage()

# ---------------------------------------------------------------------
# tablefill

def tablefill(filetype = 'lyx', **kwargs):
    """Fill LaTeX and LyX template files with external inputs

    Description
    -----------

    tablefill is a python function designed to fill LaTeX and LyX tables
    with output from text files (usually output from Stata or Matlab).
    The original tablefill.py does the same but only for LyX files, and
    has fewer error checks. The regexps are also slightly different.

    Input
    -----

    See 'tablefill_readme.txt' for details on the format of these files.

    template : str
        Name of user-written document to use as basis for update
    input : str
        Space-separated list of files with tables to be used in update.
    output : str
        Filled template to be produced.

    Output
    ------
    exit : str
        One of SUCCESS, WARNING, ERROR
    exit_msg : str
        Details on the exit status


    Usage
    -----
    exit, exit_msg = tablefill(template = 'template_file',
                               input    = 'input_file(s)',
                               output   = 'output_file')
    """
    try:
        print "Parsing arguments..."
        fill_engine = tablefill_internals_engine(filetype)
        fill_engine.get_parsed_arguments(kwargs)

        print "Parsing tables in '%s' into dictionary." % fill_engine.input
        fill_engine.get_parsed_tables()

        print "Searching for labels in template '%s'" % fill_engine.template
        print ""
        fill_engine.get_filled_template()

        print "Adding warning that this was automatically generated..."
        fill_engine.get_notification_message()

        print "Writing to output file '%s'" % fill_engine.output
        fill_engine.write_to_output(fill_engine.filled_template)

        print "Wrapping up..." + linesep
        fill_engine.get_exit_message()
        print fill_engine.exit + '!'
        print fill_engine.exit_msg
        return fill_engine.exit, fill_engine.exit_msg
    except:
        exit_msg = format_exc()
        exit     = 'ERROR'
        print exit + '!'
        print exit_msg
        return exit, exit_msg

# ---------------------------------------------------------------------
# tablefill_internals

class tablefill_internals_cliparse:
    """
    WARNING: Internal class to parse arguments to pass to tablefill
    """
    def __init__(self):
        self.compiler = {'tex': "pdflatex ",
                         'lyx': "lyx -e pdf2 "}

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
        parser.add_argument('-t', '--type',
                            dest     = 'filetype',
                            type     = str,
                            nargs    = 1,
                            choices  = ['auto', 'lyx', 'tex'],
                            default  = ['auto'],
                            help     = "Template file type (default: auto)",
                            required = False)
        parser.add_argument('-f', '--force',
                            dest     = 'force',
                            action   = 'store_true',
                            help     = "Name input/output automatically",
                            required = False)
        parser.add_argument('-c', '--compile',
                            dest     = 'compile',
                            action   = 'store_true',
                            help     = "Compile output",
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
            print "template = %s" % self.template
            print "input    = %s" % self.input
            print "output   = %s" % self.output
            print ""

    def get_file_type(self):
        fname = path.basename(self.template)
        ext   = path.splitext(fname)[-1].lower().strip('. ')
        inext = self.args.filetype[0].lower()
        if inext not in ['auto', 'tex', 'lyx']:
            unknown_type = "Type '%s' not allowed. Expected {auto,lyx,tex}."
            unknown_type = unknown_type % inext
            raise KeyError(unknown_type)
        elif inext == 'auto':
            if ext not in ['tex', 'lyx']:
                unknown_type  = "File type '%s' not known."
                unknown_type += " Expecting .lyx or .tex file."
                unknown_type = unknown_type % ext
                raise KeyError(unknown_type)
            else:
                self.ext = ext.lower()
                print "NOTE: Automatically detected input type as %s" % ext
        else:
            self.ext = inext
            if ext != inext:
                mismatch_msg  = "NOTE: Provided template type '%s' "
                mismatch_msg += "does not match detected template type '%s'"
                mismatch_msg += linesep + "Will use program associated with '%s'"
                mismatch_msg  = mismatch_msg % (inext, ext, inext)
                print mismatch_msg + linesep

    def get_compiled(self):
        if self.args.compile:
            compile_program  = self.compiler[self.ext]
            compile_program += ' ' + self.output
            print "Compiling not yet implemented. Stay tuned! Would've run:"
            print compile_program + linesep

# ---------------------------------------------------------------------
# tablefill_tex_internals

class tablefill_internals_engine:
    """
    WARNING: Internal class used by tablefill_tex
    """
    def __init__(self, filetype = 'tex'):
        self.filetype  = filetype.lower()
        if self.filetype not in ['lyx', 'tex']:
            unknown_type  = "File type '%s' not known."
            unknown_type += " Expecting .lyx or .tex file."
            unknown_type  = unknown_type % filetype
            raise KeyError(unknown_type)
        self.warn_msg  = {'nomatch': '', 'notable': '', 'nolabel': ''}
        self.warnings  = {'nomatch': [], 'notable': [], 'nolabel': []}
        self.tags      = '^<Tab:(.+)>' + linesep
        self.matcha    = r'\\*#\\*#\\*#'      # Matches ### and \#\#\#
        self.matchb    = r'\\*#(\d+)(,*)\\*#' # Matches #\d+# and \#\d+,*\#
        self.matchc    = '(-*\d+)(\.*\d*)'    # Matches (-)integer(.decimal)
        if self.filetype == 'tex':
            self.begin = r'.*\\begin{table}.*'
            self.end   = r'.*\\end{table}.*'
            self.label = r'.*\\label{tab:(.+)}'
        elif self.filetype == 'lyx':
            self.begin = r'name "tab:'
            self.end   = r'</lyxtabular>'
            self.label = r'name "tab:(.+)"'

    def get_parsed_arguments(self, kwargs, filetype):
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
            missing_files_msg  = "Please check the following are available:"
            missing_files_msg += linesep + linesep.join(missing_files)
            raise IOError(missing_files_msg)

        outdir = path.split(self.output)[0]
        missing_path = not path.isdir(outdir)
        if missing_path:
            missing_outdir_msg  = "Please check the following directory exists:"
            missing_outdir_msg += outdir
            raise IOError(missing_outdir_msg)

        cannot_write = not access(outdir, W_OK)
        if cannot_write:
            cannot_write_msg  = "Please check you have write access to: "
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
                if self.filetype == 'tex':
                    table_search, table_tag  = self.search_label(read_template, n)
                    table_start  = n
                    search_msg   = self.get_search_msg(table_search, table_tag, n)
                elif self.filetype == 'lyx':
                    table_tag    = re.findall(self.label, line, flags = re.IGNORECASE)[0]
                    table_search = table_tag in self.tables
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
                    warn_nolabel += " but couldn't find " + self.label
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

        msg  = ["This file was produced by 'tablefill.py'" + linesep]
        msg += ["    Template file: %s" % self.template + linesep]
        msg += ["    Input file(s): %s" % self.input + linesep]
        msg += ["To make changes, edit the input and template files." + linesep]

        if self.warning:
            msg += [linesep + "THERE WAS AN ISSUE CREATING THIS FILE!" + linesep]
            msg += [s + linesep for s in self.warn_msg.values()]
        else:
            msg += [linesep + "DO NOT EDIT THIS FILE DIRECTLY." + linesep]
        msg = linesep.join(msg).split(linesep)
        msg = ['% ' + m + linesep for m in msg]

        n   = 0
        if self.filetype == 'tex':
            head = 3 * [72 * '%' + linesep]
            tail = head
        elif self.filetype == 'lyx':
            head  = ["\\begin_layout Standard" + linesep]
            head += ["\\begin_inset Note Note" + linesep]
            head += ["status open" + linesep + linesep]
            head += ["\\begin_layout Plain Layout" + linesep]
            tail  = ["\\end_layout" + linesep]
            tail += ["\\end_inset" + linesep]
            tail += ["\\end_layout" + linesep]
            while not self.filled_template[n].startswith('\\begin_body'):
                n += 1
            n += 1
        self.filled_template[n:n] = head + msg + tail

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
