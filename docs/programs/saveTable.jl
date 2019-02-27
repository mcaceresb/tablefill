# saveTable("test.txt", "<tab:testJulia1>", [[1 2]; [3 4]])
# saveTable("test.txt", "<tab:testJulia2>", rand(2, 2))

using DelimitedFiles

function saveTable(outfile, tag, outmatrix)
    open(outfile, "a") do file
        write(file, "$(tag)\n")
        writedlm(file, outmatrix, "\t")
    end
end
