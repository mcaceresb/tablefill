#!/usr/bin/env python2
# encoding: utf-8

"""Fill LaTeX template files with external inputs

Description
-----------

tablefill.py is a python module designed to fill LaTeX and Lyx tables
with output from text files (usually output from Stata or Matlab). The
original tablefill.py does the same for LyX files only, and has fewer
error checks. Note this is intended both for command line _AND_ script
usage. Hence both the following are valid

>>> from tablefill import tablefill

$ python tablefill.py
$ chmod +x tablefill.py
$ tablefill.py

Usage
-----

tablefill.py [-h] [-v] [FLAGS] [-i [INPUT [INPUT ...]]] [-o OUTPUT]
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

See tablefill_help.txt for details on the files and the replace engine

WARNING
-------

The program currently does not handle trailing comments. If a line
doesn't start with a comment, it will replace everything in that line,
even if there is a comment halfway through.

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

Several try-catch pairs and error checks are redundant because right
now this may also be run from python and not just from the command line
(done for backwards compatibility's sake).

I also specify python 2 because I use python 3 on my local machine (as
everyone should) but am forced to use python 2 over ssh (as MIT servers
available to me come with python 2.6).
"""

# NOTE: For all my personal projects I import the print function from
# the future. You should do that also. Seriously (:

from __future__ import division, print_function
from os import linesep, path, access, W_OK, system, chdir, remove
from decimal import Decimal, ROUND_HALF_UP
from collections import Iterable as Iter
from traceback import format_exc
from operator import itemgetter
from sys import exit as sysexit
from sys import version_info
from tempfile import mktemp
import xml.etree.ElementTree as xml
import argparse
import math
import re
try:
    import numpy
    numpyok = True
except:
    numpyok = False

__program__   = "tablefill.py"
__usage__     = """[-h] [-v] [FLAGS] [-i [INPUT [INPUT ...]]] [-o OUTPUT]
                    [--pvals [PVALS [PVALS ...]]] [--stars [STARS [STARS ...]]]
                    [--xml-tables [INPUT [INPUT ...]]] [-t {auto,lyx,tex}]
                    TEMPLATE"""
__purpose__   = "Fill tagged tables in LaTeX files with external text tables"
__author__    = "Mauricio Caceres <caceres@nber.org>"
__created__   = "Thu Jun 18, 2015"
__updated__   = "Tue Apr 12, 2017"
__version__   = __program__ + " version 0.8.0 updated " + __updated__

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

    exit, exit_msg = tablefill(template       = fill.template,
                               input          = fill.input,
                               output         = fill.output,
                               filetype       = fill.ext,
                               verbose        = fill.verbose,
                               silent         = fill.silent,
                               pvals          = fill.pvals,
                               stars          = fill.stars,
                               fillc          = fill.fillc,
                               legacy_parsing = fill.legacy_parsing,
                               numpy_syntax   = fill.numpy_syntax,
                               use_floats     = fill.use_floats,
                               ignore_xml     = fill.ignore_xml,
                               xml_tables     = fill.xml_tables)

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


# Backwards-compatible string formatting
def compat_format(x):
    if version_info >= (2, 7):
        return format(x, ',d')
    else:
        import locale
        locale.setlocale(locale.LC_ALL, 'en_US')
        return locale.format("%d", x, grouping = True)


# Backwards-compatible list flattening
# http://stackoverflow.com/questions/2158395/
def flatten(l):
    if version_info >= (3, 0):
        for el in l:
            if isinstance(el, Iter) and not isinstance(el, (str, bytes)):
                for sub in flatten(el):
                    yield sub
            else:
                yield el
    else:
        for el in l:
            if isinstance(el, Iter) and not isinstance(el, basestring):
                for sub in flatten(el):
                    yield sub
            else:
                yield el


def tolist(anything):
    return anything if isinstance(anything, list) else [anything]


def tolist2(anything):
    return list(anything) if hasattr(anything, '__iter__') else [anything]


def print_verbose(prints, stuff):
    if prints:
        print(stuff)


def print_silent(silence, stuff):
    if not silence:
        print(stuff)


def custom_convert(x, func):
    if isinstance(x, func):
        return x
    else:
        try:
            return func(x)
        except:
            return None


def nested_convert(item, func):
    # if isinstance(item, list):
    if hasattr(item, '__iter__'):
        return [nested_convert(x, func) for x in item]

    return custom_convert(item, func)


