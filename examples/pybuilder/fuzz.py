# Fuzz cli options

from pythonfuzz.main import PythonFuzz

@PythonFuzz
def fuzz(buf):

    if(len(buf) < 8):
        return

    file_ext = buf[:8]
    file_ext = file_ext.decode("ascii")
    file_content = buf[8:]

    try:
        with tempfile.NamedTemporaryFile(suffix=file_ext) as af:
            print(af.name)
    except ValueError:
        pass

if __name__ == '__main__':
    fuzz()
