#! /usr/bin/env python
# ---------------------------------------------------------------------
# Tests for tablefill.py

import unittest
import os
import re
import sys
sys.path.append('../py/')
from nostderrout import nostderrout
from tablefill import tablefill

class testTablefill(unittest.TestCase):

    def getFileNames(self):
        self.input_appendix = 'input/tables_appendix.txt input/tables_appendix_two.txt'
        self.input_nolabel  = 'input/tables_appendix.txt input/tables_nolabel.txt'
        self.input_fakeone  = 'input/fake_file.txt input/tables_appendix_two.txt'
        self.input_faketwo  = 'input/tables_appendix.txt input/fake_file.txt'
        self.output         = './input/tablefill_template_filled.lyx'
        self.template       = 'input/tablefill_template.lyx'
        self.templatebreaks = 'input/tablefill_template_breaks.lyx'
        self.templatetext   = '../test/input/textfill_template.lyx'
        self.templatenolab  = 'input/tablefill_template_nolab.lyx'
        self.templatewrong  = 'input/tablefill_template_wrong.lyx'

    def testInput(self):
        self.getFileNames()
        with nostderrout():
            message = tablefill(input    = self.input_appendix,
                                template = self.template,
                                output   = self.output)
            self.assertIn('filled successfully', message)

        tag_data    = open(self.template, 'rU').readlines()
        filled_data = open(self.output, 'rU').readlines()
        self.assertEqual(len(tag_data) + 13, len(filled_data))
        for n in range(len(tag_data)):
            self.tag_compare(tag_data[n], filled_data[n + 13])

    def tag_compare(self, tag_line, filled_line):
        if re.match('^.*#\d+#', tag_line) or re.match('^.*#\d+,#', tag_line):
            entry_tag = re.split('#', tag_line)[1]
            decimal_places = int(entry_tag.replace(',', ''))
            if decimal_places > 0:
                self.assertTrue(re.search('\.', filled_line))
                decimal_part = re.split('\.', filled_line)[1]
                non_decimal = re.compile(r'[^\d.]+')
                decimal_part = non_decimal.sub('', decimal_part)
                self.assertEqual(len(decimal_part), decimal_places)
            else:
                self.assertFalse(re.search('\.', filled_line))
            if re.match('^.*#\d+,#', tag_line):
                integer_part = re.split('\.', filled_line)[0]
                if len(integer_part) > 3:
                    self.assertEqual(integer_part[-4], ',')

    def testBreaksRoundingString(self):
        self.getFileNames()
        with nostderrout():
            error = tablefill(input    = self.input_appendix,
                              template = self.templatebreaks,
                              output   = self.output)
        self.assertIn('InvalidOperation', error)

    def testIllegalSyntax(self):
        self.getFileNames()

        # missing arguments
        with nostderrout():
            error = tablefill(input    = self.input_appendix,
                              template = self.template)
        self.assertIn('KeyError', error)

        # non-existent input 1
        with nostderrout():
            error = tablefill(input    = self.input_fakeone,
                              template = self.template,
                              output   = self.output)
        self.assertIn('IOError', error)

        # non-existent input 2
        with nostderrout():
            error = tablefill(input    = self.input_faketwo,
                              template = self.template,
                              output   = self.output)
        self.assertIn('IOError', error)

    def testArgumentOrder(self):
        self.getFileNames()

        with nostderrout():
            message = tablefill(template = self.template,
                                input    = self.input_appendix,
                                output   = self.output)
        self.assertIn('filled successfully', message)
        filled_data_args1 = open(self.output, 'rU').readlines()

        with nostderrout():
            message = tablefill(output   = self.output,
                                template = self.template,
                                input    = self.input_appendix)
        self.assertIn('filled successfully', message)
        filled_data_args2 = open(self.output, 'rU').readlines()

        self.assertEqual(filled_data_args1, filled_data_args2)

# ##############################################################################
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  WARNING  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
# ##############################################################################

    # The following test uses three files that are WRONG but the tablefill.py
    # function completely ignores the issues
    #   1. The first template file has the pattern OUTSIDE a table
    #   2. The second template file has a table with a missing label
    #   3. The third template is fine, but one of its labels is not in input
    def testMissingLabel(self):
        self.getFileNames()

        # Pattern outside of table
        with nostderrout():
            error = tablefill(input    = self.input_appendix,
                              template = self.templatewrong,
                              output   = self.output)
        self.assertIn('filled successfully', error)

        # No label in tables
        with nostderrout():
            error = tablefill(input    = self.input_appendix,
                              template = self.templatenolab,
                              output   = self.output)
        self.assertIn('filled successfully', error)

        # No label in template
        with nostderrout():
            error = tablefill(input    = self.input_nolabel,
                              template = self.template,
                              output   = self.output)
        self.assertIn('filled successfully', error)

# ##############################################################################
# !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!  WARNING  !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!#
# ##############################################################################


if __name__ == '__main__':
    os.getcwd()
    unittest.main()
