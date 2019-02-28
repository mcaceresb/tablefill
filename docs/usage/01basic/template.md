<!-- tablefill:start tab:paragraph -->

Sample paragraph referring to a number: e.g. $N = #0,#$.  Or perhaps
text: e.g. This is the ### sample. You can also fill text using
python-style formatting: #{}#.

<!-- tablefill:end -->

<!-- tablefill:start tab:example -->

| Outcomes     | N    | Mean | (Std.) |
| ------------ | ---- | ---- | ------ |
| Outcomes ### | #0,# | #1,# | (#2,#) |
| Outcomes ### | #0,# | #1,# | (#2,#) |
| Outcomes ### | #0,# | #1,# | (#2,#) |
| Outcomes ### | #0,# | #1,# | (#2,#) |

<!-- tablefill:end -->

`pandoc` will compile raw LaTeX inside markdown documents, so
`tablefill` will also replace placeholders in LaTeX tables inside
markdown files:

\begin{table}
  \caption{Table caption (e.g. regression results)}
  \label{tab:anotherExample}
  \begin{tabular}{p{4.25cm}c}
    Outcomes
    & Coef
    & (SE)
    \\
    Variable 1 & \#{:.1f}\# (\#{:.2f}\#)\#*\# \\
    Variable 2 & \#{:.1f}\# (\#{:.2f}\#)\#*\# \\
    Variable 3 & \#{:.1f}\# (\#{:.2f}\#)\#*\# \\
    \midrule
             N & \#{:,.0f}\# \\
    \multicolumn{4}{p{5cm}}{\footnotesize Footnotes!}
  \end{tabular}
\end{table}
\end{document}
