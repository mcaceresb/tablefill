% saveTable("test.txt", "<tab:testMatlab1>", [[1 2]; [3 4]])
% saveTable("test.txt", "<tab:testMatlab2>", rand(2, 2))

function saveTable(outfile, tag, outmatrix)
    fh = fopen(outfile, "a");
    fprintf(fh, '%s\n', tag);
    fclose(fh);
    dlmwrite(outfile, outmatrix, '-append', 'delimiter', '\t');
end
