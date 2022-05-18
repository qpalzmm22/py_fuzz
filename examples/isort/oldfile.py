from pythonfuzz.main import PythonFuzz
import isort

@PythonFuzz
def fuzz(buf):
	try:
		fname = buf.decode("ascii")
		isort.file(fname)
	except UnicodeDecodeError:
		pass

if __name__ == '__main__':
	fuzz()
