#!/bin/bash

rm log.csv
rm -r seed_ext
cp -r bsd seed_ext

pip install ../..

python3 fuzz.py --inf-run seed_ext | tee debug_ext
#python3 fuzz.py --inf-run --run 4000000
