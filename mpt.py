import multiprocessing as mp

def work(value, value2):
	pname = mp.current_process().name
	print(pname, value)
	i = 0
	while 1:
		i = i +1
		if i > 1000000000:
			break


if __name__ == "__main__":
	print("tt")
	p = mp.Process(name="Sub P", target=work, args=("hello", "real"))
	p.start()
	p.join()
	print("Main Process")
