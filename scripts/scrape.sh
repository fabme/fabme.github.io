#!/usr/bin/env bash
########## PEAR #############
#python test.py -i data/pear/tops.txt -t template/pear/tops.html -d stage/pear/tops.html -p \#1
#python test.py -i data/pear/shirts.txt -t stage/pear/tops.html -d ../pear/tops.html -p \#2
#python test.py -i data/pear/trousers.txt -t template/pear/trousers_jeans.html -d stage/pear/trousers_jeans.html -p \#1
#python test.py -i data/pear/jeans.txt -t stage/pear/trousers_jeans.html -d ../pear/trousers_jeans.html -p \#2
#python test.py -i data/pear/coats_jackets.txt -t template/pear/coats_jackets.html -d ../pear/coats_jackets.html -p \#1
#python test.py -i data/pear/shorts_capris.txt -t template/pear/shorts_capris.html -d ../pear/shorts_capris.html -p \#1
#python test.py -i data/pear/skirts.txt -t template/pear/skirts_dresses.html -d stage/pear/skirts_dresses.html -p \#1
#python test.py -i data/pear/dresses.txt -t stage/pear/skirts_dresses.html -d ../pear/skirts_dresses.html -p \#2
########## APPLE #############
#python test.py -i data/apple/tops.txt -t template/apple/tops.html -d stage/apple/tops.html -p \#1
#python test.py -i data/apple/shirts.txt -t stage/apple/tops.html -d ../apple/tops.html -p \#2
python test.py -i data/apple/trousers.txt -t template/apple/trousers_jeans.html -d stage/apple/trousers_jeans.html -p \#1
python test.py -i data/apple/jeans.txt -t stage/apple/trousers_jeans.html -d ../apple/trousers_jeans.html -p \#2
python test.py -i data/apple/coats_jackets.txt -t template/apple/coats_jackets.html -d ../apple/coats_jackets.html -p \#1
python test.py -i data/apple/shorts_capris.txt -t template/apple/shorts_capris.html -d ../apple/shorts_capris.html -p \#1
python test.py -i data/apple/skirts.txt -t template/apple/skirts_dresses.html -d stage/apple/skirts_dresses.html -p \#1
python test.py -i data/apple/dresses.txt -t stage/apple/skirts_dresses.html -d ../apple/skirts_dresses.html -p \#2
