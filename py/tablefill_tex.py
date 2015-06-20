#! /usr/bin/env python
# ---------------------------------------------------------------------
# Program:  tablefill_tex.py
# Based on: tablefill.py
# Version:  0.1.0
# Author:   Mauricio Caceres <caceres@nber.org>

from decimal import Decimal, ROUND_HALF_UP
from traceback import format_exc
from os import linesep, path
import re
# import warnings

# ---------------------------------------------------------------------
# Main function

class tablefill_tex:
    """Fill tagged tables in LaTeX Files with external text tables

    WARNING
    -------
    1. Currently, soft warnings are given for the following
        - #(#|\d+,*)# is found on a line outside a table environment
        - #(#|\d+,*)# is on a table environment with no label
        - A tabular environment's label has no match in tables.txt

       The version of tablefill.py I have ignores these three cases and
       gives no indication of these issues.

    2. New lines of the table must be on new lines of the .tex file
    3. Checks for #(#|\d+,*)# inside tables, not tabular. Sorry!

    Note
    ----
    Based on tablefill.py for updating LyX files. See ../tablefill_readme.txt

    I simplified several steps from tablefill. However, this function is more
    complicated because
        - The function now checks inputs are correct (names and type)
        - The function now checks if input files exist
        - The function gives soft warnings for the cases mentioned above
        - labels in LaTeX can be anywhere in the table environment
        - .tex can have several matches of the pattern in the same line
        - # is a special character in TeX and is escaped by \#; hence I
          wrote regexps to match both #(#|\d+,*)# and \#(\#|\d+,*)\#

    Input
    -----
    input : str
        Space-separated list of files with tables to be used in update
    template : str
        Name of document to use as basis for update
    output : str
        Script updates template using input and places text in output

    Mechanism
    ---------
    For each tab:label in input and corresponding tab:label in output
        input value <- output value
        ###         <- same value
        #\d+#       <- rounded to \d+ digits
        #\d+,#      <- rounded to \d+ digits w/thousands comma separator
    """

    def __init__(self, **kwargs):
        try:
            print "Parsing arguments..."
            self.f_parse_args(kwargs)
            self.f_check_files_exist()

            print "Parsing tables in '%s' into dictionary." % self.input
            tables = self.f_parse_tables()

            print "Searching for labels in template '%s'" % self.template + linesep
            self.f_regexps_and_issues()
            tex_text = self.f_insert_tables(tables)
            self.f_check_issues()

            print "Adding warning that this was automatically generated..."
            tex_text, ninserted = self.f_insert_warning(tex_text)

            print "Writing to output file '%s'" % self.output
            self.f_write_to_output(tex_text)

            print "Wrapping up..." + linesep
            if self.problem:
                exitmsg = ["The following issues were found:"]
                exitmsg += filter(None, [None if im == '' else im + linesep
                                         for im in self.issuesmsg.values()])
                self.exitmsg = linesep.join(exitmsg)
                self.exit    = 'WARNINGS'
            else:
                exitmsg = "All tags in '%s' successfully filled by 'tablefill.py'"
                exitmsg += linesep + "Output can be found in '%s'" + linesep
                self.exitmsg = exitmsg % (self.template, self.output)
                self.exit    = 'SUCCESS'
            print self.exit + '!'
            print self.exitmsg
        except:
            self.exitmsg = format_exc()
            self.exit    = 'ERROR'
            print self.exit + '!'
            print self.exitmsg

    def f_parse_args(self, kwargs):
        arguments  = ['input', 'template', 'output']
        argmissing = filter(lambda arg: arg not in kwargs.keys(), arguments)
        if argmissing != []:
            raise KeyError("Missing arguments: " + ', '.join(argmissing))

        notstr  = filter(lambda t: not isinstance(t[1], basestring),
                         kwargs.items())
        if notstr != []:
            msg = "Expected str for '%s' but got type '%s'"
            msg = [msg % (k, v.__class__.__name__) for k, v in notstr]
            raise TypeError(linesep.join(msg))

        self.template = path.abspath(kwargs['template'])
        self.output   = path.abspath(kwargs['output'])
        self.input    = [path.abspath(ins) for ins in kwargs['input'].split()]

    def f_check_files_exist(self):
        pleasemsg = 'Please check that the following are available:' + linesep
        allfiles  = self.input + [self.template, self.output]
        missing   = filter(lambda file: not path.isfile(file), allfiles)
        if missing != []:
            raise IOError(pleasemsg + linesep.join(missing))

    def f_regexps_and_issues(self):
        self.issuesmsg = {'nomatch': '', 'notable': '', 'nolabel': ''}
        self.issues    = {'nomatch': [], 'notable': [], 'nolabel': []}
        self.begin     = r'.*\\begin{table}.*'
        self.end       = r'.*\\end{table}.*'
        self.label     = r'.*\\label{tab:(.+)}'
        self.matcha    = r'\\*#\\*#\\*#'      # Matches ###
        self.matchb    = r'\\*#(\d+)(,*)\\*#' # Matches #\d+,#
        self.matchc    = '(-*\d+)(\.*\d*)'    # Matches (-)integer(.decimal)

    # ---------------------------------------------------------------------
    # parse tables and values as dict

    def f_parse_tables(self):
        read_data  = [open(file, 'rU').readlines() for file in self.input]
        parse_data = sum(read_data, [])
        tagpattern = '^<Tab:(.+)>' + linesep
        tables = {}
        for row in parse_data:
            if re.match(tagpattern, row, flags = re.IGNORECASE):
                tag = re.findall(tagpattern, row, flags = re.IGNORECASE)[0].lower()
                tables[tag] = []
            else:
                clean_row_entries = [entry.strip() for entry in row.split('\t')]
                tables[tag] += clean_row_entries
        return {k: self.a_filter_missing(v) for k, v in tables.items()}

    def a_filter_missing(self, string_list):
        return filter(lambda a: a != '.' and a != '', string_list)

    # ---------------------------------------------------------------------
    # Replace placeholders with values

    # Ok, so, doing this for LaTeX is a bit more complicated because a label
    # can be anywhere ): Also, the tabular environment can be arranged in
    # any manner the author so desires. The code
    #   1. Searches for a \begin{table} statement
    #   2. Searches for a \label{tab:label} BEFORE an \end{table} statement
    #   3. If the label is in the list of tables, start processing
    #   4. Find all occurrences of ###, #\d+,*# in each line and replace
    #   5. Currently, soft warnings are given for the following
    #       - #(#|\d+,*)# is found on a line outside a table environment
    #       - #(#|\d+,*)# is on a table environment with no label
    #       - A tabular environment's label has no match in tables.txt
    def f_insert_tables(self, tables):
        tex_text   = open(self.template, 'rU').readlines()
        search     = False
        tag        = ''
        entryn     = 0
        tablestart = -1

        for n in range(len(tex_text)):
            line = tex_text[n]
            if not search and re.search(self.begin, line):
                search, tag  = self.a_search_label(tex_text, n, tables)
                tablestart   = n
                searchmsg, warn_nomatch = self.a_get_search_msg(search, tag, n)
                print searchmsg + warn_nomatch

            if re.search(self.matcha, line) or re.search(self.matchb, line):
                if search:
                    table = tables[tag]
                    matched, entryn = self.a_replace_line(line, table, entryn)
                    tex_text[n] = matched
                elif tablestart == -1:
                    self.issues['notable'] += [str(n)]
                    warn_notable = "Line %d matches #(#|\d+,*)#"
                    warn_notable += " but is not in begin/end table statements."
                    warn_notable += " Skipping..."
                    print warn_notable % n
                elif tag == '':
                    self.issues['nolabel'] += [str(n)]
                    warn_nolabel = "Line %d matches #(#|\d+,*)#"
                    warn_nolabel += " but couldn't find \\label{tab:.+}."
                    warn_nolabel += " Skipping..."
                    print warn_nolabel % n

            if re.search(self.end, line):
                searchmsg = "Table '%s' starting in line %d ended in line %d. "
                searchmsg += "%d replacements were made." + linesep
                print searchmsg % (tag, tablestart, n, entryn)
                tag    = ''
                search = False
                entryn = 0
                tablestart = -1

        return tex_text

    # Search for label until \end{table} statement Returns label value (''
    # if none is found) and whether it matches a tag in the tables file
    def a_search_label(self, intext, start, tables):
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
            return label in tables, label
        else:
            return False, ''

    def a_get_search_msg(self, search, tag, tablestart):
        warn_nomatch = ''
        searchmsg    = "Found table in line %d. " % tablestart
        if tag == '':
            searchmsg += "No label. Skipping..."
        else:
            searchmsg += "Found label '%s'... " % tag
            if search:
                searchmsg += "Found match!"
            else:
                self.issues['nomatch'] += [tag]
                warn_nomatch = linesep + "NO MACHES FOR '%s' IN '%s'!"
                warn_nomatch += " Please check input file(s)"
                warn_nomatch = warn_nomatch % (tag, self.input)
        return searchmsg, warn_nomatch

    # Replaces all occurrences of #(#|\d+,*)# in a line. Needs to split by
    # & because that's how LaTeX delimits tables. Returns how many values it
    # replaced because LaTeX can have any number of entries per line.
    def a_replace_line(self, line, table, tablen):
        linesep = line.split('&')
        for i in range(len(linesep)):
            cell = linesep[i]
            if re.search(self.matcha, cell):
                entry      = table[tablen]
                linesep[i] = re.sub(self.matcha, entry, cell)
                tablen    += 1
            elif re.search(self.matchb, cell):
                entry      = table[tablen]
                linesep[i] = self.a_round_and_format(cell, entry)
                tablen    += 1
        line = '&'.join(linesep)
        return line, tablen

    # Decimal's quantize makes the object have the same number of
    # significant digits as the input passed. format(str, ',d') returns
    # str with comma as thousands separator
    def a_round_and_format(self, cell, entry):
        precision, comma = re.findall(self.matchb, cell)[0]
        precision = int(precision)
        roundas   = 0 if precision == 0 else pow(10, -precision)
        roundas   = Decimal(str(roundas))
        rounded   = str(Decimal(entry).quantize(roundas, rounding = ROUND_HALF_UP))
        if ',' in comma:
            integer_part, decimal_part = re.findall(self.matchc, rounded)[0]
            rounded = format(int(integer_part), ',d') + decimal_part
        return re.sub(self.matchb, rounded, cell)

    # ---------------------------------------------------------------------
    # Check for the issues mentioned above insert_tables

    def f_check_issues(self):
        for key in self.issues.keys():
            self.issues[key] = ','.join(self.issues[key])

        self.problem = True in [v != '' for v in self.issues.values()]
        if self.problem:
            fill   = (self.template, self.input)
            imtags = "WARNING: These tags were in '%s' but not in '%s':" % fill
            imhead = "WARNING: Lines in '%s' maching #(#|\d+,*)#" % self.template
            imend  = linesep + "Output '%s' may not compile!" % self.output

        if self.issues['nomatch'] != '':
            self.issuesmsg['nomatch']  = imtags
            self.issuesmsg['nomatch'] += self.issues['nomatch'] + imend

        if self.issues['notable'] != '':
            self.issuesmsg['notable']  = imhead
            self.issuesmsg['notable'] += " but were not in a table environment: "
            self.issuesmsg['notable'] += self.issues['notable'] + imend

        if self.issues['nolabel'] != '':
            self.issuesmsg['nolabel']  = imhead
            self.issuesmsg['nolabel'] += " but the environment had no label: "
            self.issuesmsg['nolabel'] += self.issues['nolabel'] + imend

    # ---------------------------------------------------------------------
    # Insert message, write output file

    def f_insert_warning(self, tex_text):
        template = ''.join(self.template)
        head = 3 * [72 * '%' + linesep]
        msg  = ["This file was produced by 'tablefill.py'" + linesep]
        msg += ["    Template file: %s" % template + linesep]
        msg += ["    Input file(s): %s" % self.input + linesep]
        msg += ["To make changes, edit the input and template files." + linesep]

        # If there were issues, say so in the message
        if self.problem:
            msg += [linesep + "THERE WAS AN ISSUE CREATING THIS FILE!" + linesep]
            msg += [s + linesep for s in self.issuesmsg.values()]
        else:
            msg += [linesep + "DO NOT EDIT THIS FILE DIRECTLY." + linesep]
        msg = linesep.join(msg).split(linesep)
        insertmsg = head + ['% ' + m + linesep for m in msg] + head
        return insertmsg + tex_text, len(insertmsg)

    def f_write_to_output(self, text):
        outfile = open(self.output, 'wb')
        outfile.write(''.join(text))
        outfile.close()
