import collections

prev_prev_prev_line = 0
prev_prev_line = 0
prev_line = 0
prev_filename = ''

func_filename = ''
func_line_no = 0

data = dict()
crashes = collections.defaultdict(set) #added
coverage = collections.defaultdict(set) 
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
        add_to_set(func_filename + ":" + prev_filename + ":" + str(prev_line) + ":" + str(func_line_no))
    else:
        add_to_set(func_filename + ":" + str(prev_line) + ":" + str(func_line_no))

    prev_prev_prev_line = prev_prev_line
    prev_prev_line = prev_line
    prev_line = func_line_no
    prev_filename = func_filename

    return trace

def add_to_set(edge):
#    print("DEBUG ", edge)
    global data
    try:
        data[edge].append("hit")
    except KeyError:
        data[edge] = []
        data[edge].append("hit")

def get_coverage(coverage):
    global data 

    # TODO test
    global prev_line
    global prev_filename

    prev_line = 0
    prev_filename = ''

    coverage = data
    print("Coverage: ", sum(map(len, coverage.values())))
    print("Data: ", sum(map(len, data.values())))

    data = {}
    print("AFTER Data: ", sum(map(len, data.values())))

    return coverage

def get_crash():
    return index

def set_crash():
    crashes[func_filename].add((prev_prev_prev_line, prev_prev_line))
#   print(func_filename, "p: ", prev_prev_prev_line, "f: ", prev_prev_line)
    global index
    index = sum(map(len, crashes.values()))
