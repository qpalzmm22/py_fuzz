import tempfile
from tinytag import TinyTag
from pythonfuzz.main import PythonFuzz

@PythonFuzz
def fuzz(buf):

    if(len(buf) < 8):
        return

    try:
        file_ext = buf.decode("ascii")
        file_ext = file_ext[:8]
        file_content = buf[8:]
        with tempfile.NamedTemporaryFile(suffix=file_ext) as af:
            af.write(file_content)
            TinyTag.get(af.name)
 #           print(af.name)
    except UnicodeDecodeError:
        pass

if __name__ == '__main__':
   fuzz()
