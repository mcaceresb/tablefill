Matrix Input
============

!!! info "Warning"
    This page is under construction

Input files must be tab-delimited rows of numbers or characters,
preceded by `<label>`. The numbers can be arbitrarily long, can be
negative, and can also be in scientific notation.

```
<tab:Test>
1	2	3
2	3	1
3	1	2
```

The rows do not need to be of equal length.

```
<tab:FunnyMat>
1	2	3	23	2
2	3
3	1	2	2
1
```

Completely blank (no tab) lines are ignored. If a "cell" is merely ".",
"[space]", or "NA" then it is treated as missing. That is, in the program:

```
<tab:Test>
1	2	3
2	.	1	3
3	    1	2
```

is equivalent to:

```
<tab:Test>
1	2	3
2	1	3
3	1	2
```

This feature is useful as several languages outputs missing values as
NA, blank, or ".". Last, `tablefill` understands scientific notation of
the form: `[numbers].[numbers]e(+/-)[numbers]`

    <tab:TestScientific>
    23.2389e+23
    -2.23e-2
    -0.922e+3
