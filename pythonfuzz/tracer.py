import collections
import sys

prev_line = 0
prev_filename = ''

func_filename = ''
func_line_no = 0

edges = collections.defaultdict(set)
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
    if not edges.get(fname):
        edges[fname] = collections.defaultdict(int)
    edges[fname][(prev_line,cur_line)] = edges[fname][(prev_line, cur_line)] + 1


def get_coverage():
    global edges
    
    for filename in edges:
        for edge in edges[filename]:
            if(edges[filename][edge] <= 1):
                coverage[filename].add((edge, 0))
            elif(edges[filename][edge] <= 2):
                coverage[filename].add((edge, 1))
            elif(edges[filename][edge] <= 3):
                coverage[filename].add((edge, 2))
            elif(edges[filename][edge] <= 16):
                coverage[filename].add((edge, 3))
            elif(edges[filename][edge] <= 32):
                coverage[filename].add((edge, 4))
            elif(edges[filename][edge] <= 64):
                coverage[filename].add((edge, 5))
            elif(edges[filename][edge] <= 128):
                coverage[filename].add((edge, 6))
            else:
                coverage[filename].add((edge, 7))
    
    edges = {}
    return sum(map(len, coverage.values()))


