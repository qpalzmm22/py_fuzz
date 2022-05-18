import isort
from pythonfuzz.main import PythonFuzz

@PythonFuzz
def fuzz(buf):
    try:
        sorted_code = isort.code(buf.decode("ascii"))
    except UnicodeDecodeError:
        pass

if __name__ == '__main__':
    fuzz()
