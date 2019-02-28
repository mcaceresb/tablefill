* matrix test = (1, 2 \ 3, 4)
* saveTable using "test.txt", tag("<tab:testStata1>") outmatrix(test)
*
* mata: st_matrix("test", runiform(2, 2))
* saveTable using "test.txt", tag("<tab:testStata2>") outmat(test)

capture program drop saveTable
program saveTable
    version 13
    syntax using/, tag(str) OUTMatrix(name) [Format(str)]
    mata: saveTable()
end

capture mata: mata drop saveTable()
mata:
void function saveTable()
{
    real scalar i, j, fh
    real matrix outmatrix
    outmatrix = st_matrix(st_local("outmatrix"))
    fmt = st_local("format")
    if ( fmt == "" ) {
        fmt = "%21.9f"
    }
    fmt = "\t" + fmt
    fh  = fopen(st_local("using"), "a")
    fwrite(fh, sprintf("%s\n", st_local("tag")))
    for(i = 1; i <= rows(outmatrix); i++) {
        for(j = 1; j <= cols(outmatrix); j++) {
            fwrite(fh, sprintf(fmt, outmatrix[i, j]))
        }
        fwrite(fh, sprintf("\n"))
    }
    fclose(fh)
}
end
