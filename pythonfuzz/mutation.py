import hashlib
import math
import os
import random
import struct
from zipfile import ZIP_BZIP2

from numpy import TooHardError

from . import dictionnary

try:
    from random import _randbelow
except ImportError:
    from random import _inst
    _randbelow = _inst._randbelow

INTERESTING8 = [-128, -1, 0, 1, 16, 32, 64, 100, 127]
INTERESTING16 = [0, 128, 255, 256, 512, 1000, 1024, 4096, 32767, 65535]
INTERESTING32 = [0, 1, 32768, 65535, 65536, 100663045, 2147483647, 4294967295]


class Mutation(object):
    def __init__(self, max_input_size=4096, dict_path=None):
        self._dict = dictionnary.Dictionary(dict_path)
        self._max_input_size = max_input_size
        self._deter_nm = 10
        self._havoc_nm = 7

    @staticmethod
    def _rand(n):
        if n < 2:
            return 0
        return _randbelow(n)

    # Exp2 generates n with probability 1/2^(n+1).
    @staticmethod
    def _rand_exp():
        rand_bin = bin(random.randint(0, 2**32-1))[2:]
        rand_bin = '0'*(32 - len(rand_bin)) + rand_bin
        count = 0
        for i in rand_bin:
            if i == '0':
                count +=1
            else:
                break
        return count

    @staticmethod
    def _choose_len(n):
        x = Mutation._rand(100)
        if x < 90:
            return Mutation._rand(min(8, n)) + 1
        elif x < 99:
            return Mutation._rand(min(32, n)) + 1
        else:
            return Mutation._rand(n) + 1

    @staticmethod
    def copy(src, dst, start_source, start_dst, end_source=None, end_dst=None):
        end_source = len(src) if end_source is None else end_source
        end_dst = len(dst) if end_dst is None else end_dst
        byte_to_copy = min(end_source-start_source, end_dst-start_dst)
        #src[start_source:start_source+byte_to_copy] = dst[start_dst:start_dst+byte_to_copy]
        dst[start_dst:start_dst+byte_to_copy] = src[start_source:start_source+byte_to_copy]


    def mutate_det(self, buf, idx, x):
        res = buf[:]
        if x == 0:
            # Add/subtract from a byte.
            if len(res) == 0 or len(res) <= idx:
                return res
            #pos = self._rand(len(res))
            pos = idx
            v = self._rand(2 ** 8)
            res[pos] = (res[pos] + v) % 256
        elif x == 1:
            # Add/subtract from a uint16.
            if len(res) < 2 or len(res) - 1 <= idx:
                return res
            #pos = self._rand(len(res) - 1)
            pos = idx
            v = self._rand(2 ** 16)
            if bool(random.getrandbits(1)):
                v = struct.pack('>H', v)
            else:
                v = struct.pack('<H', v)
            res[pos] = (res[pos] + v[0]) % 256
            res[pos + 1] = (res[pos] + v[1]) % 256
        elif x == 2:
            # Add/subtract from a uint32.
            if len(res) < 4 or len(res) - 3 <= idx:
                return res
            #pos = self._rand(len(res) - 3)
            pos = idx
            v = self._rand(2 ** 32)
            if bool(random.getrandbits(1)):
                v = struct.pack('>I', v)
            else:
                v = struct.pack('<I', v)
            res[pos] = (res[pos] + v[0]) % 256
            res[pos + 1] = (res[pos + 1] + v[1]) % 256
            res[pos + 2] = (res[pos + 2] + v[2]) % 256
            res[pos + 3] = (res[pos + 3] + v[3]) % 256
        elif x == 3:
            # Add/subtract from a uint64.
            if len(res) < 8 or len(res) - 7 <= idx:
                return res
            #pos = self._rand(len(res) - 7)
            pos = idx
            v = self._rand(2 ** 64)
            if bool(random.getrandbits(1)):
                v = struct.pack('>Q', v)
            else:
                v = struct.pack('<Q', v)
            res[pos] = (res[pos] + v[0]) % 256
            res[pos + 1] = (res[pos + 1] + v[1]) % 256
            res[pos + 2] = (res[pos + 2] + v[2]) % 256
            res[pos + 3] = (res[pos + 3] + v[3]) % 256
            res[pos + 4] = (res[pos + 4] + v[4]) % 256
            res[pos + 5] = (res[pos + 5] + v[5]) % 256
            res[pos + 6] = (res[pos + 6] + v[6]) % 256
            res[pos + 7] = (res[pos + 7] + v[7]) % 256
        elif x == 4:
            # Replace a byte with an interesting value.
            if len(res) == 0 or len(res) <= idx :
                return res
            #pos = self._rand(len(res))
            pos = idx
            res[pos] = INTERESTING8[self._rand(len(INTERESTING8))] % 256
        elif x == 5:
            # Replace an uint16 with an interesting value.
            if len(res) < 2 or len(res) - 1 <= idx:
                return res
            #pos = self._rand(len(res) - 1)
            pos = idx
            v = random.choice(INTERESTING16)
            if bool(random.getrandbits(1)):
                v = struct.pack('>H', v)
            else:
                v = struct.pack('<H', v)
            res[pos] = v[0] % 256
            res[pos + 1] = v[1] % 256
        elif x == 6:
            # Replace an uint32 with an interesting value.
            if len(res) < 4 or len(res) - 3 <= idx:
                return res
            #pos = self._rand(len(res) - 3)
            pos = idx
            v = random.choice(INTERESTING32)
            if bool(random.getrandbits(1)):
                v = struct.pack('>I', v)
            else:
                v = struct.pack('<I', v)
            res[pos] = v[0] % 256
            res[pos + 1] = v[1] % 256
            res[pos + 2] = v[2] % 256
            res[pos + 3] = v[3] % 256
        elif x == 7:
            # Replace an ascii digit with another digit.
            if len(res) <= idx:
                return res
            pos = idx
            if ord('0') <= res[pos] <= ord('9'):
                was = res[pos]
                now = was
                while was == now:
                    now = self._rand(10) + ord('0')
                res[pos] = now
        elif x == 8:
            # Insert Dictionary word
            dict_word = self._dict.get_word()
            if dict_word is None:
                return res
            #pos = self._rand(len(res) + 1)
            pos = idx
            n = len(dict_word)
            for k in range(n):
                res.append(0)
            self.copy(res, res, pos, pos+n)
            for k in range(n):
                res[pos+k] = dict_word[k]
        elif x == 9:
            # Replace with Dictionary word
            dict_word = self._dict.get_word()
            if(dict_word == None or len(res) < len(dict_word) or len(res) - len(dict_word) <= idx):
                return res
            #pos = self._rand(len(res) - len(dict_word))
            pos = idx
            self.copy(dict_word, res, 0, pos)
        
        if len(res) > self._max_input_size:
            res = res[:self._max_input_size]
        return res

    def mutate_havoc(self, buf):
        res = buf[:]
        
        if self._dict is None:
            x = self._rand(self._havoc_nm-2)
        else:
            x = self._rand(self._havoc_nm)

        if x == 0:
            # Remove a range of bytes.
            if len(res) <= 1 :
                return res
            #pos0 = idx
            pos0 = self._rand(len(res))
            pos1 = pos0 + self._choose_len(len(res) - pos0)
            self.copy(res, res, pos1, pos0)
            res = res[:len(res) - (pos1-pos0)]
        elif x == 1:
            # Insert a range of random bytes.
            pos = self._rand(len(res) + 1)
            #pos = idx
            n = self._choose_len(10)
            for k in range(n):
                res.append(0)
            self.copy(res, res, pos, pos+n)
            for k in range(n):
                res[pos+k] = self._rand(256)
        elif x == 2:
            # Duplicate a range of bytes.
            if len(res) <= 1 :
                return res
            src = self._rand(len(res))
            #src = idx
            dst = self._rand(len(res))
            while src == dst:
                dst = self._rand(len(res))
            n = self._choose_len(len(res) - src)
            tmp = bytearray(n)
            self.copy(res, tmp, src, 0)
            for k in range(n):
                res.append(0)
            self.copy(res, res, dst, dst+n)
            for k in range(n):
                res[dst+k] = tmp[k]
        elif x == 3:
            # Copy a range of bytes.
            if len(res) <= 1 :
                return res
            src = self._rand(len(res))
            #src = idx
            dst = self._rand(len(res))
            while src == dst:
                dst = self._rand(len(res))
            n = self._choose_len(len(res) - src)
            self.copy(res, res, src, dst, src+n)
        elif x == 4:
            # Bit flip. Spooky!
            if len(res) == 0 :
                return res
            pos = self._rand(len(res))
            #pos = idx
            res[pos] ^= 1 << self._rand(8)
        elif x == 5:
            # Set a byte to a random value.
            if len(res) == 0 :
                return res
            pos = self._rand(len(res))
            #pos = idx
            res[pos] ^= self._rand(255) + 1
        elif x == 6:
            # Swap 2 bytes.
            if len(res) <= 1 :
                return res
            src = self._rand(len(res))
            #src = idx
            dst = self._rand(len(res))
            while src == dst:
                dst = self._rand(len(res))
            res[src], res[dst] = res[dst], res[src]
        
        if len(res) > self._max_input_size:
            res = res[:self._max_input_size]
        return res
