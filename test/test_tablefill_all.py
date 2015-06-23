#! /usr/bin/env python
# ---------------------------------------------------------------------
# Tests for tablefill.py
# TODO(mauricio): Implement error codes in CLI version

from subprocess import call
import unittest
import os
import sys
sys.path.append('../')
from nostderrout import nostderrout
from tablefill import tablefill
program = 'python ../tablefill.py --silent'

class testTableFillFunction(unittest.TestCase):

    def getFileNames(self):
        self.input_appendix = 'input/tables_appendix.txt input/tables_appendix_two.txt'
        self.input_nolabel  = 'input/tables_appendix.txt input/tables_nolabel.txt'
        self.input_fakeone  = 'input/fake_file.txt input/tables_appendix_two.txt'
        self.input_faketwo  = 'input/tables_appendix.txt input/fake_file.txt'

        self.texoutput      = './input/tablefill_template_filled.tex'
        self.lyxoutput      = './input/tablefill_template_filled.lyx'
        self.texoutputnodir = './input/does/not/exist/tablefill_template_filled.tex'
        self.lyxoutputnodir = './input/does/not/exist/tablefill_template_filled.lyx'

        self.pytemplate        = 'input/tablefill_template.py'
        self.blanktemplate     = 'input/tablefill_template'
        self.textemplate       = 'input/tablefill_template.tex'

        self.textemplatebreaks = 'input/tablefill_template_breaks.tex'
        self.textemplatetext   = '../test/input/textfill_template.tex'
        self.textemplatenolab  = 'input/tablefill_template_nolab.tex'
        self.textemplatewrong  = 'input/tablefill_template_wrong.tex'

        self.lyxtemplate       = 'input/tablefill_template.lyx'
        self.lyxtemplatebreaks = 'input/tablefill_template_breaks.lyx'
        self.lyxtemplatetext   = '../test/input/textfill_template.lyx'
        self.lyxtemplatenolab  = 'input/tablefill_template_nolab.lyx'
        self.lyxtemplatewrong  = 'input/tablefill_template_wrong.lyx'

    def testInput(self):
        self.getFileNames()
        with nostderrout():
            statuslyx, msglyx = tablefill(input    = self.input_appendix,
                                          template = self.lyxtemplate,
                                          output   = self.lyxoutput)
            statustex, msgtex = tablefill(input    = self.input_appendix,
                                          template = self.textemplate,
                                          output   = self.texoutput)

        self.assertEqual('SUCCESS', statustex)
        self.assertEqual('SUCCESS', statuslyx)

        # Given my message changes length, I need to change this
        # self.assertEqual(len(tag_data) + 13, len(filled_data))
        # Also, Their tag comparison would be a pain to implement See
        # the tests at the bottom instead

    def testBreaksRoundingString(self):
        self.getFileNames()
        with nostderrout():
            errorlyx, msglyx = tablefill(input    = self.input_appendix,
                                         template = self.lyxtemplatebreaks,
                                         output   = self.lyxoutput)
            errortex, msgtex = tablefill(input    = self.input_appendix,
                                         template = self.textemplatebreaks,
                                         output   = self.texoutput)

        self.assertEqual('ERROR', errortex)
        self.assertEqual('ERROR', errorlyx)
        self.assertIn('InvalidOperation', msgtex)
        self.assertIn('InvalidOperation', msglyx)

    def testIllegalSyntax(self):
        self.getFileNames()

        # missing arguments
        with nostderrout():
            errorlyx, msglyx = tablefill(input    = self.input_appendix,
                                         template = self.lyxtemplate)
            errortex, msgtex = tablefill(input    = self.input_appendix,
                                         template = self.textemplate)

        self.assertEqual('ERROR', errortex)
        self.assertEqual('ERROR', errorlyx)
        self.assertIn('KeyError', msgtex)
        self.assertIn('KeyError', msglyx)

        # Must be strings
        with nostderrout():
            errorlyx, msglyx = tablefill(input    = [self.input_appendix],
                                         template = self.lyxtemplate,
                                         output   = self.lyxoutput)
            errortex, msgtex = tablefill(input    = [self.input_appendix],
                                         template = self.textemplate,
                                         output   = self.texoutput)

        self.assertEqual('ERROR', errortex)
        self.assertEqual('ERROR', errorlyx)
        self.assertIn('TypeError', msgtex)
        self.assertIn('TypeError', msglyx)

        with nostderrout():
            errorlyx, msglyx = tablefill(input    = self.input_appendix,
                                         template = self.lyxtemplate,
                                         output   = 10)
            errortex, msgtex = tablefill(input    = self.input_appendix,
                                         template = self.textemplate,
                                         output   = 10)

        self.assertEqual('ERROR', errortex)
        self.assertEqual('ERROR', errorlyx)
        self.assertIn('TypeError', msgtex)
        self.assertIn('TypeError', msglyx)

        # unexpected arguments are ignored
        with nostderrout():
            statuslyx, msglyx = tablefill(input    = self.input_appendix,
                                          template = self.lyxtemplate,
                                          waffle   = "My Waffles are Best!",
                                          output   = self.lyxoutput)
            statustex, msgtex = tablefill(input    = self.input_appendix,
                                          template = self.textemplate,
                                          waffle   = "My Waffles are Best!",
                                          output   = self.texoutput)

        self.assertEqual('SUCCESS', statustex)
        self.assertEqual('SUCCESS', statuslyx)

    def testIllegalArgs(self):
        self.getFileNames()

        # Must be lyx or tex
        with nostderrout():
            errorlyx, msglyx = tablefill(input    = self.input_appendix,
                                         template = self.pytemplate,
                                         output   = self.lyxoutput)
            errortex, msgtex = tablefill(input    = self.input_appendix,
                                         template = self.blanktemplate,
                                         output   = self.texoutput)

        self.assertEqual('ERROR', errortex)
        self.assertEqual('ERROR', errorlyx)
        self.assertIn('KeyError', msgtex)
        self.assertIn('KeyError', msglyx)

        # But you can override if you know the file type
        with nostderrout():
            statustex, msgtex = tablefill(input    = self.input_appendix,
                                          template = self.pytemplate,
                                          output   = self.texoutput,
                                          filetype = 'tex')

        self.assertEqual('SUCCESS', statustex)

        # non-existent output folder
        with nostderrout():
            errorlyx, msglyx = tablefill(input    = self.input_appendix,
                                         template = self.lyxtemplate,
                                         output   = self.lyxoutputnodir)
            errortex, msgtex = tablefill(input    = self.input_appendix,
                                         template = self.textemplate,
                                         output   = self.texoutputnodir)

        self.assertEqual('ERROR', errortex)
        self.assertEqual('ERROR', errorlyx)
        self.assertIn('IOError', msgtex)
        self.assertIn('IOError', msglyx)

        # non-existent input 1
        with nostderrout():
            errorlyx, msglyx = tablefill(input    = self.input_fakeone,
                                         template = self.lyxtemplate,
                                         output   = self.lyxoutput)
            errortex, msgtex = tablefill(input    = self.input_fakeone,
                                         template = self.textemplate,
                                         output   = self.texoutput)

        self.assertEqual('ERROR', errortex)
        self.assertEqual('ERROR', errorlyx)
        self.assertIn('IOError', msgtex)
        self.assertIn('IOError', msglyx)

        # non-existent input 2
        with nostderrout():
            errorlyx, msglyx = tablefill(input    = self.input_faketwo,
                                         template = self.lyxtemplate,
                                         output   = self.lyxoutput)
            errortex, msgtex = tablefill(input    = self.input_faketwo,
                                         template = self.textemplate,
                                         output   = self.texoutput)

        self.assertEqual('ERROR', errortex)
        self.assertEqual('ERROR', errorlyx)
        self.assertIn('IOError', msgtex)
        self.assertIn('IOError', msglyx)

    def testArgumentOrder(self):
        self.getFileNames()

        with nostderrout():
            statuslyx, msglyx = tablefill(template = self.lyxtemplate,
                                          input    = self.input_appendix,
                                          output   = self.lyxoutput)
            statustex, msgtex = tablefill(template = self.textemplate,
                                          input    = self.input_appendix,
                                          output   = self.texoutput)

        self.assertEqual('SUCCESS', statustex)
        self.assertEqual('SUCCESS', statuslyx)
        texfilled_data_args1 = open(self.texoutput, 'rU').readlines()
        lyxfilled_data_args1 = open(self.lyxoutput, 'rU').readlines()

        with nostderrout():
            statuslyx, msglyx = tablefill(output   = self.lyxoutput,
                                          template = self.lyxtemplate,
                                          input    = self.input_appendix)
            statustex, msgtex = tablefill(output   = self.lyxoutput,
                                          template = self.lyxtemplate,
                                          input    = self.input_appendix)

        self.assertEqual('SUCCESS', statustex)
        self.assertEqual('SUCCESS', statuslyx)
        texfilled_data_args2 = open(self.texoutput, 'rU').readlines()
        lyxfilled_data_args2 = open(self.lyxoutput, 'rU').readlines()

        self.assertEqual(texfilled_data_args1, texfilled_data_args2)
        self.assertEqual(lyxfilled_data_args1, lyxfilled_data_args2)

    # ------------------------------------------------------------------
    # The following test uses three files that are WRONG but the
    # original tablefill.py ignores the issues. This gives a warning.

    def testMissingLabel(self):
        self.getFileNames()

        # Pattern outside of table
        with nostderrout():
            warnlyx, msglyx = tablefill(input    = self.input_appendix,
                                        template = self.lyxtemplatewrong,
                                        output   = self.lyxoutput)
            warntex, msgtex = tablefill(input    = self.input_appendix,
                                        template = self.textemplatewrong,
                                        output   = self.texoutput)

        self.assertEqual('WARNING', warntex)
        self.assertEqual('WARNING', warnlyx)

        # No label in tables
        with nostderrout():
            warnlyx, msglyx = tablefill(input    = self.input_appendix,
                                        template = self.lyxtemplatenolab,
                                        output   = self.lyxoutput)
            warntex, msgtex = tablefill(input    = self.input_appendix,
                                        template = self.textemplatenolab,
                                        output   = self.texoutput)

        self.assertEqual('WARNING', warntex)
        self.assertEqual('WARNING', warnlyx)

        # No label in template
        with nostderrout():
            warnlyx, msglyx = tablefill(input    = self.input_nolabel,
                                        template = self.lyxtemplate,
                                        output   = self.lyxoutput)
            warntex, msgtex = tablefill(input    = self.input_nolabel,
                                        template = self.textemplate,
                                        output   = self.texoutput)

        self.assertEqual('WARNING', warntex)
        self.assertEqual('WARNING', warnlyx)


