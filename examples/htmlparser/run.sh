#!/bin/bash

rm log.csv
rm -r seed
cp -r bsd seed

pip uninstall -y pythonfuzz
pip install ../..

python fuzz.py --inf-run --sched afl seed