# ---------------------------------------------------------------------
# tablefill

def tablefill(silent         = False,
              verbose        = True,
              filetype       = 'auto',
              pvals          = [0.1, 0.05, 0.01],
              stars          = ['*', '**', '***'],
              fillc          = False,
              legacy_parsing = False,
              numpy_syntax   = False,
              use_floats     = False,
              ignore_xml     = False,
              xml_tables     = None,
              **kwargs):
    """Fill LaTeX and LyX template files with external inputs

    Description
    -----------

    tablefill is a python function designed to fill LaTeX and LyX tables
    with output from text files (usually output from Stata or Matlab).
    The original tablefill.py does the same but only for LyX files, and
    has fewer error checks. The regexps are also slightly different.

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
        fill_engine = tablefill_internals_engine(filetype,
                                                 verbose,
                                                 silent,
                                                 pvals,
                                                 stars,
                                                 fillc,
                                                 legacy_parsing,
                                                 numpy_syntax,
                                                 use_floats,
                                                 ignore_xml,
                                                 xml_tables)

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
        self.compiler = {'tex': "xelatex ",
                         'lyx': "lyx -e pdf2 "}
        self.bibtex   = {'tex': "bibtex ",
                         'lyx': "echo Not sure how to run BiBTeX via LyX on "}

    def get_input_parser(self):
        """
        Parse command-line arguments using argparse; return parser
        """
        parser_desc    = __purpose__
        parser_prog    = __program__
        # parser_use     = __program__ + ' ' + __usage__
        parser_version = __version__
        parser = argparse.ArgumentParser(prog  = parser_prog,
                                         description = parser_desc)
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
        parser.add_argument('--pvals',
                            dest     = 'pvals',
                            type     = str,
                            nargs    = '*',
                            default  = ['0.1', '0.05', '0.01'],
                            help     = "Significance thresholds",
                            required = False)
        parser.add_argument('--stars',
                            dest     = 'stars',
                            type     = str,
                            nargs    = '*',
                            default  = ['*', '**', '***'],
                            help     = "Stars for sig thresholds " +
                                       "(enclose each in quotes)",
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
        parser.add_argument('-b', '--bibtex',
                            dest     = 'bibtex',
                            action   = 'store_true',
                            help     = "Compile BiBTeX",
                            required = False)
        parser.add_argument('-fc', '--fill-comments',
                            dest     = 'fill_comments',
                            action   = 'store_true',
                            help     = "Fill placeholders in comments",
                            required = False)
        parser.add_argument('--ignore-xml',
                            dest     = 'ignore_xml',
                            action   = 'store_true',
                            help     = "Ignore XML in template comments.",
                            required = False)
        parser.add_argument('--legacy-parsing',
                            dest     = 'legacy_parsing',
                            action   = 'store_true',
                            help     = "Legacy parsing for XML tables.",
                            required = False)
        parser.add_argument('--numpy-syntax',
                            dest     = 'numpy_syntax',
                            action   = 'store_true',
                            help     = "Numpy syntax for custom XML tables.",
                            required = False)
        parser.add_argument('--use-floats',
                            dest     = 'use_floats',
                            action   = 'store_true',
                            help     = "Use floats for custom XML python.",
                            required = False)
        parser.add_argument('--xml-tables',
                            dest     = 'xml_tables',
                            type     = str,
                            nargs    = '*',
                            metavar  = 'INPUT',
                            default  = None,
                            help     = "Files with custom XML combinations.",
                            required = False),
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
        self.stars    = self.args.stars
        self.fillc    = self.args.fill_comments
        self.legacy_parsing = self.args.legacy_parsing
        self.numpy_syntax   = self.args.numpy_syntax
        self.use_floats     = self.args.use_floats
        self.ignore_xml     = self.args.ignore_xml
        self.xml_tables     = self.args.xml_tables
        try:
            self.pvals = [float(p) for p in self.args.pvals]
            assert all([(0 < p < 1) for p in self.pvals])
        except:
            raise ValueError("--pvals only takes numbers between 0 and 1")

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

        if not self.args.compile and self.args.bibtex:
            print("NOTE: Cannot run BiBTeX without compiling." + linesep)

        if self.args.compile:
            chdir(path.dirname(path.abspath(self.output)))
            compile_program  = self.compiler[self.ext]
            compile_program += ' ' + self.output

            bibtex_auxfile   = path.splitext(path.basename(self.output))[0]
            bibtex_program   = self.bibtex[self.ext]
            bibtex_program  += ' ' + bibtex_auxfile + '.aux'

            logmsg = "Compiling in beta! Use with caution. Running"
            print_verbose(self.verbose, logmsg)
            print_verbose(self.verbose, compile_program + linesep)
            system(compile_program + linesep)
            if self.args.bibtex:
                system(bibtex_program + linesep)
                system(compile_program + linesep)
                system(compile_program + linesep)


# ---------------------------------------------------------------------
# tablefill_internals_engine

class tablefill_internals_engine:
    """
    WARNING: Internal class used by tablefill_tex
    """
    def __init__(self,
                 filetype       = 'auto',
                 verbose        = True,
                 silent         = False,
                 pvals          = [0.1, 0.05, 0.01],
                 stars          = ['*', '**', '***'],
                 fillc          = False,
                 legacy_parsing = False,
                 numpy_syntax   = False,
                 use_floats     = False,
                 ignore_xml     = False,
                 xml_tables     = None):

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

        while len(pvals) > len(stars):
            i = 1
            while '*' * i in stars:
                i += 1
            stars += ['*' * i]

        stars               = stars[:len(pvals)]
        starlist            = [(p, s) for (p, s) in zip(pvals, stars)]
        starlist.sort(key = lambda p: p[0], reverse = True)
        self.pvals          = [p for (p, s) in starlist]
        self.stars          = [s for (p, s) in starlist]
        self.fillc          = fillc
        self.legacy_parsing = legacy_parsing
        self.numpy_syntax   = numpy_syntax
        self.use_floats     = use_floats
        self.ignore_xml     = ignore_xml
        self.xml_tables     = xml_tables

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
        # The regexes are looking for
        #   - matche:   strings to escape (&, %)
        #   - match0:   either matcha or matchb
        #   - matcha:   ### for non-numeric matches or #*# for p-val parsing
        #   - matchb:   numeric matches (#\d+%?#, \#\d+,?\#)
        #   - matchc:   (-?)integer(.decimal)?
        #   - matchd:   absolute value
        #   - comments: comment
        self.tags      = '^<Tab:(.+)>' + linesep
        self.matche    = r'[^\\](%|&)'
        self.match0    = r'\\?#\|?((\d+)(,?|\\?%)?|\\?(#|\*))\|?\\?#'
        self.matcha    = r'\\?#\\?(#|\*)\\?#'
        self.matchb    = r'\\?#\|?(\d+)(,?|\\?%)\|?\\?#'
        self.matchc    = '(-?\d+)(\.?\d*)'
        self.matchd    = r'\\?#\|.{1,4}\|\\?#'
        self.comments  = '^\s*%'
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

        # Read in all the tables
        read_data  = [open(file, 'rU').readlines() for file in self.input]
        parse_data = sum(read_data, [])

        ctables = {}
        for row in parse_data:
            if re.match(self.tags, row, flags = re.IGNORECASE):
                tag = re.findall(self.tags, row, flags = re.IGNORECASE)
                tag = tag[0].lower()
                ctables[tag] = []
            else:
                clean_row_entries = [e.strip() for e in row.split('\t')]
                ctables[tag] += [clean_row_entries]

        if self.xml_tables is None and not self.ignore_xml:
            if self.legacy_parsing:
                self.parse_xml_file_legacy(ctables,
                                           self.template,
                                           prefix = '^%\s*')
            else:
                self.parse_xml_file(ctables, self.template, prefix = '^%\s*')
        else:
            if self.legacy_parsing:
                self.parse_xml_file_legacy(ctables,
                                           self.xml_tables,
                                           prefix = '')
            else:
                self.parse_xml_file(ctables, self.xml_tables, prefix = '')

        # Read in actual and custom tables
        # self.tables = {k: self.filter_missing(v) for k, v in tables.items()}
        self.tables = dict((k, self.filter_missing(list(flatten(v))))
                           for (k, v) in ctables.items())

    def parse_xml_file(self, ctables, xml_input, prefix = ''):
        """Parse custom tabs in comments/XML files

        Note that the parsing here is VERY crude (you will note it uses
        a combination of XML parsing and regexes). This is more or less
        intentional, since I want to be inflexible when using this
        feature as it is VERY experimental. As it becomes stable the
        function may move to proper XML parsing.

        Args:
            ctables (dict): Dictionary with input tables
            xml_input (list): Template or XML files with custom tags

        Kwargs:
            prefix (str): regex with prefix for XML parsing (if parsing
                          from template comments, this should be a LaTeX
                          comment, e.g. '^%\s*', as the tables would be
                          commented out in the file).

        Returns: Dictionary with resulting custom tables

        """

        # Read in all the custom tables
        xml_list     = tolist(xml_input)
        xml_template = [open(file, 'rU').readlines() for file in xml_list]
        xml_toparse  = sum(xml_template, [])

        xml_regex  = prefix
        xml_regex += "<tablefill-python\s+tag\s*=\s*['\"](.+)\s*['\"]"

        # Figure out where the custom XML tags are
        i = 0
        custom = []
        for line in xml_toparse:
            s = re.search(xml_regex, line)
            if s:
                j = i
                search = True
                while search and j <= len(xml_toparse):
                    if re.search('</\s*tablefill-python\s*>', xml_toparse[j]):
                        search = False
                    j += 1

                if not search:
                    custom += [range(i, j)]

            i += 1

        # Prase each custom XMl tag into a dictionary
        cdict = {}
        for c in custom:
            chtml    = []
            cobj     = itemgetter(*c)(xml_toparse)
            for obj in cobj:
                chtml += [re.sub('^%\s*', '', obj)]

            try:
                cxml = xml.fromstringlist(chtml)
            except:
                xml_parse_msg = "Could not parse custom XML in lines %d-%d."
                raise Warning('\t' + xml_parse_msg % (c[0], c[-1]))

            t = cxml.get('tag')
            cdict[t] = cxml

        # Get temporary string and numeric dictionaries
        strdict = ctables
        numdict = {}
        for tag, table in ctables.items():
            numdict[tag] = nested_convert(table, float)

        numpy_strdict = {}
        numpy_numdict = {}
        if numpyok:
            for tag, table in strdict.items():
                numpy_strdict[tag] = numpy.asmatrix(table)

            for tag, table in numdict.items():
                numpy_numdict[tag] = numpy.asmatrix(table)

        # Create all the custom tables using python/numpy slicing
        for tag, cxml in cdict.items():
            print_verbose(self.verbose, "\tcreating custom tab:%s" % (tag))

            csyntax = cxml.get('syntax')
            if csyntax not in [None, 'python', 'numpy']:
                xml_syntax_msg  = "Custom table '%s' requested unknown syntax"
                xml_syntax_msg += " '%s'. Specify 'python' or 'numpy'."
                raise Warning('\t' + xml_syntax_msg % (tag, csyntax))

            usenumpy = self.numpy_syntax and not csyntax == 'python'
            usenumpy = usenumpy or (csyntax == 'numpy')
            if usenumpy and not numpyok:
                xml_numpy_msg  = "Custom table '%s' requested syntax 'numpy'"
                xml_numpy_msg += " but python failed to import numpy."
                raise Warning('\t' + xml_numpy_msg % tag)

            usetype = 'float' if self.use_floats else cxml.get('type')
            if usetype not in [None, 'float', 'numeric', 'str', 'string']:
                xml_usetype_msg  = "Custom table '%s' asked unknown type"
                xml_usetype_msg += " '%s'. Specify 'float' or 'str'."
                raise Warning('\t' + xml_usetype_msg % (tag, usetype))

            if usetype in ['float', 'numeric']:
                usedict = numpy_numdict if numpyok and usenumpy else numdict
            else:
                usedict = numpy_strdict if numpyok and usenumpy else strdict

            try:
                clean_text = re.subn('\s|' + linesep, '', cxml.text)[0]
                ceval = eval(clean_text, usedict)
                if numpyok and usenumpy:
                    if usetype in ['float', 'numeric']:
                        numpy_numdict[tag] = ceval
                    else:
                        numpy_strdict[tag] = ceval

                    ceval = tolist2(ceval)
                    toadd = list(flatten([numpy.array(l) for l in ceval]))
                    strdict[tag] = nested_convert(toadd, str)
                    numdict[tag] = nested_convert(toadd, float)
                else:
                    ceval = tolist2(ceval)
                    toadd = list(flatten(ceval))
                    strdict[tag] = nested_convert(ceval, str)
                    numdict[tag] = nested_convert(ceval, float)
                    if numpyok:
                        numpy_strdict[tag] = numpy.asmatrix(strdict[tag])
                        numpy_numdict[tag] = numpy.asmatrix(numdict[tag])

            except:
                warn_custom = "custom 'tab:%s' failed to parse." % tag
                print_verbose(self.verbose, '\t' + warn_custom)
                continue

            ctables[tag] = list(nested_convert(toadd, str))

    def parse_xml_file_legacy(self, ctables, xml_input, prefix = ''):
        """Parse custom tabs in comments/XML files

        Note that the parsing here is VERY crude (you will note it uses
        a combination of XML parsing and regexes). This is more or less
        intentional, since I want to be inflexible when using this
        feature as it is VERY experimental. As it becomes stable the
        function may move to proper XML parsing.

        Args:
            ctables (dict): Dictionary with input tables
            xml_input (list): Template or XML files with custom tags

        Kwargs:
            prefix (str): regex with prefix for XML parsing (if parsing
                          from template comments, this should be a LaTeX
                          comment, e.g. '^%\s*', as the tables would be
                          commented out in the file).

        Returns: Dictionary with resulting custom tables

        """

        # Read in all the custom tables
        xml_list     = tolist(xml_input)
        xml_template = [open(file, 'rU').readlines() for file in xml_list]
        xml_toparse  = sum(xml_template, [])

        xml_regex  = prefix
        xml_regex += "<tablefill-(custom|python)\s+tag\s*=\s*['\"](.+)\s*['\"]"

        # Figure out where the custom XML tags are
        i = 0
        custom = []
        todo   = []
        for line in xml_toparse:
            s = re.search(xml_regex, line)
            if s:
                j = i
                w = s.groups()[0]
                todo  += [w]
                search = True
                while search and j <= len(xml_toparse):
                    if re.search('</\s*tablefill-%s\s*>' % w, xml_toparse[j]):
                        search = False
                    j += 1

                if not search:
                    custom += [range(i, j)]

            i += 1

        # Put them into a dictionary
        cdict = {}
        edict = {}
        for c, e in zip(custom, todo):
            chtml    = []
            cobj     = itemgetter(*c)(xml_toparse)
            for obj in cobj:
                chtml += [re.sub('^%\s*', '', obj)]

            try:
                cxml = xml.fromstringlist(chtml)
            except:
                xml_parse_msg  = "Could not parse custom XML in lines %d-%d."
                raise Warning('\t' + xml_parse_msg % (c[0], c[-1]))

            t = cxml.get('tag')
            cdict[t] = cxml
            edict[t] = e

        # Create all the custom tables using python/numpy slicing
        for tag, cxml in cdict.items():
            print_verbose(self.verbose, "\tcreating custom tab:%s" % (tag))

            csyntax = cxml.get('syntax')
            if csyntax not in [None, 'python', 'numpy']:
                xml_syntax_msg  = "Custom table '%s' requested unknown syntax"
                xml_syntax_msg += " '%s'. Specify 'python' or 'numpy'."
                raise Warning('\t' + xml_syntax_msg % (tag, csyntax))

            usenumpy = self.numpy_syntax and not csyntax == 'python'
            usenumpy = usenumpy or (csyntax == 'numpy')
            if usenumpy and not numpyok:
                xml_numpy_msg  = "Custom table '%s' requested syntax 'numpy'"
                xml_numpy_msg += " but python failed to import numpy."
                raise Warning('\t' + xml_numpy_msg % tag)

            convert = 'float' if self.use_floats else cxml.get('convert')
            if convert not in [None, 'float', 'str']:
                xml_convert_msg  = "Custom table '%s' asked unknown conversion"
                xml_convert_msg += " '%s'. Specify 'float' or 'str'."
                raise Warning('\t' + xml_convert_msg % (tag, convert))

            if edict[tag] == 'python':
                inputs  = [l.strip() for l in cxml.get('inputs').split(',')]
                inputs  = filter(lambda a: a != '', inputs)
                xmlexec = mktemp()
                with open(xmlexec, "w+") as tmp:
                    tmp.writelines(cxml.text)

                python = {}
                for table in inputs:
                    ptable = tolist(ctables[table])
                    if convert == 'float':
                        ptable = nested_convert(ptable, float)

                    if numpyok and usenumpy:
                        ptable = numpy.asmatrix(ptable)

                    python[table] = ptable

                try:
                    execfile(xmlexec, python)
                except:
                    xml_python_msg = "Custom code for '%s' failed to run."
                    raise Warning('\t' + xml_python_msg % tag)

                remove(xmlexec)
                try:
                    table_tag = python[tag]
                except:
                    xml_python_msg = "Code for '%s' did not create 'tag'"
                    raise Warning('\t' + xml_python_msg % tag)

                if numpyok and usenumpy:
                    table_tag = numpy.array(table_tag)

                table_tag = list(flatten(table_tag))
                if convert == 'float':
                    table_tag = nested_convert(table_tag, str)

                ctables[tag] = table_tag
            else:
                ctables[tag] = table_tag = []
                for combine in cxml.findall('combine'):
                    ctag  = combine.get('tag')
                    clist = ctables[ctag]
                    if numpyok and usenumpy:
                        clist = numpy.asmatrix(clist)

                    for subset in combine.text.split(';'):
                        clean_subset = subset.strip(linesep).replace(' ', '')
                        if clean_subset == '':
                            continue

                        try:
                            add = eval("clist%s" % (clean_subset))
                            if numpyok and usenumpy:
                                add = numpy.array(add)

                            table_tag += [add]
                        except:
                            warn_custom  = "custom 'tab:%s' failed to subset "
                            warn_custom += "'%s' from 'tab:%s'; will continue."
                            warn_msg = warn_custom % (tag, clean_subset, ctag)
                            print_verbose(self.verbose, warn_msg)
                            continue

                ctables[tag] = list(flatten(table_tag))

    def filter_missing(self, string_list):
        filters = ['.', '', 'NA', 'nan', 'NaN', 'None']
        return filter(lambda a: a not in filters, string_list)

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
                if re.search(self.comments, line.strip()) and not self.fillc:
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
        i = 0
        force_stop = False
        starts = tablen
        match0 = re.search(self.match0, line)
        while match0 and not force_stop:
            s, e = match0.span()
            cell = line[s:e]
            matcha = re.search(self.matcha, cell)
            matchb = re.search(self.matchb, cell)

            if len(table) > tablen:
                # Replace all pattern A matches (simply replace the text)
                if matcha:
                    entry    = re.sub(self.matche, '\\\\\\1', table[tablen])
                    if '*' in matcha.groups():
                        cell = self.parse_pval_to_stars(cell, entry)
                    else:
                        cell = re.sub(self.matcha, entry, cell, count = 1)

                    line    = re.sub(self.matcha, cell, line, count = 1)
                    tablen += 1

                # Replace all pattern B matches (round, comma and % format)
                if matchb:
                    entry   = re.sub(self.matche, '\\\\\\1', table[tablen])
                    cell    = self.round_and_format(cell, entry)
                    line    = re.sub(self.matchb, cell, line, count = 1)
                    tablen += 1
            else:
                if matcha or matchb:
                    starts  = tablen if tablen - starts == i + 1 else starts
                    tablen += 1

                force_stop = True

            match0 = re.search(self.match0, line)
            i += 1

        return line, tablen, starts

    def round_and_format(self, cell, entry):
        """
        Rounds entry according to the format in cell. Note Decimal's
        quantize makes the object have the same number of significant
        digits as the input passed. format(str, ',d') returns str with
        comma as thousands separator.
        """
        precision, comma = re.findall(self.matchb, cell)[0]
        precision = int(precision)
        roundas   = 0 if precision == 0 else pow(10, -precision)
        roundas   = Decimal(str(roundas))
        dentry    = 100 * Decimal(entry) if '%' in comma else Decimal(entry)
        dentry    = abs(dentry) if re.search(self.matchd, cell) else dentry
        rounded   = str(dentry.quantize(roundas, rounding = ROUND_HALF_UP))
        if ',' in comma:
            integer_part, decimal_part = re.findall(self.matchc, rounded)[0]
            neg      = '-' if re.match('^-0', integer_part) else ''
            rounded  = neg + compat_format(int(integer_part)) + decimal_part
        return re.sub(self.matchb, rounded, cell, count = 1)

    def parse_pval_to_stars(self, cell, entry):
        """
        Parse a p-value to significance symbols. The default is to
        parse 0.1, 0.05, 0.01 to *, **, ***, but the user can specify
        arbitrary thresholds and symbols.
        """
        pos  = sum([float(entry) < p for p in self.pvals]) - 1
        star = '' if pos < 0 else self.stars[pos]
        return re.sub(self.matcha, star, cell, count = 1)

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
