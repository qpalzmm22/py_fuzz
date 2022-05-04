import collections
import hashlib
import os
from pathlib import Path
from random import random
from re import S
from traceback import print_tb
from zipfile import ZIP_BZIP2

from numpy import TooHardError

from . import dictionnary, mutate

try:
    from random import _randbelow
except ImportError:
    from random import _inst
    _randbelow = _inst._randbelow


INTERESTING8 = [-128, -1, 0, 1, 16, 32, 64, 100, 127]
INTERESTING16 = [0, 128, 255, 256, 512, 1000, 1024, 4096, 32767, 65535]
INTERESTING32 = [0, 1, 32768, 65535, 65536, 100663045, 2147483647, 4294967295]


class Corpus(object):
    def __init__(self, dirs=None, max_input_size=4096, dict_path=None):
        self._inputs = []
        self._run_time = [] # running time of inputs
        self._mutated = [] # Mutated or not
        self._depth = [] # input depth of mutate
        self._is_favored = [] # favored or not
        
        self._total_path = set()
        self._favored = {} 
        
        self._mutation = mutate.Mutator(max_input_size, dict_path)

        self._dictpath = dict_path
        self._dict = dictionnary.Dictionary(dict_path)
        self._max_input_size = max_input_size
        self._dirs = dirs if dirs else []
        for i, path in enumerate(dirs):
            if i == 0 and not os.path.exists(path):
                os.mkdir(path)

            if os.path.isfile(path):
                self._add_file(path)
            else:
                for i in os.listdir(path):
                    fname = os.path.join(path, i)
                    if os.path.isfile(fname):
                        self._add_file(fname)

        self._seed_run_finished = not self._inputs
        self._seed_idx = 0
        self._save_corpus = dirs and os.path.isdir(dirs[0])
        self._inputs.append(bytearray(0))
        self._put_inputs()

    @property
    def length(self):
        return len(self._inputs)

    @staticmethod
    def _rand(n):
        if n < 2:
            return 0
        return _randbelow(n)

    def _put_inputs(self):
        self._run_time.append(0)
        self._mutated.append(0)
        self._depth.append(0)
        self._is_favored.append(0)


    def _add_file(self, path):
        with open(path, 'rb') as f:
            self._inputs.append(bytearray(f.read()))
            self._put_inputs()
   
    def put(self, buf):
        self._inputs.append(buf)
        self._put_inputs()
        if self._save_corpus:
            m = hashlib.sha256()
            m.update(buf)
            fname = os.path.join(self._dirs[0], m.hexdigest())
            with open(fname, 'wb') as f:
                f.write(buf)

    def Isinteresting(self, coverage):
        origin_len = len(self._total_path)
        for edge in coverage:
            self._total_path.add(edge)
        
        if(len(self._total_path) > origin_len):
            return True
        else:
            return False

    def set_time(self, idx, time):
        self._run_time.insert(idx, time)

    def get_index(self, input):
            return self._inputs.index(input)
        
            
    def UpdatedFavored(self, buf, index, time, coverage):
        isize = len(buf) * time
        for edge in coverage:
            if not edge in self._favored:
                self._favored[edge] = buf
                self._is_favored[index] += 1
            else:
                favored_idx = self._inputs.index(self._favored[edge])
                if (isize < (len(self._favored[edge]) * self._run_time[favored_idx])):
                    self._favored[edge] = buf
                    self._is_favored[favored_idx] -= 1
                    self._is_favored[index] += 1
    
    def there_is_uumutated_favored(self):
        for i in range(len(self._inputs)):
            if self._refcount[i] > 0 and self._mutated[i] is False :
               return True
        return False

    def seed_selection(self): #TODO: while
        for idx in range(len(self._inputs)):
            if self._is_favored[idx] == 1:
                return idx
            else:
                if self.there_is_uumutated_favored():
                    if random() >= 0.01:
                        continue
                elif self._mutated[idx] == 0:
                    if random() >= 0.05:
                        continue
                else:
                    if random() >= 0.25:
                        continue 
                return idx


    def generate_input(self):
        if not self._seed_run_finished:
            next_input = self._inputs[self._seed_idx]
            self._mutated[self._seed_idx] = 1
            self._depth[self._seed_idx] += 1 
            self._seed_idx += 1
            if self._seed_idx >= len(self._inputs):
                self._seed_run_finished = True
            return (self._seed_idx-1, next_input)

        idx = self.seed_selection()

#        idx = self._rand(len(self._inputs))
        buf = self._inputs[idx]
        self._mutated[idx] = 1
        self._depth[idx] += 1
#        print("DDDEUBG ", idx, " ", buf)

        return (idx, self._mutation.mutate(buf))
