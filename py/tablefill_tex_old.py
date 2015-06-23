# ---------------------------------------------------------------------
# Program:  tablefill_tex.py
# Based on: tablefill_lyx.py
# Version:  0.2.0
# Author:   Mauricio Caceres <caceres@nber.org>

from traceback import format_exc
from decimal import Decimal, ROUND_HALF_UP
from os import linesep, path, access, W_OK
import re

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
# tablefill_tex_internals

class tablefill_tex_internals:
    """
    Aux functions for tablefill_tex
    """
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
                search_msg  += "%d replacements were made." % table_entry
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
