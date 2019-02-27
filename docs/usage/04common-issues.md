Common Issues
=============

!!! info "Warning"
    This page is under construction

Common Mistakes
---------------

- Missing table label/tag in the input file or in the template file.

- Mismatch between the length of the template table and corresponding
  text table. If the template table has more entries to be filled than
  the text table has entries to fill from, this will cause an error.

- Use of numerical tags (e.g. #1#) to fill non-numerical data. This will
  cause an error. Non-numerical data can only be filled using "###", as
  it does not make sense to round or truncate this data.

- The program currently does not handle trailing comments. If a line
   doesn't start with a comment, it will replace everything in that line,
   even if there is a comment halfway through.

- New lines of the table must be on new lines of the `.tex` file

Error Logging
-------------

The program indicates

- When it finds a table environment
    - If it finds a label within that environment
    - If the label matches one in the input file(s)
    - Whether it finds the `#(#|\d+,*)#` pattern but no label
    - When it finds the end of the table environment
    - How many substitutions it made in the table
- When it finds the `#(#|\d+,*)#` pattern outside a table environment
- When it finds more `#(#|\d+,*)#` than entries in the corresponding table
- When it finds an error (and if so it terminates)
