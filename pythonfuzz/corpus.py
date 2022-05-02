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
    def __init__(self, dirs=None, max_input_size=4096, dict_path=None):
        # inputs and path are coordinated with index
        self._inputs = []
        self._total_path = set()
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
        self._select_idx = 0
        self._save_corpus = dirs and os.path.isdir(dirs[0])
        self._mutation = mutation.Mutation(max_input_size, dict_path)
        self._inputs.append(bytearray(0))

    def _add_file(self, path):
        with open(path, 'rb') as f:
            self._inputs.append(bytearray(f.read()))

    @property
    def length(self):
        return len(self._inputs)

    def put(self, buf):
        self._inputs.append(buf)
        if self._save_corpus:
            m = hashlib.sha256()
            m.update(buf)
            fname = os.path.join(self._dirs[0], m.hexdigest())
            with open(fname, 'wb') as f:
                f.write(buf)

    # returns the index of the input
    def seed_selection(self):
        idx = self._seed_idx
        
        self._seed_idx += 1
        if self._seed_idx >= len(self._inputs):
            self._seed_idx = 0
            if not self._seed_run_finished:
                self._seed_run_finished = True
        return idx
    
    def isInteresting(self, coverage):
        orig_len = len(self._total_path)
        for edge in coverage :
            self._total_path.add(edge)
        
        #self._total_path = self._total_path.union(coverage)
        if(orig_len < len(self._total_path)):
            return True
        else:
            return False
    
    def generate_input(self):
        
        buf_ind = self.seed_selection()

        buf = self._inputs[buf_ind]
        if self._seed_run_finished:
            return self._mutation.mutate(buf)
        else: 
            return buf
