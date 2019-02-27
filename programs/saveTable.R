# saveTable("test.txt", "<tab:testR1>", matrix(1:4, 2, 2))
# saveTable("test.txt", "<tab:testR2>", matrix(runif(4), 2, 2))

saveTable <- function (outfile, tag, outmatrix) {
    cat(tag,
        sep    = "\n",
        file   = outfile,
        append = TRUE)

    write.table(outmatrix,
                file      = outfile,
                sep       = "\t",
                append    = TRUE,
                quote     = FALSE,
                col.names = FALSE,
                row.names = FALSE)
}
