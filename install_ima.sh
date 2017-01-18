cd IMa/
if hash mpicxx 2>/dev/null; then
	mpicxx -o IMa2 *.cpp -w -DMPI_ENABLED -DXML_ENABLED
	sed -i 's/var compile_multithread = 0/var compile_multithread = 1/' ../main.js
else
	g++ -o IMa2 *.cpp -O2 -w -DXML_ENABLED
fi
