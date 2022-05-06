import os
import psutil

print("pid: ", os.getpid())
print("rss: ", psutil.Process(os.getpid()).memory_info().rss)

dict = []
count = 0
intt = 0

while True:
    dict.append(1)
    if (count%10000000) == 0:
        print("DDD size: ", len(dict))
        print("DDD rss: ", psutil.Process(os.getpid()).memory_info().rss)
   #     dict.clear()
    count += 1
    