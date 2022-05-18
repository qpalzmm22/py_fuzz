#!/bin/bash
# removes inp seeds and crashes

mv ./seed/inp ./inp

rm ./seed/*

mv ./inp ./seed/inp

rm ./crashes/*

rm log.csv
