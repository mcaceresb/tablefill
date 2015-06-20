#! /usr/bin/env python
# ---------------------------------------------------------------------
# Tests for tablefill_tex.py

import os

input_appendix = 'input/tables_appendix.txt input/tables_appendix_two.txt'
input_nolabel  = 'input/tables_appendix.txt input/tables_nolabel.txt'
input_fakeone  = 'input/fake_file.txt input/tables_appendix_two.txt'
input_faketwo  = 'input/tables_appendix.txt input/fake_file.txt'
output         = 'input/tablefill_template_filled.tex'
template       = 'input/tablefill_template.tex'
templatebreaks = 'input/tablefill_template_breaks.tex'
templatenolab  = 'input/tablefill_template_nolab.tex'
templatewrong  = 'input/tablefill_template_wrong.tex'

program = 'python ../tablefill.py '

# Correct
os.system('%s %s --input %s --force' % (program, template, input_appendix))
os.system('%s %s --input %s --output %s' % (program, template, input_appendix, output))
os.system('%s --input %s -o %s %s' % (program, input_appendix, output, template))
os.system('%s -h' % program)

# Errors
os.system('%s %s --input %s --force' % (program, templatebreaks, input_appendix))
os.system('%s %s --input %s' % (program, template, input_appendix))
os.system('%s %s --input %s --force' % (program, template, input_fakeone))
os.system('%s %s --input %s --force' % (program, template, input_faketwo))
os.system('%s --input %s %s --force' % (program, input_appendix, template))

# Warnings
os.system('%s %s --input %s --force' % (program, templatewrong, input_appendix))
os.system('%s %s --input %s --force' % (program, templatenolab, input_appendix))
os.system('%s %s --input %s --force' % (program, template, input_nolabel))
