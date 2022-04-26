from pythonfuzz.main import PythonFuzz
from tinytag import TinyTag

@PythonFuzz
def fuzz(buf):
	try:
		f_name = buf.decode("ascii")
		tag = TinyTag.get(f_name)
	
	except (UnicodeDecodeError, ValueError):
		pass

if __name__ == '__main__':
	fuzz()


