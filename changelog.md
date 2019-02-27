# Changelog

## tablefill-0.9.2 (2019-02-26)

### Features

- Markdown support:

    <!-- tablefill:start tab:label -->

    Table with placeholders

    <!-- tablefill:end -->

## tablefill-0.9.1 (2018-07-17)

### Features

- Pip-installable by [@kylebarron](https://github.com/kylebarron).

## tablefill-0.9.0 (2018-07-17)

### Bug Fixes

- Python 3 support. Fixes https://github.com/mcaceresb/tablefill/issues/2
- Encloses all filters in `list`
- File concatenation replaces deprecated `U` flag for `newline = None`
- `nested_convert` avoids iterating over strings.
- output file is opened as `w` instead of `wb`

## tablefill-0.8.1 (2017-06-13)

### Features

- Old XML parsing available via `--legacy-parsing`
- Basic XML error checks
- Numpy syntax can do string and numeric numpy matrices.
- XML engine parses all entries to numeric and string
  dictionaries and parses strings and floats sepparately.

## tablefill-0.8.0 (2017-04-11)

### Features

- `<tablefill-custom>` has been moved to `<tablefill-python>`
    - The engine now evaluates whatever is in the tag.
    - All the tables are available as python lists of lists
    - The resulting object is read into the specified tag
    - Can pass `syntax = 'numpy'` to use `numpy` matrix syntax instead of
      python list slicing.
    - Can pass `type = 'float'` so all entries in each table
      are available as floats instead of strings.
    - WARNING: When using `type = float` the conversion is NOT
      necessarily lossless, as with the normal tablefill you can also
      have placeholders be replaced with strings. But if you try to
      convert everything to floats then you will replace those with
      missing. This would only affect tables created this way.
- When tablefill call is empty, nothing is parsed. In previous
  versions the entire table was added.
- The default syntax can be changed to `numpy` via `--use-numpy`
- The default conversion can be changed to `float` via `--use-floats`

An example:
```xml
<tablefill-python tag = 'output_table' type = 'float'>
    input_table0[1][2], input_table0[2][1],
    input_table0[1][2] / input_table0[2][1],
</tablefill-python>

<tablefill-python tag = 'output_table' type = 'float' syntax = 'numpy'>
    input_table0[:2, :2] / input_table1[:2, :2]
</tablefill-python>
```

### Planned

- Error checking for XML parsing: Currently very minimal
  error checks are in place as this functionality is beta.
  - If XMl file is provided, note if parsing failed in that file
  - If multiple XML files provided, give file name as well
  - Whether error was due to regex parsing
  - Whether an opened tag was closed
  - Closing a tag and opening the next tag on the same line
  - Etc.
- Replace tablefill-python with a more limited tablefill-math
  so that I don't have to worry about executing arbitrary python
  code. It's bad practice, no?
- Replace engine with eval using the table dictionary as the context to
  simplify syntax. This would result in, for instance
```xml
<tablefill-custom tag = 'newtagname'>
    tagname[rows1][subentries1],
    tagname[rows2][subentries2],
    tagname[rows3][subentries3],
    othertagname[rows3][subentries3]
</tablefill-custom>
```
This would also simplify the function call for math... Have a float
dictionary and a normal one. Use the float dictionary for `type =
'float'` and the string otherwise. Always update both. Then for

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
