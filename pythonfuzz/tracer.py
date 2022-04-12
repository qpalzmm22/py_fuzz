import collections
import sys

prev_line = 0
prev_filename = ''

func_filename = ''
func_line_no = 0

data = collections.defaultdict(set)
coverage = collections.defaultdict(set)
index = 0

edges = []

def trace(frame, event, arg):
    if event != 'line':
        return trace

    global prev_line
    global prev_filename

    func_filename = frame.f_code.co_filename
    func_line_no = frame.f_lineno

    if func_filename != prev_filename:
        # We need a way to keep track of inter-files transferts,
        # and since we don't really care about the details of the coverage,
        # concatenating the two filenames in enough.
        add_to_set(func_filename + prev_filename, prev_line, func_line_no)
    else:
        add_to_set(func_filename, prev_line, func_line_no)
    

    prev_line = func_line_no
    prev_filename = func_filename

    return trace


def add_to_set(fname, prev_line, cur_line):
    #print(fname, " ", prev_line, " ", cur_line)
    if not data.get(fname):
        data[fname] = collections.defaultdict(int)
    data[fname][(prev_line,cur_line)] = data[fname][(prev_line, cur_line)] + 1


def get_coverage():
    global prev_line
    global prev_filename
    global data
    
    for x in data:
        for y in data[x]:
            if(data[x][y] <= 1):
                coverage[x].add((y, 0))
            elif(data[x][y] <= 2):
                coverage[x].add((y, 1))
            elif(data[x][y] <= 3):
                coverage[x].add((y, 2))
            elif(data[x][y] <= 16):
                coverage[x].add((y, 3))
            elif(data[x][y] <= 32):
                coverage[x].add((y, 4))
            elif(data[x][y] <= 64):
                coverage[x].add((y, 5))
            elif(data[x][y] <= 128):
                coverage[x].add((y, 6))
            else:
                coverage[x].add((y, 7))
    
    prev_line = 0
    prev_filename = ''
    data = {}
    #print(coverage)   
    return sum(map(len, coverage.values()))
