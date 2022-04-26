from pythonfuzz.main import PythonFuzz
import tempfile
import isort

@PythonFuzz
def fuzz(buf):
	try:
		string = buf.decode("ascii")
		f = tempfile.NamedTemporaryFile('w+')
		f.write(string)
		
#		print("DEBUG fname: ", f.name)
		f.seek(0)
#		content = f.read()
#		print("DEBUG Content: ", content)

		isort.file(f.name)
		f.close()
	except UnicodeDecodeError:
		pass

if __name__ == '__main__':
	fuzz()
