import hashlib
import math
import os
import random
import struct
#import copy
from zipfile import ZIP_BZIP2

from numpy import TooHardError

from . import dictionnary
from . import mutation

class Corpus(object):
    def __init__(self, dirs=None, max_input_size=4096, dict_path=None):
        # inputs and path are coordinated with index
        self._inputs = []

        self._input_path = []
        self._refcount = []
        self._time = []
        self._mutated = []
        self._depth = []
        
        self._favored = {}
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
        self._seed_run_finished = False
        self._seed_idx = -1
        self._init_seed_size = 0
        self._save_corpus = dirs and os.path.isdir(dirs[0])
        self._mutation = mutation.Mutation(max_input_size, dict_path)
        self.enqueue(bytearray(0))

    def _add_file(self, path):
        with open(path, 'rb') as f:
            self.enqueue(bytearray(f.read()))

    @property
    def length(self):
        return len(self._inputs)

    def put(self, buf, depth):
        if self._save_corpus:
            m = hashlib.sha256()
            m.update(buf)
            fname = os.path.join(self._dirs[0], m.hexdigest())
            with open(fname, 'wb') as f:
                f.write(buf)
        idx = self.enqueue(buf)
        self._depth[idx] = depth
        return idx

    def enqueue(self, buf):
        self._inputs.append(buf)
        idx = len(self._inputs) - 1
        self._time.append(0)
        self._mutated.append(False)
        self._refcount.append(0)
        self._depth.append(0)
        return idx

    def is_det_ran(self):
        if self._depth[self._seed_idx] > 0:
            return True
        else :
            return False

    def _add_to_total_coverage(self, path):
        '''
        comp = copy.deepcopy(self._total_path)
        print(comp)
        '''
        for edge, hitcount in path.items() :
            self._total_path.add((edge, hitcount))
        '''
        diff = self._total_path - comp
        if diff is not None:
            print(diff)
            print("new path added: ",  len(self._total_path - comp))
        '''

    def is_interesting(self, path):
        orig_len = len(self._total_path)
        self._add_to_total_coverage(path)
        if orig_len < len(self._total_path):
            return True
        else:
            return False
    
    def update_favored(self, idx, buf, time, coverage):
        for edge in coverage :
            if self._favored.get(edge) is None:
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
        unmutated_favored_in_queue = self.is_there_unmutated_favored() 
        while True:
            self._seed_idx += 1
            if self._seed_idx >= len(self._inputs):
                self._seed_idx = 0

            if(self._refcount[self._seed_idx] == 0) :
                #if self.is_there_unmutated_favored():
                if unmutated_favored_in_queue:
                    if random.random() >= 0.01 :
                        continue
                elif self._mutated[self._seed_idx] is True:
                    if random.random() >= 0.05 :
                        continue
                else :
                    if random.random() >= 0.25 :
                        continue

            break
        return self._seed_idx

    def generate_input(self):
        if self._seed_run_finished:
            buf_idx = self.seed_selection()
            #buf_idx = self._mutation._rand(len(self._inputs))
            buf = self._inputs[buf_idx]
            self._mutated[buf_idx] = True
            return buf
        else:
            self._seed_idx += 1
            if(self._seed_idx >= len(self._inputs)):
                self._seed_idx = 0
            buf_idx = self._seed_idx
            buf = self._inputs[buf_idx]
            return buf

    def calculate_score(self, score):
        score = 1 << self._mutation._rand(6)
        return score
