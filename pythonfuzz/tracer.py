import collections

prev_prev_prev_line = 0
prev_prev_line = 0
prev_line = 0
prev_filename = ''

func_filename = ''
func_line_no = 0

data = collections.defaultdict(set)
crashes = collections.defaultdict(set) #added
coverage = collections.defaultdict(set) #added
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
#    print(func_filename, "prev_line: ", prev_line, "curr_line: ", func_line_no)
    
    if func_filename != prev_filename:
        # We need a way to keep track of inter-files transferts,
        # and since we don't really care about the details of the coverage,
        # concatenating the two filenames in enough.
        add_to_set(func_filename + prev_filename, prev_line, func_line_no)
    else:
        add_to_set(func_filename, prev_line, func_line_no)

    prev_prev_prev_line = prev_prev_line
    prev_prev_line = prev_line
    prev_line = func_line_no
    prev_filename = func_filename

    return trace


def add_to_set(fname, prev_line, cur_line):
    #print(fname, " ", prev_line, " ", cur_line)
    if not data.get(fname):
        data[fname] = collections.defaultdict(int)
    data[fname][(prev_line,cur_line)] = data[fname][(prev_line, cur_line)] + 1

#def get_coverage():
#    return sum(map(len, data.values()))


def get_coverage():
    global data

    # TODO test
    global prev_line
    global prev_filename

    prev_line = 0
    prev_filename = ''

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

    data = {}
    return sum(map(len, coverage.values()))


def get_crash():
    return index

def set_crash():
    crashes[func_filename].add((prev_prev_prev_line, prev_prev_line))
#   print(func_filename, "p: ", prev_prev_prev_line, "f: ", prev_prev_line)
    global index
    index = sum(map(len, crashes.values()))
