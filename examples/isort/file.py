from pythonfuzz.main import PythonFuzzFile
import isort

@PythonFuzzFile
def fuzz():
	try:
		isort.file(PythonFuzzFile._fuzzfile)
	except UnicodeDecodeError:
		pass

if __name__ == '__main__':
	fuzz()
