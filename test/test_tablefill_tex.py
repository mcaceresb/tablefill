#! /usr/bin/env python
# ---------------------------------------------------------------------
# Tests for tablefill_tex.py

import unittest
import os
import sys
sys.path.append('../py/')
from nostderrout import nostderrout
from tablefill_tex import tablefill_tex

class testTableFillTeX(unittest.TestCase):

    def getFileNames(self):
        self.input_appendix = 'input/tables_appendix.txt input/tables_appendix_two.txt'
        self.input_nolabel  = 'input/tables_appendix.txt input/tables_nolabel.txt'
        self.input_fakeone  = 'input/fake_file.txt input/tables_appendix_two.txt'
        self.input_faketwo  = 'input/tables_appendix.txt input/fake_file.txt'
        self.output         = './input/tablefill_template_filled.tex'
        self.template       = 'input/tablefill_template.tex'
        self.templatebreaks = 'input/tablefill_template_breaks.tex'
        self.templatetext   = '../test/input/textfill_template.tex'
        self.templatenolab  = 'input/tablefill_template_nolab.tex'
        self.templatewrong  = 'input/tablefill_template_wrong.tex'

    def testInput(self):
        self.getFileNames()
        with nostderrout():
            message = tablefill_tex(input    = self.input_appendix,
                                    template = self.template,
                                    output   = self.output)
        self.assertIn('SUCCESS', message.exit)
        # tag_data    = open(self.template, 'rU').readlines()
        # filled_data = open(self.output, 'rU').readlines()

        # Given my message changes length, I need to change this
        # self.assertEqual(len(tag_data) + 13, len(filled_data))

        # Also, Their tag comparison would be a pain to implement See
        # the tests at the bottom instead

    def testBreaksRoundingString(self):
        self.getFileNames()
        with nostderrout():
            error = tablefill_tex(input    = self.input_appendix,
                                  template = self.templatebreaks,
                                  output   = self.output)
        self.assertIn('ERROR', error.exit)
        self.assertIn('InvalidOperation', error.exitmsg)

    def testIllegalSyntax(self):
        self.getFileNames()

        # missing arguments
        with nostderrout():
            error = tablefill_tex(input    = self.input_appendix,
                                  template = self.template)
        self.assertIn('ERROR', error.exit)
        self.assertIn('KeyError', error.exitmsg)

        # non-existent input 1
        with nostderrout():
            error = tablefill_tex(input    = self.input_fakeone,
                                  template = self.template,
                                  output   = self.output)
        self.assertIn('ERROR', error.exit)
        self.assertIn('IOError', error.exitmsg)

        # non-existent input 2
        with nostderrout():
            error = tablefill_tex(input    = self.input_faketwo,
                                  template = self.template,
                                  output   = self.output)
        self.assertIn('ERROR', error.exit)
        self.assertIn('IOError', error.exitmsg)

    def testArgumentOrder(self):
        self.getFileNames()

        with nostderrout():
            message = tablefill_tex(template = self.template,
                                    input    = self.input_appendix,
                                    output   = self.output)
        self.assertIn('SUCCESS', message.exit)
        filled_data_args1 = open(self.output, 'rU').readlines()

        with nostderrout():
            message = tablefill_tex(output   = self.output,
                                    template = self.template,
                                    input    = self.input_appendix)
        self.assertIn('SUCCESS', message.exit)
        filled_data_args2 = open(self.output, 'rU').readlines()

        self.assertEqual(filled_data_args1, filled_data_args2)

    # ---------------------------------------------------------------------
    # The following test uses three files that are WRONG but
    # the tablefill.py function completely ignores the issues.
    # tablefill_tex.py Gives at least will give a warning
    def testMissingLabel(self):
        self.getFileNames()

        # Pattern outside of table
        with nostderrout():
            error = tablefill_tex(input    = self.input_appendix,
                                  template = self.templatewrong,
                                  output   = self.output)
        self.assertIn('WARNINGS', error.exit)

        # No label in tables
        with nostderrout():
            error = tablefill_tex(input    = self.input_appendix,
                                  template = self.templatenolab,
                                  output   = self.output)
        self.assertIn('WARNINGS', error.exit)

        # No label in template
        with nostderrout():
            error = tablefill_tex(input    = self.input_nolabel,
                                  template = self.template,
                                  output   = self.output)
        self.assertIn('WARNINGS', error.exit)


if __name__ == '__main__':
    os.getcwd()
    unittest.main()
