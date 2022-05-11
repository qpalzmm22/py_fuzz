import collections
import sys

prev_prev_prev_line = 0
prev_prev_line = 0
prev_line = 0
prev_filename = ''

func_filename = ''
func_line_no = 0

# TODO
# refactor name, "edges" to "edges_hit_count" or something like that
edges = {}
index = 0
crashes = collections.defaultdict(set)

def trace(frame, event, arg):
    if event != 'line':
        return trace

    global prev_prev_prev_line
    global prev_prev_line
    global prev_line
    global prev_filename

    func_filename = frame.f_code.co_filename
    func_line_no = frame.f_lineno

    if func_filename != prev_filename:
        # We need a way to keep track of inter-files transferts,
        # and since we don't really care about the details of the coverage,
        # concatenating the two filenames in enough.
        add_to_set(prev_filename + ":" + str(prev_line) + func_filename + ":" + str(func_line_no))
    else:
        add_to_set(func_filename + ":" + str(prev_line) + ":" + str(func_line_no))
    
    prev_prev_prev_line = prev_prev_line
    prev_prev_line = prev_line
    prev_line = func_line_no
    prev_filename = func_filename

    return trace


def add_to_set(edge):
    #print(fname, " ", prev_line, " ", cur_line)
    if not edges.get(edge):
        edges[edge] = 0
    edges[edge] = edges[edge] + 1


def get_coverage():
    global edges
    global prev_line
    global prev_filename

    coverage = {}

    for edge in edges:
        if(edges[edge] <= 1):
            coverage[edge] = 0
        elif(edges[edge] <= 2):
            coverage[edge] = 1
        elif(edges[edge] <= 3):
            coverage[edge] = 2
        elif(edges[edge] <= 16):
            coverage[edge] = 3
        elif(edges[edge] <= 32):
            coverage[edge] = 4
        elif(edges[edge] <= 64):
            coverage[edge] = 5
        elif(edges[edge] <= 128):
            coverage[edge] = 6
        else:
            coverage[edge] = 7
    #print(coverage)
    edges = {}
    prev_line = 0
    prev_filename = ""

    return coverage

def get_crash():
	return index

def set_crash():
	crashes[func_filename].add((prev_prev_prev_line, prev_prev_line))

	global index
	index = sum(map(len, crashes.values()))
