Common Issues
=============

!!! info "Warning"
    This page is under construction

Error Logging
-------------

`tablefill` tries to be informative when the template and input
do not line up as expected. Therefore when it finds a table
environment it checks:

- If it finds a label within that environment
- If the label matches one in the input file(s)
- Whether it finds the `#(#|\d+,*)#` pattern but no label
- When it finds the end of the table environment
- How many substitutions it made in the table
- When there are more `#(#|\d+,*)#` than entries in the corresponding input matrix.
- When it finds the `#(#|\d+,*)#` pattern outside a table environment

If the user forgets to include a label/tag or if there is a mismatch
between the number of placeholders, `tablefill` say so and note where
to fix the issue. 

Notes
-----

- Non-numerical data can only be filled using "###"; all other placeholders
  require numeric input.

- The program currently does not handle trailing comments. If a line
  doesn't start with a comment, it will replace everything in that line,
  even if there is a comment halfway through.

- New lines of the table must be on new lines of the `.tex` file

- Only _one_ label is matched to a table. If there are duplicate labels in the
  input file(s), only the last one is kept. This is done so the user can
  continuously append results to the same input file.
