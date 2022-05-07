import collections

prev_prev_prev_line = 0
prev_prev_line = 0
prev_line = 0
prev_filename = ''

func_filename = ''
func_line_no = 0

data = {}
index = 0
crashes = collections.defaultdict(set) #added

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
        add_to_set(prev_filename + ":" + func_filename + ":" + str(prev_line) + ":" + str(func_line_no))
        #data[]
    else:
        add_to_set(func_filename + ":" + str(prev_line) + ":" + str(func_line_no))
        #data[]

    prev_prev_prev_line = prev_prev_line
    prev_prev_line = prev_line
    prev_line = func_line_no
    prev_filename = func_filename

    return trace

def add_to_set(edge):
    if data.get(edge) is None:
        data[edge] = 0
    data[edge] = data[edge] + 1

def get_coverage():
    global data 
    # TODO test
    global prev_line
    global prev_filename

    prev_line = 0
    prev_filename = ''

    coverage = {}
    for edge in data:
        if(data[edge] <= 1):
            coverage[edge] = 0
        elif(data[edge] <= 2):
            coverage[edge] = 1
        elif(data[edge] <= 3):
            coverage[edge] = 2
        elif(data[edge] <= 16):
            coverage[edge] = 3
        elif(data[edge] <= 32):
            coverage[edge] = 4
        elif(data[edge] <= 64):
            coverage[edge] = 5
        elif(data[edge] <= 128):
            coverage[edge] = 6
        else:
            coverage[edge] = 7  

#    for edge in coverage:
#        print(edge, " ",  coverage[edge].count('hit'))

#    print("Coverage: ", sum(map(len, coverage.values())))
#    print("Data: ", sum(map(len, data.values())))

    data = {}
    return coverage

def get_crash():
    return index

def set_crash():
    crashes[func_filename].add((prev_prev_prev_line, prev_prev_line))
#   print(func_filename, "p: ", prev_prev_prev_line, "f: ", prev_prev_line)
    global index
    index = sum(map(len, crashes.values()))

