import tempfile
import isort
import sys

inp = sys.stdin.read()
#string = inp.decode("ascii")

f = tempfile.NamedTemporaryFile('w+', suffix='.py')
f.write(inp)

isort.file(f.name)	
sorted_code = isort.code(inp)
print(sorted_code)

f.close()
