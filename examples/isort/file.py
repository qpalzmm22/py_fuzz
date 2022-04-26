from pythonfuzz.main import PythonFuzz
import isort

@PythonFuzz
def fuzz(buf):
	try:
		fname = buf.decode("ascii")
#		print("DEBUG fname: ", fname)
#		f = open(fname, 'rb+')
#		f.seek(0)
#		content = f.read()
#		print("DEBUG Content: ", content)
		isort.file(fname)
#		f.close()
	except (UnicodeDecodeError, ValueError):
		pass

if __name__ == '__main__':
	fuzz()
