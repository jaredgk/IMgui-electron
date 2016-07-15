cd IMa
if hash mpicxx 2>/dev/null; then
	mpicxx -o IMa2 *.cpp -DMPI_ENABLED -DXML_ENABLED
else
	g++ -o IMa2 *.cpp -O2 -DXML_ENABLED
fi
