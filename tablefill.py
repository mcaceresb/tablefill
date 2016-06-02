#!/usr/bin/env python
# encoding: utf-8

"""Fill LaTeX template files with external inputs

Description
-----------

tablefill.py is a python module designed to fill LaTeX and Lyx tables
with output from text files (usually output from Stata or Matlab). The
original tablefill.py does the same for LyX files only, and has fewer
error checks. For backwards compatibility, this also works as a python
module, meaning

>>> from tablefill import tablefill

Will allow usage of tablefill wherever currently in use. However, it
can also be called like any command-line tool

$ python tablefill.py --help

Usage
-----

tablefill.py [-h] [-v] [-i [INPUT [INPUT ...]]] [-o OUTPUT]
             [-t {auto,lyx,tex}] [FLAGS] TEMPLATE

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
  --verbose             Verbose printing
  --silent              Try to say nothing

See tablefill_help.txt for details on the files and the replace engine

Examples
--------

$ ls
tablefill.py
test.tex
test_table.txt
$ python tablefill.py test.tex --force --silent
$ ls
tablefill.py
test.tex
test_table.txt
test_filled.txt
$ python tablefill.py test.tex -i test_table.txt -o output.tex --verbose

Notes
-----

Several try-catch pairs and error checks are redundant because right now
as this is meant to be backwards-compatible and can be called from other
python scripts or used directly from the command line.
"""

# NOTE: For all my personal projects I import the print function from
# the future. You should do that also. Seriously (:

from __future__ import division, print_function
from traceback import format_exc
from os import linesep, path, access, W_OK, system
from decimal import Decimal, ROUND_HALF_UP
from sys import exit as sysexit
import argparse
import re

__program__   = "tablefill.py"
__usage__     = """[-h] [-v] [-i [INPUT [INPUT ...]]] [-o OUTPUT]
                    [-t {auto,lyx,tex}] [-f] [-c] TEMPLATE"""
__purpose__   = "Fill tagged tables in LaTeX files with external text tables"
__author__    = "Mauricio Caceres <caceres@nber.org>"
__created__   = "Thu Jun 18, 2015"
__updated__   = "Wed Mar 30, 2016"
__version__   = __program__ + " version 0.3.0 updated " + __updated__

# Define basestring in a backwards-compatible way
try:
    "" is basestring
except NameError:
    basestring = str

def main():
    """
    WARNING: This function expects command-line inputs to exist.
    """

    fill = tablefill_internals_cliparse()
    fill.get_input_parser()
    fill.get_parsed_arguments()
    fill.get_argument_strings()
    fill.get_file_type()
    print_verbose(fill.verbose, "Arguments look OK. Will run tablefill.")

    exit, exit_msg = tablefill(template = fill.template,
                               input    = fill.input,
                               output   = fill.output,
                               filetype = fill.ext,
                               verbose  = fill.verbose,
                               silent   = fill.silent)

    if exit == 'SUCCESS':
        fill.get_compiled()
        sysexit(0)
    elif exit == 'WARNING':
        print_silent(fill.silent, "Exit status came with a warning")
        print_silent(fill.silent, "Output might not be as expected!")
        print_silent(fill.silent, "Rerun program with --verbose option.")
        fill.get_compiled()
        sysexit(-1)
    elif exit == 'ERROR':
        fillerror_msg  = 'ERROR while filling table.'
        fillerror_msg += ' Check function call.' + linesep
        print_silent(fill.silent, fillerror_msg)
        fill.parser.print_usage()
        sysexit(1)


def tolist(anything):
    return anything if isinstance(anything, list) else [anything]


def print_verbose(prints, stuff):
    if prints:
        print(stuff)


def print_silent(silence, stuff):
    if not silence:
        print(stuff)

# ---------------------------------------------------------------------
# tablefill


