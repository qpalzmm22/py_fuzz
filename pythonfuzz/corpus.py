import hashlib
import os
from pathlib import Path
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
        self._path = [] # path of a input
        self._total_path = []
        
        self._extensions = []
        self._depth = [] # input depth of mutate
        self._mutated = [] # Mutated or not
        
        self._favored = [] # favored of a branch, set?
        self._time = []
        self._size = []

        self._dictpath = dict_path
        self._dict = dictionnary.Dictionary(dict_path)
        self._max_input_size = max_input_size
        self._dirs = dirs if dirs else []
        for i, path in enumerate(dirs):
            if i == 0 and not os.path.exists(path):
                os.mkdir(path)

            if os.path.isfile(path):
                self._add_file(path)
                self._extensions.append(Path(path).suffix)
            else:
                for i in os.listdir(path):
                    fname = os.path.join(path, i)
                    if os.path.isfile(fname):
                        self._add_file(fname)
                        self._extensions.append(Path(fname).suffix)


        self._seed_run_finished = not self._inputs
        self._seed_idx = 0
        self._save_corpus = dirs and os.path.isdir(dirs[0])
        self._inputs.append(bytearray(0))
        self._extensions.append('')

    @property
    def length(self):
        return len(self._inputs)

    @staticmethod
    def _rand(n):
        if n < 2:
            return 0
        return _randbelow(n)


    def _add_file(self, path):
        with open(path, 'rb') as f:
            self._inputs.append(bytearray(f.read()))
   
    def put(self, buf):
        self._inputs.append(buf)
        if self._save_corpus:
            m = hashlib.sha256()
            m.update(buf)
            fname = os.path.join(self._dirs[0], m.hexdigest())
            with open(fname, 'wb') as f:
                f.write(buf)

    def put_extension(self, extension):
        self._extensions.append(extension)

    def Isinteresting():
        print()

    def UpdatedFavored():
        print()
    
    def generate_input(self):
        if not self._seed_run_finished:
            next_input = self._inputs[self._seed_idx]
            self._seed_idx += 1
            if self._seed_idx >= len(self._inputs):
                self._seed_run_finished = True
            return next_input
        
        # TODO seed selection

        buf = self._inputs[self._rand(len(self._inputs))]
        mutator = mutate.Mutator(buf, len(self._inputs), self._max_input_size, self._dictpath)

        return mutator.mutate()

    def generate_input_for_file(self):
        if not self._seed_run_finished:
            next_input = self._inputs[self._seed_idx]
            next_extension = self._extensions[self._seed_idx]
            self._seed_idx += 1
            if self._seed_idx >= len(self._inputs):
                self._seed_run_finished = True
            return (next_input, next_extension)

        rand_num = self._rand(len(self._inputs))

        buf = self._inputs[rand_num]
        extension = self._extensions[rand_num]
        mutator = mutate.Mutator(buf, len(self._inputs), self._max_input_size, self._dictpath)
        
        return (mutator.mutate(), extension)
    