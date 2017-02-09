Change Log
==========

## tablefill-0.7.0 (2016-10-24)

### Features

* Added placeholder #|\d+|# to take absolute value of input
* Added backwards-compatible list flattening
* Added option to fill in the comments.
* Now parses commented XML code to combine tables

```xml
<tablefill-custom tag = 'newtagname'>
    <combine tag = 'tagname'>
        [rows1][subentries1];
        [rows2][subentries2];
    </combine>
    <combine tag = 'othertagname'>
        [rows3][subentries3]
    </combine>
</tablefill-custom>
```

is parsed to combine `[rows1][subentries1]` and `[rows2][subentries2]`
from `tagname` with `[rows3][subentries3]` of `othertagname`. The
syntax for `[rows][sub]` is python syntax for nested lists: See
[here](http://stackoverflow.com/questions/509211#509295). Note that
python uses 0-based indexing and that the combine engine uses the raw
matrices (i.e. before missing entries are stripped). Each matrix is
parsed as a list of lists, so

```html
1  2  3    [[1,  2,  3],
. -1 -2 --> [., -1, -2],
.  0  .     [.,  0,  .]]

[0]  or [-1]  --> [.,  0,  .]
[1]  or [-2]  --> [., -1, -2]
[2]  or [-3]  --> [1,  2,  3]
[1:] or [-2:] --> [.,  0,  .]
[1][1:3] or [-2][-2:] --> [-1, -2]
```

## tablefill-0.6.0 (2016-10-16)

### Features

* Can now parse entry as p-value (i.e. replace with stars)
* Backwards-compatible comma formatting
* Can now have multiple matches per cell
* Tolerates "NA" as missing value (for R compatibility)

### Bug fixes

* Can correctly compile bibtex (cd into dir, etc.)
* Can correctly parse too many/too few matches.
* Regexps now only tolerate one escape character.
* Regexps now accept comments with leading blanks.
