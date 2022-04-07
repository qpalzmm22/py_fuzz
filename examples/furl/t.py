from furl import furl

f = furl(input())
print(f)
print(f.path.segments)
f.path.normalize()
print(f)

