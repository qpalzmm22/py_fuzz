from itertools import tee
from tinytag import TinyTag
import tempfile
import random

def suffix():
	randnum = random.randint(0, 3)
	if(randnum == 0):
		return ".mp4"
	elif(randnum == 1):
		return ".mp3"
	elif(randnum == 2):
		return ".WMA"
	elif(randnum == 3):
		return ".riff"

a = input()
#f= tempfile.NamedTemporaryFile('w+', suffix=suffix())
f= tempfile.NamedTemporaryFile('w+')
f.write(a)

print("F_name: ", f.name)
f.seek(0)
zz = f.read()
print("Content: ", zz)

tag = TinyTag.get(f.name)
print(tag.artist)
print(tag.duration)
print(tag.filesize)
print(tag.track)
print(tag.year)
print(tag.comment)
print(tag.disc)

f.close()
