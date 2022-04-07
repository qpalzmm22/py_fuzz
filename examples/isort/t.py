import tempfile
import isort
import sys

inp = sys.stdin.read()

f = tempfile.NamedTemporaryFile('w+', suffix='.py')
f.write(inp)

f.seek(0)
tem = f.read()
print(tem, "\n=======\n")

isort.file(f.name)	

f.seek(0)
zz = f.read()
print(zz, "\n======================\n")

sorted_code = isort.code(inp)
print(sorted_code)


# print(sorted_code)
f.close()