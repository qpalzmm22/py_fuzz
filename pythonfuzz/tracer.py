import collections
import sys

prev_prev_prev_line = 0
prev_prev_line = 0
prev_line = 0
prev_filename = ''

func_filename = ''
func_line_no = 0

data = collections.defaultdict(set)
crashes = collections.defaultdict(set) #added
index = 0

def trace(frame, event, arg):
    if event != 'line':
        return trace

    global prev_prev_prev_line
    global prev_prev_line
    global prev_line
    global prev_filename

    func_filename = frame.f_code.co_filename
    func_line_no = frame.f_lineno
 #   print(func_filename, "prev_line: ", prev_line, "curr_line: ", func_line_no)
    
    if func_filename != prev_filename:
        # We need a way to keep track of inter-files transferts,
        # and since we don't really care about the details of the coverage,
        # concatenating the two filenames in enough.
        data[func_filename + prev_filename].add((prev_line, func_line_no))
    else:
        data[func_filename].add((prev_line, func_line_no))

    prev_prev_prev_line = prev_prev_line
    prev_prev_line = prev_line
    prev_line = func_line_no
    prev_filename = func_filename

    return trace


def get_coverage():
    return sum(map(len, data.values()))

def get_crash():
    return index

def set_crash():
    crashes[func_filename].add((prev_prev_prev_line, prev_prev_line))
#    print(func_filename, "p: ", prev_prev_prev_line, "f: ", prev_prev_line)
    global index
    index = sum(map(len, crashes.values()))
