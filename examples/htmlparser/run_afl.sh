#!/bin/bash

rm log.csv
rm -r seed
cp -r bsd seed

pip install ../..

python3 fuzz.py --inf-run seed --sched afl | tee debug
#python3 fuzz.py --inf-run --run 4000000
