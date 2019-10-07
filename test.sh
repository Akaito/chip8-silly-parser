#!/bin/bash

./tobytes.py program.txt program.bin --verbose
./tobytes.py assembly.txt assembly.bin --verbose

od -tx1 program.bin > program-od.txt
od -tx1 assembly.bin > assembly-od.txt
diff program-od.txt assembly-od.txt

###
echo "~~~ newops-test.txt ~~~"

./tobytes.py newops-testopcodes.txt newops-testopcodes.bin --verbose
./tobytes.py newops-test.txt newops-test.bin --verbose
od -tx1 newops-testopcodes.bin > newops-testopcodes-od.txt
od -tx1 newops-test.bin > newops-test-od.txt
diff newops-testopcodes-od.txt newops-test-od.txt

