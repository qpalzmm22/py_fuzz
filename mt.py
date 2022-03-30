def copy(src, dst, start_source, start_dst, end_source=None, end_dst=None):
    end_source = len(src) if end_source is None else end_source
    end_dst = len(dst) if end_dst is None else end_dst
    byte_to_copy = min(end_source-start_source, end_dst-start_dst)
    src[start_source:start_source+byte_to_copy] = dst[start_dst:start_dst+byte_to_copy]

def mutate(buf):
	res = buf[:]
	pos0 = self.

if __name__ == '__main__':
	a = input()
	print("a: ", a)


