import collections
import sys

prev_line = 0
prev_filename = ''

func_filename = ''
func_line_no = 0
# TODO
# refactor name, "edges" to "edges_hit_count" or something like that
# refactor name, "coverage" to "gloval_hit_count" or something like that
edges = {}
coverage = collections.defaultdict(set)
txlen = {}
index = 0

# 1. consider files as index
# 2. use the filenames + line number as is
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
        add_to_set(func_filename + ":" + str(prev_line) + prev_filename + ":" + str(func_line_no))
    else:
        add_to_set(func_filename + ":" + str(prev_line) + ":" + str(func_line_no))

    prev_line = func_line_no
    prev_filename = func_filename

    return trace

def add_to_set(edge):
 #   print(fname, " ", prev_line, " ", cur_line)
    if edges.get(edge) is None:
        edges[edge] = 0
    edges[edge] = edges[edge] + 1

def add_to_coverage():
    global edges

    for edge in edges:
        if(edges[edge] <= 1):
            coverage[edge].add(0)
        elif(edges[edge] <= 2):
            coverage[edge].add(1)
        elif(edges[edge] <= 3):
            coverage[edge].add(2)
        elif(edges[edge] <= 16):
            coverage[edge].add(3)
        elif(edges[edge] <= 32):
            coverage[edge].add(4)
        elif(edges[edge] <= 64):
            coverage[edge].add(5)
        elif(edges[edge] <= 128):
            coverage[edge].add(6)
        else:
            coverage[edge].add(7)

def get_coverage():
    add_to_coverage()
    
    return sum(map(len, coverage.values()))


def update_favored(buf, time, favored):
    global txlen
    global edges
    
    if len(buf) == 0:
        return favored
    val = len(buf) * time
    for edge in edges.keys():
        if txlen.get(edge) is None:
            txlen[edge] = val
            favored[edge] = buf
            #print("NEW] val: " + str(val)  )
        elif(val < txlen[edge]): 
            txlen[edge] = val
            favored[edge] = buf
            #print("Update] val: " + str(val)  )
    edges = {}
    return favored

