import collections
import sys

#mydic = dict() #collections.defaultdict(set)
#mydic['one'] = []

#mydic['one'].insert(1)

#mydic['one'] += 1
#mydic['one'].add(('fname1,3'))
#mydic['one'].add(('fname1,2'))
#mydic['one'].add(('fname2,1,2'))

#print(list(mydic))
#print(len(mydic))
#print(mydic['one'])


cdic = dict()
cdic['1'] = [] # key - coverage
cdic['2'] = [] # key - coverage
cdic['3'] = [] # key - coverage

cdic['1'].append("zz") #
cdic['1'].append("zz") #
cdic['2'].append("zz") #
cdic['3'].append("zz") #
cdic['1'].append("zz")

len(cdic['1']) # hit count
#.append(mydic['one'])

print("=================")

print(cdic['1'])
print(cdic.values())
print(cdic['1'].count('zz'))
print(cdic['2'].count('zz'))
print(cdic['1'].index('zz'))
print(sum(map(len, cdic.values())))


#print(a['one'].pop)
