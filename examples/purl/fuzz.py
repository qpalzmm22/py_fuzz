from pythonfuzz.main import PythonFuzz
from purl import URL

@PythonFuzz
def fuzz(buf):
	try:
		string = buf.decode("ascii")
		URL(string)
	except UnicodeDecodeError:
		pass

if __name__ == '__main__':
	fuzz()
