# ---------------------------------------------------------------------
# Given their tag comparison is too much of a pain to implement,
# here are two instances of me testing out various inputs and outputs

replace_line = () # Get it from tablefill_tex.py

tablen = 0
matcha = r'\\*#\\*#\\*#'
matchb = r'\\*#(\d+)(,*)\\*#'
expect = ['String', '2309.2093', '2309.20930',
          '2309.20930000000000000000', '2309.209',
          '2309.21', '2309', '2,309', '-0.02',
          '-0.0223000', '-22,300,000,000.000000 ',
          '(2309.21)', '2309.21**', 'ab2309.21cd']
table  = ['String', '2309.2093', '2309.2093', '2309.2093', '2309.2093',
          '2309.2093', '2309.2093', '2309.2093', '-2.23e-2', '-2.23e-2',
          '-2.23e+10', '2309.2093', '2309.2093', '2309.2093', 'abc']
line   = ['###', '#4#', '#5#', '#20#', '#3#', '#2#', '#0#', '#0,#',
          '#2#', '#7#', ' #6,#', '(#2#)', '#2#**', 'ab#2#cd', '###']
line   = ' & '.join(line)
matchedline, tablen = replace_line(line, table, tablen, matcha, matchb)
ziplines = zip(matchedline.split(' & '), expect)
allmatch = all([res.strip() == exp.strip() for res, exp in ziplines])
print allmatch


tablen = 0
matcha = r'\\*#\\*#\\*#'
matchb = r'\\*#(\d+)(,*)\\*#'

crazymatch = '\\beta Hi \$(\\#\\#\\#)\%* \\alpha '
crazymatch += '& \\beta Hi \$(\\##\\#)\%* \\alpha '
crazymatch += '& \\beta Hi \$(\\#\\##)\%* \\alpha '
crazymatch += '& \\beta Hi \$(#\\#\\#)\% \\alpha '
crazymatch += '& \\beta Hi \$(\\###)*\% \\alpha '
crazymatch += '& \\beta Hi \$(##\\#)*\% \\alpha '
crazymatch += '& \\beta Hi \$(###)*\% \\alpha '

crazymatch += '& \\beta Hi (\$\\#3\\#)\%* \\alpha '
crazymatch += '& \\beta Hi (\$\\#3\\#)\%* \\alpha '
crazymatch += '& \\beta Hi (\$\\#3#*  \\alpha '
crazymatch += '& \\beta Hi (\$#3\\#*  \\alpha '
crazymatch += '& \\beta Hi (\$\\#3#*  \\alpha '
crazymatch += '& \\beta Hi (\$#3\\#*  \\alpha '
crazymatch += '& \\beta Hi (\$#3#)    \\alpha '

crazymatch += '& \\beta Hi \$(\\#0,\\#)\%* \\alpha '
crazymatch += '& \\beta Hi \$(\\#0,\\#)\%* \\alpha '
crazymatch += '& \\beta Hi \$(\\#0,#*  \\alpha '
crazymatch += '& \\beta Hi \$(#0,\\#*  \\alpha '
crazymatch += '& \\beta Hi \$(\\#0,#*  \\alpha '
crazymatch += '& \\beta Hi \$(#0,\\#*  \\alpha '
crazymatch += '& \\beta Hi \$(#0,#)    \\alpha '

expect  = ['\\beta Hi \\$(3234.43241)\\%* \\alpha']
expect += ['\\beta Hi \\$(3234.43241)\\%* \\alpha']
expect += ['\\beta Hi \\$(3234.43241)\\%* \\alpha']
expect += ['\\beta Hi \\$(3234.43241)\\% \\alpha']
expect += ['\\beta Hi \\$(3234.43241)*\\% \\alpha']
expect += ['\\beta Hi \\$(3234.43241)*\\% \\alpha']
expect += ['\\beta Hi \\$(3234.43241)*\\% \\alpha']

expect += ['\\beta Hi (\\$3234.432)\\%* \\alpha']
expect += ['\\beta Hi (\\$3234.432)\\%* \\alpha']
expect += ['\\beta Hi (\\$3234.432*  \\alpha']
expect += ['\\beta Hi (\\$3234.432*  \\alpha']
expect += ['\\beta Hi (\\$3234.432*  \\alpha']
expect += ['\\beta Hi (\\$3234.432*  \\alpha']
expect += ['\\beta Hi (\\$3234.432)    \\alpha']

expect += ['\\beta Hi \\$(3,234)\\%* \\alpha']
expect += ['\\beta Hi \\$(3,234)\\%* \\alpha']
expect += ['\\beta Hi \\$(3,234*  \\alpha']
expect += ['\\beta Hi \\$(3,234*  \\alpha']
expect += ['\\beta Hi \\$(3,234*  \\alpha']
expect += ['\\beta Hi \\$(3,234*  \\alpha']
expect += ['\\beta Hi \\$(3,234)    \\alpha ']

table  = ['3234.43241'] * len(crazymatch)
matchedline, tablen = replace_line(crazymatch, table, 0, matcha, matchb)
ziplines = zip(matchedline.split(' & '), expect)
allmatch = all([res.strip() == exp.strip() for res, exp in ziplines])
print allmatch
