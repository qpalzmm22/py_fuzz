import isort
from pythonfuzz.main import PythonFuzz

@PythonFuzz
def fuzz(buf):
    try:
        with tempfile.NamedTemporaryFile() as af:
            af.write(buf)
        isort.file(af.name)
    except UnicodeDecodeError:
        pass

if __name__ == '__main__':
    fuzz()
