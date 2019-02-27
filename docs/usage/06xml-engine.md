XML Engine
==========

!!! info "Warning"
    This page is under construction

The following code in the `.tex` template will be interpreted by
`tablefill.py` (please note I use `tag` and `label` interchangeably
throughout the documentation):

```xml
% <tablefill-python tag = 'newtagname'>
%     tagname[rows1][subentries1],
%     tagname[rows2][subentries2],
%     othertagname[rows3][subentries3]
% </tablefill-python>
%
% <tablefill-python tag = 'othernewtagname' type = 'float'>
%     tagname[row1][subentry1] / tagname[row2][subentry2],
%     othertagname[rows3][subentries3]
% </tablefill-python>
```

The above is parsed as xml and will create 2 new tags: First it creates
`newtagname` with `[rows1][subentries1]` and `[rows2][subentries2]`
from `tagname` and `[rows3][subentries3]` from `othertagname`.
Second it creates `othernewtagname` with the result of the operation
`tagname[row1][subentry1] / tagname[row2][subentry2]` followed by the
entries from `othertagname[rows3][subentries3]`. Only scalar operations
are supported, and the type must be set to `float` or the parsing will exit
with error.

The syntax for `[rows][sub]` is python syntax for nested
lists: See [here](http://stackoverflow.com/questions/509211#509295).
Note that python uses 0-based indexing and that the combine engine uses
the raw matrices (i.e. before missing entries are stripped). Each matrix
is parsed as a list of lists, so
```html
1  2  3        [[1,  2,  3],
. -1 -2   -->   [., -1, -2],
.  0  .         [.,  0,  .]]

[0]  or [-1]          --> [.,  0,  .]
[1]  or [-2]          --> [., -1, -2]
[2]  or [-3]          --> [1,  2,  3]
[1:] or [-2:]         --> [.,  0,  .]
[1][1:3] or [-2][-2:] --> [-1, -2]
```

It is also possible to specify tables in a separate `.xml` file and
pass it to tablefill (there should be no leading `%` in this case) via
`--xml-tables` in the command line or `xml_tables` in a function call.

