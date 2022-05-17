#!/bin/bash

rm log.csv
rm -r seed
cp -r bsd seed

pip install ../..

python fuzz.py --inf-run seed