class testTableFillCLI(unittest.TestCase):

    def getFileNames(self):
        self.input_appendix = 'input/tables_appendix.txt input/tables_appendix_two.txt'
        self.input_nolabel  = 'input/tables_appendix.txt input/tables_nolabel.txt'
        self.input_fakeone  = 'input/fake_file.txt input/tables_appendix_two.txt'
        self.input_faketwo  = 'input/tables_appendix.txt input/fake_file.txt'

        self.texoutput      = './input/tablefill_template_filled.tex'
        self.lyxoutput      = './input/tablefill_template_filled.lyx'
        self.texoutputnodir = './input/does/not/exist/tablefill_template_filled.tex'
        self.lyxoutputnodir = './input/does/not/exist/tablefill_template_filled.lyx'

        self.pytemplate        = 'input/tablefill_template.py'
        self.blanktemplate     = 'input/tablefill_template'
        self.textemplate       = 'input/tablefill_template.tex'

        self.textemplatebreaks = 'input/tablefill_template_breaks.tex'
        self.textemplatetext   = '../test/input/textfill_template.tex'
        self.textemplatenolab  = 'input/tablefill_template_nolab.tex'
        self.textemplatewrong  = 'input/tablefill_template_wrong.tex'

        self.lyxtemplate       = 'input/tablefill_template.lyx'
        self.lyxtemplatebreaks = 'input/tablefill_template_breaks.lyx'
        self.lyxtemplatetext   = '../test/input/textfill_template.lyx'
        self.lyxtemplatenolab  = 'input/tablefill_template_nolab.lyx'
        self.lyxtemplatewrong  = 'input/tablefill_template_wrong.lyx'

    def testInput(self):
        self.getFileNames()
        lyxinforce = (program, self.lyxtemplate, self.input_appendix)
        lyxinout   = (program, self.lyxtemplate, self.input_appendix, self.lyxoutput)
        lyxinforce_status = call('%s %s --input %s --force' % lyxinforce, shell = True)
        lyxinout_status   = call('%s %s --input %s --output %s' % lyxinout, shell = True)
        self.assertEqual(0, lyxinforce_status)
        self.assertEqual(0, lyxinout_status)

        texinforce = (program, self.textemplate, self.input_appendix)
        texinout   = (program, self.textemplate, self.input_appendix, self.texoutput)
        texinforce_status = call('%s %s --input %s --force' % texinforce, shell = True)
        texinout_status   = call('%s %s --input %s --output %s' % texinout, shell = True)
        self.assertEqual(0, texinforce_status)
        self.assertEqual(0, texinout_status)

    def testBreaksRoundingString(self):
        self.getFileNames()

        lyxinout = (program, self.lyxtemplatebreaks, self.input_appendix, self.lyxoutput)
        lyxinout_status = call('%s %s --input %s --output %s' % lyxinout, shell = True)
        texinout = (program, self.textemplatebreaks, self.input_appendix, self.texoutput)
        texinout_status = call('%s %s --input %s --output %s' % texinout, shell = True)
        self.assertEqual(1, lyxinout_status)
        self.assertEqual(1, texinout_status)

    def testIllegalSyntax(self):
        self.getFileNames()

        # missing arguments
        lyxinout = (program, self.lyxtemplate, self.input_appendix)
        lyxinout_status = call('%s %s --input %s' % lyxinout, shell = True)
        texinout = (program, self.textemplate, self.input_appendix)
        texinout_status = call('%s %s --input %s' % texinout, shell = True)
        self.assertEqual(1, lyxinout_status)
        self.assertEqual(1, texinout_status)

        # unexpected arguments are give error courtesy of argparse
        lyxinout = (program, self.lyxtemplate, self.input_appendix, self.lyxoutput)
        lyxinout_status = call('%s %s --input %s --output %s hello' % lyxinout, shell = True)
        texinout = (program, self.textemplate, self.input_appendix, self.texoutput)
        texinout_status = call('%s %s --input %s --output %s hello' % texinout, shell = True)
        self.assertEqual(2, lyxinout_status)
        self.assertEqual(2, texinout_status)

        lyxinout = (program, self.lyxtemplate, self.input_appendix, self.lyxoutput)
        lyxinout_status = call('%s %s --input %s --output %s --waffle hi' % lyxinout, shell = True)
        texinout = (program, self.textemplate, self.input_appendix, self.texoutput)
        texinout_status = call('%s %s --input %s --output %s --waffle hi' % texinout, shell = True)
        self.assertEqual(2, lyxinout_status)
        self.assertEqual(2, texinout_status)

    def testIllegalArgs(self):
        self.getFileNames()

        lyxinout = (program, self.pytemplate, self.input_appendix, self.lyxoutput)
        lyxinout_status = call('%s %s --input %s --output %s' % lyxinout, shell = True)
        texinout = (program, self.pytemplate, self.input_appendix, self.texoutput)
        texinout_status = call('%s %s --input %s --output %s' % texinout, shell = True)
        self.assertEqual(1, lyxinout_status)
        self.assertEqual(1, texinout_status)

        texinout = (program, self.pytemplate, self.input_appendix, self.texoutput)
        texinout_status = call('%s %s --input %s --output %s --type tex' % texinout, shell = True)
        self.assertEqual(0, texinout_status)

        lyxinout = (program, self.lyxtemplate, self.input_appendix, self.lyxoutputnodir)
        lyxinout_status = call('%s %s --input %s --output %s' % lyxinout, shell = True)
        texinout = (program, self.textemplate, self.input_appendix, self.texoutputnodir)
        texinout_status = call('%s %s --input %s --output %s' % texinout, shell = True)
        self.assertEqual(1, lyxinout_status)
        self.assertEqual(1, texinout_status)

        lyxinout = (program, self.lyxtemplate, self.input_fakeone, self.lyxoutput)
        lyxinout_status = call('%s %s --input %s --output %s' % lyxinout, shell = True)
        texinout = (program, self.textemplate, self.input_fakeone, self.texoutput)
        texinout_status = call('%s %s --input %s --output %s' % texinout, shell = True)
        self.assertEqual(1, lyxinout_status)
        self.assertEqual(1, texinout_status)

        lyxinout = (program, self.lyxtemplate, self.input_faketwo, self.lyxoutput)
        lyxinout_status = call('%s %s --input %s --output %s' % lyxinout, shell = True)
        texinout = (program, self.textemplate, self.input_faketwo, self.texoutput)
        texinout_status = call('%s %s --input %s --output %s' % texinout, shell = True)
        self.assertEqual(1, lyxinout_status)
        self.assertEqual(1, texinout_status)

    def testArgumentOrder(self):
        self.getFileNames()

        lyxinout = (program, self.lyxtemplate, self.lyxoutput, self.input_appendix)
        lyxinout_status = call('%s %s --output %s --input %s' % lyxinout, shell = True)
        texinout = (program, self.textemplate, self.texoutput, self.input_appendix)
        texinout_status = call('%s %s --output %s --input %s' % texinout, shell = True)
        self.assertEqual(0, lyxinout_status)
        self.assertEqual(0, texinout_status)
        texfilled_data_args1 = open(self.texoutput, 'rU').readlines()
        lyxfilled_data_args1 = open(self.lyxoutput, 'rU').readlines()

        # Since input takes multiple inputs, this actually fails
        lyxinout = (program, self.lyxoutput, self.input_appendix, self.lyxtemplate)
        lyxinout_status = call('%s --output %s --input %s %s' % lyxinout, shell = True)
        texinout = (program, self.texoutput, self.input_appendix, self.textemplate)
        texinout_status = call('%s --output %s --input %s %s' % texinout, shell = True)
        self.assertEqual(2, lyxinout_status)
        self.assertEqual(2, texinout_status)

        # But this is also OK
        lyxinout = (program, self.lyxoutput, self.input_appendix, self.lyxtemplate)
        lyxinout_status = call('%s --output %s --input %s --type lyx %s' % lyxinout, shell = True)
        texinout = (program, self.texoutput, self.input_appendix, self.textemplate)
        texinout_status = call('%s --output %s --input %s --type tex %s' % texinout, shell = True)
        self.assertEqual(0, lyxinout_status)
        self.assertEqual(0, texinout_status)

        texfilled_data_args2 = open(self.texoutput, 'rU').readlines()
        lyxfilled_data_args2 = open(self.lyxoutput, 'rU').readlines()

        self.assertEqual(texfilled_data_args1, texfilled_data_args2)
        self.assertEqual(lyxfilled_data_args1, lyxfilled_data_args2)

    # ------------------------------------------------------------------
    # The following test uses three files that are WRONG but the
    # original tablefill.py ignores the issues. This gives a warning.

    def testMissingLabel(self):
        self.getFileNames()
        lyxinout = (program, self.lyxtemplatewrong, self.lyxoutput, self.input_appendix)
        lyxinout_status = call('%s %s --output %s --input %s' % lyxinout, shell = True)
        texinout = (program, self.textemplatewrong, self.texoutput, self.input_appendix)
        texinout_status = call('%s %s --output %s --input %s' % texinout, shell = True)
        self.assertEqual(255, lyxinout_status)
        self.assertEqual(255, texinout_status)

        lyxinout = (program, self.lyxtemplatenolab, self.lyxoutput, self.input_appendix)
        lyxinout_status = call('%s %s --output %s --input %s' % lyxinout, shell = True)
        texinout = (program, self.textemplatenolab, self.texoutput, self.input_appendix)
        texinout_status = call('%s %s --output %s --input %s' % texinout, shell = True)
        self.assertEqual(255, lyxinout_status)
        self.assertEqual(255, texinout_status)

        lyxinout = (program, self.lyxtemplate, self.lyxoutput, self.input_nolabel)
        lyxinout_status = call('%s %s --output %s --input %s' % lyxinout, shell = True)
        texinout = (program, self.textemplate, self.texoutput, self.input_nolabel)
        texinout_status = call('%s %s --output %s --input %s' % texinout, shell = True)
        self.assertEqual(255, lyxinout_status)
        self.assertEqual(255, texinout_status)


if __name__ == '__main__':
    os.getcwd()
    unittest.main()
