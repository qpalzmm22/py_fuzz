# TODO : Refactor names isInteresting and updateFavored

import os
import sys
import time
import sys
import psutil
import hashlib
import logging
import functools
import copy
import multiprocessing as mp
from multiprocessing import Manager
mp.set_start_method('fork')

from pythonfuzz import corpus, dictionnary, tracer

logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))
logging.getLogger().setLevel(logging.DEBUG)

SAMPLING_WINDOW = 5 # IN SECONDS

try:
    lru_cache = functools.lru_cache
except:
    import functools32
    lru_cache = functools32.lru_cache


def worker(self, child_conn):
    # Silence the fuzzee's noise
    class DummyFile:
        """No-op to trash stdout away."""
        def write(self, x):
            pass
    logging.captureWarnings(True)
    logging.getLogger().setLevel(logging.ERROR)
    if self._close_fd_mask & 1:
        sys.stdout = DummyFile()
    if self._close_fd_mask & 2:
        sys.stderr = DummyFile()
    
    while True:
        buf = child_conn.recv_bytes()
        try:
            sys.settrace(tracer.trace)
            self._target(buf)
        except Exception as e:
            tracer.set_crash()
            
            if not self._inf_run:
                logging.exception(e)
                child_conn.send(None)
                break
            else:
                sys.settrace(None)
                if(tracer.get_crash() > self._crashes):
                    print("new crash ", self._crashes)
                    self._crashes += 1
                    logging.exception(e)
                    child_conn.send(None)
                else :
                    run_coverage = tracer.get_coverage()    
                    child_conn.send(run_coverage)

        else:
            sys.settrace(None)
            run_coverage = tracer.get_coverage()
            child_conn.send(run_coverage)

class Fuzzer(object):
    def __init__(self,
                 target,
                 dirs=None,
                 exact_artifact_path=None,
                 rss_limit_mb=2048,
                 timeout=120,
                 regression=False,
                 max_input_size=4096,
                 close_fd_mask=0,
                 runs=-1,
                 dict_path=None,
				 inf_run=False):
        self._target = target
        self._dirs = [] if dirs is None else dirs
        self._exact_artifact_path = exact_artifact_path
        self._rss_limit_mb = rss_limit_mb
        self._timeout = timeout
        self._regression = regression
        self._close_fd_mask = close_fd_mask
        self._corpus = corpus.Corpus(self._dirs, max_input_size, dict_path, timeout)
        self._total_executions = 0
        self._executions_in_sample = 0
        self._last_sample_time = time.time()
        self._total_coverage = 0
        self._p = None
        self.runs = runs
        self._inf_run = inf_run # added
        self._crashes = 0
        self._hangs = 0
        self._run_coverage = {}
        self._n_time = 0
        self._avg_time = 0
        self._tot_time = 0

    def log_stats(self, log_type):
        rss = (psutil.Process(self._p.pid).memory_info().rss + psutil.Process(os.getpid()).memory_info().rss) / 1024 / 1024

        endTime = time.time()
        execs_per_second = int(self._executions_in_sample / (endTime - self._last_sample_time))
        self._last_sample_time = time.time()
        self._executions_in_sample = 0
        ### ADDED
        n = self._n_time
        self._avg_time = n / (n + 1) * self._avg_time + execs_per_second / (n+1)
        self._n_time = n + 1
        
        #self._tot_time += execs_per_second
        #print(self._tot_time / (n + 1))
        logging.info('#{} {}     cov: {} corp: {} exec/s: {} rss: {} MB Unique Crash: {} total avg exec/s: {}'.format(
            self._total_executions, log_type, self._total_coverage, self._corpus.length, execs_per_second, rss, self._crashes, self._avg_time))
        '''
        print("---")
        print("idx : %d" % (self._corpus._seed_idx))
        print("favored : %d" %  len(self._corpus._favored))
        print("run path : %d" % len(self._run_coverage))
        print("total path : %d" % len(self._corpus._total_path))
        print("time : %d " % len(self._corpus._time))
        print("num(mutated) : %d" % len(self._corpus._mutated))
        print("num(inputs) : %d" % len(self._corpus._inputs))
        for i, inp in enumerate(self._corpus._inputs):
            print("inputs: ", inp, "hex: ", inp.hex() , " refcount", self._corpus._refcount[i])
        '''
        with open("log.csv", "a") as log_file:
            log_file.write("%d, %d\n" %(self._total_executions, self._total_coverage))
        return rss

    def write_sample(self, buf, prefix='crash-'):
        m = hashlib.sha256()
        m.update(buf)
        if self._exact_artifact_path:
            crash_path = self._exact_artifact_path
        else:
            dir_path = 'crashes'
            isExist = os.path.exists(dir_path)
            if not isExist:
              os.makedirs(dir_path)
              logging.info("The crashes directory is created")

            crash_path = dir_path + "/" + prefix + m.hexdigest()
        with open(crash_path, 'wb') as f:
            f.write(buf)
        logging.info('sample was written to {}'.format(crash_path))
        if len(buf) < 200:
            logging.info('sample = {}'.format(buf.hex()))

    def start(self):
        logging.info("[DEBUG] #0 READ units: {}".format(self._corpus.length))
        exit_code = 0
        parent_conn, child_conn = mp.Pipe()
        self._p = mp.Process(target=worker, args=(self, child_conn)) #added
        self._p.start()

        while True:
            if self.runs != -1 and self._total_executions >= self.runs:
                self._p.terminate()
                logging.info('did %d runs, stopping now.', self.runs)
                break
        
            start_time = time.time()
            buf = self._corpus.generate_input()

            parent_conn.send_bytes(buf)
            if not parent_conn.poll(self._timeout):
                logging.info("=================================================================")
                logging.info("timeout reached. testcase took: {}".format(self._timeout))
                self.write_sample(buf, prefix='timeout-')
                if self._inf_run:
                    self._hangs += 1
                else:
                    self._p.kill()
                    break

            self._run_coverage = parent_conn.recv()
            end_time = time.time()
            if self._run_coverage is None :
                self._crashes += 1
                self.write_sample(buf)
                if not self._inf_run: # added
                   exit_code = 76
                   break
                continue

            self._total_coverage = len(self._corpus._total_path)
            self._total_executions += 1
            self._executions_in_sample += 1
            rss = 0
            idx = self._corpus._seed_idx
            if self._corpus._seed_run_finished :
                if self._corpus.is_interesting(self._run_coverage):
                    idx = self._corpus.put(buf)
                    self._corpus.update_favored(idx, buf, end_time - start_time, self._run_coverage)
                    rss = self.log_stats("NEW")
                else:
                    if (time.time() - self._last_sample_time) > SAMPLING_WINDOW:
                        rss = self.log_stats('PULSE')
            else:
                # add to set
                for edge, hitcount in self._run_coverage.items() :
                    self._corpus._total_path.add((edge, hitcount))

                self._corpus.update_favored(idx, buf, end_time - start_time, self._run_coverage)
                if idx + 1 >= len(self._corpus._inputs) : 
                    self._corpus._seed_run_finished = True
                rss = self.log_stats("SEED")

            if rss > self._rss_limit_mb:
                logging.info('MEMORY OOM: exceeded {} MB. Killing worker'.format(self._rss_limit_mb))
                self.write_sample(buf)
                self._crashes += 1
                if not self._inf_run:
                    self._p.kill()
                    break

        self._p.join()
        sys.exit(exit_code)
