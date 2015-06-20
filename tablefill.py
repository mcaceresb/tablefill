#!/usr/bin/env python
# encoding: utf-8

from __future__ import division
from traceback import format_exc
# from decimal import Decimal, ROUND_HALF_UP
# from os import linesep, path, access, W_OK
from os import linesep, path
import argparse
# import re

__program__   = "tablefill"
__usage__     = "[-h] [-i [INPUT [INPUT ...]]] [-o OUTPUT] [-f] TEMPLATE"
__purpose__   = "Fill tagged tables in LaTeX files with external text tables"
__author__    = "Mauricio Caceres <caceres@nber.org>"
__created__   = "Thu Jun 18"
__updated__   = "Sat Jun 20"
__version__   = __program__ + " version 0.1.0 updated " + __updated__

# ---------------------------------------------------------------------
# Parse command-line arguments and pass them to tablefill_tex

def tablefill():
    parser = get_input_parser()
    args   = get_parsed_arguments(parser)
    try:
        template    = path.abspath(args.template[0])
        input       = ' '.join([path.abspath(f) for f in args.input])
        output      = path.abspath(args.output[0])
        print linesep + "I found these arguments:"
        print 'template = %s' % template
        print 'input    = %s' % input
        print 'output   = %s' % output
        status, msg = tablefill_tex(template = template,
                                    input = input,
                                    output = output)
    except:
        print format_exc()
        print parser.print_usage()


def get_input_parser():
    parser_desc    = __purpose__
    parser_prog    = __program__
    parser_use     = __program__ + ' ' + __usage__
    parser_version = __version__
    parser = argparse.ArgumentParser(prog = parser_prog,
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
    return parser


def get_parsed_arguments(parser):
    args = parser.parse_args()
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
                args.input = rename_file(template_name, '_table', 'txt')
            if 'OUTPUT' in missing_args:
                args.output = rename_file(template_name, '_filled')
    return args


def rename_file(base, add, ext = None):
    out  = path.splitext(base)
    add += out[-1] if ext is None else '.' + ext
    return [out[0] + add]

# ---------------------------------------------------------------------
# tablefill_tex

def tablefill_tex(**kwargs):
    return 'SUCCESS', 'Testing'

# ---------------------------------------------------------------------
# Run function

if __name__ == "__main__":
    tablefill()
