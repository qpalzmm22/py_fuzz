import sys

class DummyFile:
	def write(selt, x):
		pass

if __name__ == '__main__':
	close = int(input())

	if close & 1:
		sys.stdout = DummyFile()
	if close & 2:
		sys.stderr = DummyFile()

	print("zz")
