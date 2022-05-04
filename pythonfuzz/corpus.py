import hashlib
import math
import os
import random
import struct
from zipfile import ZIP_BZIP2

from numpy import TooHardError

from . import dictionnary
from . import mutation

class Corpus(object):
    def __init__(self, dirs=None, max_input_size=4096, dict_path=None, timeout=120):
        # inputs and path are coordinated with index
        self._inputs = []

        self._input_path = []
        self._refcount = []
        self._time = []
        self._mutated = []
        
        self._favored = {}
        self._total_path = set()
        self._timeout = timeout
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
        self._seed_run_finished = False
        self._seed_idx = 0
        self._save_corpus = dirs and os.path.isdir(dirs[0])
        self._mutation = mutation.Mutation(max_input_size, dict_path)
        self.enqueue(bytearray(0))

    def _add_file(self, path):
        with open(path, 'rb') as f:
            self.enqueue(bytearray(f.read()))

    @property
    def length(self):
        return len(self._inputs)

    def put(self, buf):
        if self._save_corpus:
            m = hashlib.sha256()
            m.update(buf)
            fname = os.path.join(self._dirs[0], m.hexdigest())
            with open(fname, 'wb') as f:
                f.write(buf)
        return self.enqueue(buf)

    def enqueue(self, buf):
        self._inputs.append(buf)
        idx = len(self._inputs) - 1
        self._time.append(self._timeout)
        self._mutated.append(False)
        self._refcount.append(0)
        return idx

    def is_interesting(self, coverage):
        orig_len = len(self._total_path)
        for edge, hitcount in coverage.items() :
            self._total_path.add((edge, hitcount))
        if orig_len < len(self._total_path):
            return True
        else:
            return False
    
    def update_favored(self, idx, buf, time, coverage):
        for edge in coverage :
            if not edge in self._favored:
                self._favored[edge] = buf
                self._time[idx] = time
                self._refcount[idx] += 1
            else:
                favored_idx = self._inputs.index(self._favored[edge])
                if time * len(buf) < self._time[favored_idx] * len(self._favored[edge]) :
                    self._favored[edge] = buf
                    self._time[idx] = time
                    self._refcount[favored_idx] -= 1
                    self._refcount[idx] += 1
    
    def is_there_unmutated_favored(self):
        for i in range(len(self._refcount)) :
            if self._refcount[i] > 0 and self._mutated[i] is False :
               return True
        return False
    
    # returns the index of the input
    def seed_selection(self):
        while True:
            if(self._refcount[self._seed_idx] == 0) :
                if self.is_there_unmutated_favored():
                    if random.random() >= 0.01 :
                        continue
                elif self._mutated[self._seed_idx] is True:
                    if random.random() >= 0.05 :
                        continue
                else :
                    if random.random() >= 0.25 :
                        continue

            self._seed_idx += 1
            if self._seed_idx >= len(self._inputs):
                self._seed_idx = 0
            break

        return self._seed_idx

    def generate_input(self):
        
        if self._seed_run_finished:
            buf_idx = self.seed_selection()
            buf = self._inputs[buf_idx]
            self._mutated[buf_idx] = True
            return self._mutation.mutate(buf)
        else:
            buf_idx = self._seed_idx
            buf = self._inputs[buf_idx]
            self._seed_idx += 1
            if(self._seed_idx >= len(self._inputs)):
                self._seed_idx = 0
                self._seed_run_finished = True
            return buf
