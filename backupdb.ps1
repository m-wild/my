sqlite3 ./mwild.db "vacuum;"
sqlite3 ./mwild.db ".backup mwild.db.bak"
mv .\mwild.db.bak ~/OneDrive/.backup -force
