from furl import furl
from pythonfuzz.main import PythonFuzz

@PythonFuzz
def fuzz(buf):
    try:
        url = buf.decode("ascii")
        f = furl(url)
    except UnicodeDecodeError:
        pass

if __name__ == '__main__':
    fuzz()
