from pythonfuzz.main import PythonFuzzFile
import isort

@PythonFuzzFile
def fuzz():
	try:
		isort.file(fname)
	except UnicodeDecodeError:
		pass

if __name__ == '__main__':
	fuzz()
