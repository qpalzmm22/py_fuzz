import tempfile
import isort
import sys

inp = sys.stdin.read()
#string = inp.decode("ascii")

print("INPUT: ", inp)

f = tempfile.NamedTemporaryFile('w+', suffix='.py')
print("fname: ", f.name)
print("Write: ", f.write(inp))

f.seek(0)
#data = print("Read: ", f.read())
data = f.read()
print("Data: ", data)

isort.file(f.name)	

# sorted_code = isort.code(inp)
# print(sorted_code)

f.close()
