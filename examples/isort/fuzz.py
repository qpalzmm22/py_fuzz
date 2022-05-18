from pythonfuzz.main import PythonFuzz
import tempfile
import isort

@PythonFuzz
def fuzz(buf):
	try:
		string = buf.decode("ascii")
		f = tempfile.NamedTemporaryFile('w+', suffix='.py')
		f.write(string)
		isort.file(f.name)
		
		sorted_code = isort.code(string)
		f.close()
	except UnicodeDecodeError:
		pass

if __name__ == '__main__':
	fuzz()