def tablefill(silent = False, verbose = True, filetype = 'auto', **kwargs):
    """Fill LaTeX and LyX template files with external inputs

    Description
    -----------

    tablefill is a python function designed to fill LaTeX and LyX tables
    with output from text files (usually output from Stata or Matlab).
    The original tablefill.py does the same but only for LyX files, and
    has fewer error checks. The regexps are also slightly improved.

    Required Input
    --------------

    See 'tablefill_help.txt' for details on the format of these files.

    template : str
        Name of user-written document to use as basis for update
    input : str
        Space-separated list of files with tables to be used in update.
    output : str
        Filled template to be produced.

    Optional Input
    --------------
    verbose : bool
        print a lot of info
    silent : bool
        try to print nothing at all
    filetype : str
        auto, lyx, or tex

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
        verbose = verbose and not silent
        logmsg  = "Parsing arguments..."
        print_verbose(verbose, logmsg)
        fill_engine = tablefill_internals_engine(filetype, verbose, silent)
        fill_engine.get_parsed_arguments(kwargs)
        fill_engine.get_file_type()
        fill_engine.get_regexps()

        logmsg  = "Parsing tables in into dictionary:" + linesep + '\t'
        logmsg += (linesep + '\t').join(tolist(fill_engine.input))
        print_verbose(verbose, logmsg)
        fill_engine.get_parsed_tables()

        logmsg  = "Searching for labels in template:" + linesep + '\t'
        logmsg += (linesep + '\t').join(tolist(fill_engine.template))
        print_verbose(verbose, logmsg + linesep)
        fill_engine.get_filled_template()

        logmsg = "Adding warning that this was automatically generated..."
        print_verbose(verbose, logmsg)
        fill_engine.get_notification_message()

        logmsg = "Writing to output file '%s'" % fill_engine.output
        print_verbose(verbose, logmsg)
        fill_engine.write_to_output(fill_engine.filled_template)

        logmsg = "Wrapping up..." + linesep
        print_verbose(verbose, logmsg)
        fill_engine.get_exit_message()
        print_silent(silent, fill_engine.exit + '!')
        print_silent(silent, fill_engine.exit_msg)
        return fill_engine.exit, fill_engine.exit_msg
    except:
        exit_msg = format_exc()
        exit     = 'ERROR'
        print_silent(silent, exit + '!')
        print_silent(silent, exit_msg)
        return exit, exit_msg

# ---------------------------------------------------------------------
# tablefill_internals_cliparse


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
        parser.add_argument('--verbose',
                            dest     = 'verbose',
                            action   = 'store_true',
                            help     = "Verbose printing",
                            required = False)
        parser.add_argument('--silent',
                            dest     = 'silent',
                            action   = 'store_true',
                            help     = "No printing",
                            required = False)
        self.parser = parser

    def get_parsed_arguments(self):
        """
        Get arguments; if input and output names are missing, guess them
        (only guess with the --force option, otherwise don't run).
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
                    args.input = self.rename_file(template_name,
                                                  '_table', 'txt')
                if 'OUTPUT' in missing_args:
                    args.output = self.rename_file(template_name,
                                                   '_filled')

        self.args = args

    def rename_file(self, base, add, ext = None):
        out  = path.splitext(base)
        add += out[-1] if ext is None else '.' + ext
        return [out[0] + add]

    def get_argument_strings(self):
        """
        Get arguments as strings to pass to tablefill
        """
        self.template = path.abspath(self.args.template[0])
        self.input    = ' '.join([path.abspath(f) for f in self.args.input])
        self.output   = path.abspath(self.args.output[0])
        self.silent   = self.args.silent
        self.verbose  = self.args.verbose and not self.args.silent

        args_msg  = linesep + "I found these arguments:"
        args_msg += linesep + "template = %s" % self.template
        args_msg += linesep + "input    = %s" % self.input
        args_msg += linesep + "output   = %s" % self.output
        args_msg += linesep
        print_verbose(self.verbose, args_msg)

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
                logmsg = "NOTE: Automatically detected input type as %s" % ext
                print_verbose(self.verbose, logmsg)
        else:
            self.ext = inext
            if ext != inext:
                mismatch_msg  = "NOTE: Provided template type '%s' "
                mismatch_msg += "does not match detected template type '%s'. "
                mismatch_msg += linesep + "Using program associated with '%s'"
                mismatch_msg  = mismatch_msg % (inext, ext, inext)
                print_verbose(self.verbose, mismatch_msg + linesep)

    def get_compiled(self):
        """
        Compile the filled template with the corresponding program.
        """
        if self.args.compile:
            compile_program  = self.compiler[self.ext]
            compile_program += ' ' + self.output
            logmsg = "Compiling in beta! Use with caution. Running"
            print_verbose(self.verbose, logmsg)
            print_verbose(self.verbose, compile_program + linesep)
            system(compile_program + linesep)

# ---------------------------------------------------------------------
# tablefill_internals_engine


class tablefill_internals_engine:
    """
    WARNING: Internal class used by tablefill_tex
    """
    def __init__(self, filetype = 'auto', verbose = True, silent = False):
        # Get file type
        self.filetype     = filetype.lower()
        if self.filetype not in ['auto', 'lyx', 'tex']:
            unknown_type  = "File type '%s' not known."
            unknown_type += " Expecting 'auto' or a .lyx or .tex file."
            unknown_type  = unknown_type % filetype
            raise KeyError(unknown_type)

        self.warn_msg  = {'nomatch': '',
                          'notable': '',
                          'nolabel': '',
                          'toolong': ''}
        self.warnings  = {'nomatch': [],
                          'notable': [],
                          'nolabel': [],
                          'toolong': []}
        self.warn_pre  = ""
        self.verbose   = verbose and not silent
        self.silent    = silent

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
            msg = [msg % (k, v.__class__.__name__)
                   for k, v in mismatched_types]
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
            missing_outdir_msg  = "Please check the directory exists:"
            missing_outdir_msg += outdir
            raise IOError(missing_outdir_msg)

        cannot_write = not access(outdir, W_OK)
        if cannot_write:
            cannot_write_msg  = "Please check you have write access to: "
            cannot_write_msg += outdir
            raise IOError(cannot_write_msg)

    def get_file_type(self):
        """
        Get file type and check if it matches the compilation type that
        was requested, if one was requested.
        """
        fname = path.basename(self.template)
        ext   = path.splitext(fname)[-1].lower().strip('. ')
        inext = self.filetype
        if inext == 'auto':
            if ext not in ['tex', 'lyx']:
                unknown_type  = "Option filetype = 'auto' detected type '%s'"
                unknown_type += " but was expecting a .lyx or .tex file."
                unknown_type  = unknown_type % ext
                raise KeyError(unknown_type)
            else:
                self.filetype = ext.lower()
                logmsg = "NOTE: Automatically detected input type as %s" % ext
                print_verbose(self.verbose, logmsg)
        elif ext != inext:
            mismatch_msg  = "NOTE: Provided template type '%s' "
            mismatch_msg += "does not match detected template type '%s'"
            mismatch_msg += linesep + "Will use program associated with '%s'"
            mismatch_msg  = mismatch_msg % (inext, ext, inext)
            print_verbose(self.verbose, mismatch_msg + linesep)

    def get_regexps(self):
        """
        Define the regular expressions to use to find a token to fill,
        the start/end of a table, etc. based on the file type.
        """
        self.tags      = '^<Tab:(.+)>' + linesep
        self.matcha    = r'\\*#\\*#\\*#'       # Matches ### and \#\#\#
        self.matchb    = r'\\*#(\d+)(,*)\\*#'  # Matches #\d+# and \#\d+,*\#
        self.matchc    = '(-*\d+)(\.*\d*)'     # Matches (-)integer(.decimal)
        self.comments  = '^%'                  # Matches comment
        if self.filetype == 'tex':
            self.begin = r'.*\\begin{table}.*'
            self.end   = r'.*\\end{table}.*'
            self.label = r'.*\\label{tab:(.+)}'
        elif self.filetype == 'lyx':
            self.begin = r'.*\\begin_inset Float table.*'
            self.end   = r'</lyxtabular>'
            self.label = r'name "tab:(.+)"'

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
                clean_row_entries = [e.strip() for e in row.split('\t')]
                tables[tag] += clean_row_entries
        # self.tables = {k: self.filter_missing(v) for k, v in tables.items()}
        self.tables = dict((k, self.filter_missing(v))
                           for (k, v) in tables.items())

    def filter_missing(self, string_list):
        return filter(lambda a: a != '.' and a != '', string_list)

    def get_filled_template(self):
        """
        Fill template file using table input(s). The idea is to read the
        template line by line and if the line matches the start of a
        table, search for the table label (to match to the input tags).

        If no label, print a note to that effect. If there is a label,
        grab the corresponding matrix from the inputs, and replace the
        tokens with the input values until the values run out or we
        reach the end of the table. Repeat for all template lines.

        This function raises warnings for
            - Token matched but in a commented out line.
            - Too many tokens in table and not enough values.
            - Token outside of begin/end table statement.
            - Table label does not match tag in inputs.
        """
        read_template = open(self.template, 'rU').readlines()
        table_start   = -1
        table_search  = False
        table_tag     = ''
        table_entry   = 0

        warn = self.warn_pre
        for n in range(len(read_template)):
            line = read_template[n]
            if not table_search and re.search(self.begin, line):
                table_search, table_tag = self.search_label(read_template, n)
                table_start  = n
                search_msg   = self.get_search_msg(table_search, table_tag, n)
                print_verbose(self.verbose, search_msg)

            if re.search(self.matcha, line) or re.search(self.matchb, line):
                if re.search(self.comments, line.strip()):
                    warn_incomments  = "Line %d matches #(#|\d+,*)#"
                    warn_incomments += " but it appears to be commented out."
                    warn_incomments += " Skipping..."
                    print_verbose(self.verbose, warn + warn_incomments % n)
                elif table_search:
                    table  = self.tables[table_tag]
                    ntable = len(table)
                    update = self.replace_line(line, table, table_entry)
                    read_template[n], table_entry, entry_start = update
                    if ntable < table_entry:
                        self.warnings['toolong'] += [str(n)]

                        nstart        = entry_start + 1
                        nend          = table_entry
                        aux_toolong   = (n, nstart, nend, table_tag, ntable)

                        warn_toolong  = "Line %d has matches %d-%d for table"
                        warn_toolong += " %s but the corresponding input"
                        warn_toolong += " matrix only has %d entries."
                        warn_toolong += " Skipping..."
                        warn_toolong  = warn_toolong % aux_toolong

                        print_verbose(self.verbose, warn + warn_toolong)
                elif table_start == -1:
                    self.warnings['notable'] += [str(n)]

                    warn_notable  = "Line %d matches #(#|\d+,*)# but"
                    warn_notable += " is not in begin/end table statements."
                    warn_notable += " Skipping..."

                    print_verbose(self.verbose, warn + warn_notable % n)
                elif table_tag == '':
                    self.warnings['nolabel'] += [str(n)]
                    warn_nolabel  = "Line %d matches #(#|\d+,*)#"
                    warn_nolabel += " but couldn't find " + self.label
                    warn_nolabel += " Skipping..."
                    print_verbose(self.verbose, warn + warn_nolabel % n)

            if re.search(self.end, line) and table_search:
                search_msg   = "Table '%s' in line %d ended in line %d."
                search_msg  += " %d replacements were made." % table_entry
                search_msg   = search_msg % (table_tag, table_start, n)
                print_verbose(self.verbose, search_msg + linesep)

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
        searchmatch = re.search(self.label, searchline,
                                flags = re.IGNORECASE)
        searchend   = re.search(self.end, searchline)
        while not searchmatch and not searchend:
            N += 1
            searchline  = intext[N]
            searchmatch = re.search(self.label, searchline,
                                    flags = re.IGNORECASE)
            searchend   = re.search(self.end, searchline)
        if not searchend and searchmatch:
            label = re.findall(self.label, searchline,
                               flags = re.IGNORECASE)[0]
            label = label.strip('{}"').lower()
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
                warn_nomatch  = linesep + self.warn_pre
                warn_nomatch += "NO MACHES FOR '%s' IN" + linesep + '\t'
                warn_nomatch += (linesep + '\t').join(self.input)
                warn_nomatch += linesep + "Please check input file(s)"
                warn_nomatch  = warn_nomatch % tag + linesep
        return search_msg + warn_nomatch

    def replace_line(self, line, table, tablen):
        """
        Replaces all matches of #(#|\d+,*)#. Splits by & because that's
        how LaTeX delimits tables. Returns how many values it replaced
        because LaTeX can have any number of entries per line.
        """
        starts  = tablen
        linesep = line.split('&')
        for i in range(len(linesep)):
            cell   = linesep[i]
            matcha = re.search(self.matcha, cell)
            matchb = re.search(self.matchb, cell)
            if len(table) > tablen:
                if matcha:
                    entry      = table[tablen]
                    linesep[i] = re.sub(self.matcha, entry, cell)
                    tablen    += 1
                elif matchb:
                    entry      = table[tablen]
                    linesep[i] = self.round_and_format(cell, entry)
                    tablen    += 1
            else:
                if matcha or matchb:
                    starts  = tablen if tablen - starts == i + 1 else starts
                    tablen += 1

        line = '&'.join(linesep)
        return line, tablen, starts

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
        rounded   = str(Decimal(entry).quantize(roundas,
                                                rounding = ROUND_HALF_UP))
        if ',' in comma:
            integer_part, decimal_part = re.findall(self.matchc, rounded)[0]
            rounded = format(int(integer_part), ',d') + decimal_part
        return re.sub(self.matchb, rounded, cell)

    def get_notification_message(self):
        """
        Inserts a message atop the LaTeX file that this was created by
        tablefill_tex. includes the following warnings, when applicable
            - #(#|\d+,*)# is found on a line outside a table environment
            - #(#|\d+,*)# is on a table environment with no label
            - A tabular environment's label has no match in tables.txt
        """
        n   = 0
        if self.filetype == 'tex':
            head  = 3 * [72 * '%' + linesep]
            tail  = head
            pre   = '% '
            after = linesep
        elif self.filetype == 'lyx':
            pre   = "\\begin_layout Plain Layout" + linesep
            after = "\\end_layout" + linesep
            head  = ["\\begin_layout Standard" + linesep]
            head += ["\\begin_inset Note Note" + linesep]
            head += ["status open" + linesep + linesep]
            tail  = ["\\end_inset" + linesep]
            tail += ["\\end_layout" + linesep]
            while not self.filled_template[n].startswith('\\begin_body'):
                n += 1
            n += 1

        for key in self.warnings.keys():
            self.warnings[key] = ', '.join(self.warnings[key])

        self.warning = True in [v != '' for v in self.warnings.values()]
        if self.warning:
            fillt  = (self.template, self.input)
            fillh  = self.template
            fillt  = ("'template' file", "'input' file(s)")
            fillh  = "'template' file"
            imtags = "WARNING: These tags were in %s but not in %s: " % fillt
            imhead = "WARNING: Lines in %s matching '#(#|d+,*)#'" % fillh
            imend  = linesep + pre if self.filetype == 'tex' else '; '
            imend += "Output '%s' may not compile!" % self.output

        if self.warnings['nomatch'] != '':
            self.warn_msg['nomatch']  = imtags
            self.warn_msg['nomatch'] += self.warnings['nomatch'] + imend

        if self.warnings['notable'] != '':
            self.warn_msg['notable']  = imhead
            self.warn_msg['notable'] += " were not in a table environment: "
            self.warn_msg['notable'] += self.warnings['notable'] + imend

        if self.warnings['nolabel'] != '':
            self.warn_msg['nolabel']  = imhead
            self.warn_msg['nolabel'] += " but the environment had no label: "
            self.warn_msg['nolabel'] += self.warnings['nolabel'] + imend

        if self.warnings['toolong'] != '':
            self.warn_msg['toolong']  = imhead
            self.warn_msg['toolong'] += " but their corresponding input matrix"
            self.warn_msg['toolong'] += " ran out of entries: "
            self.warn_msg['toolong'] += self.warnings['toolong'] + imend

        msg  = ["This file was produced by 'tablefill.py'"]
        msg += ["\tTemplate file: %s" % self.template]
        msg += ["\tInput file(s): %s" % self.input]
        msg += ["To make changes, edit the input and template files."]
        msg += [pre + after]

        if self.warning:
            msg += ["THERE WAS AN ISSUE CREATING THIS FILE!"]
            msg += [s for s in self.warn_msg.values()]
        else:
            msg += ["DO NOT EDIT THIS FILE DIRECTLY."]

        msg = [pre + m + after for m in msg]
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

# ---------------------------------------------------------------------
# Run the function

if __name__ == "__main__":
    main()
