#  Aritmetinis kodavimas
#  Rimvydas Noreika, Rolandas Porejus
import sys

class ArithmeticCoder(object):
    def __init__(self, bits_num):
	
	self.num_state_bits = int(bits_num)
        self.full_range = 1 << self.num_state_bits
        self.half_range = self.full_range >> 1  # 02^(n-1) : 01000..000
        self.quarter_range = self.half_range >> 1 # 00100..00
        self.maximum_total = self.quarter_range + 2
        self.state_mask = self.full_range - 1 # 01111..11

        self.low = 0
        self.high = self.state_mask

    def update(self, freqs, symbol):
        low = self.low
        high = self.high
        range = high - low + 1

        total = freqs.get_total()
        symlow = freqs.get_low(symbol)
        symhigh = freqs.get_high(symbol)

        if total > self.maximum_total:
            raise ValueError("Negaliu uzkoduoti simbolio, nes bendras simboliu skaicius yra per didelis nuruodytam intervalui")

        newlow  = low + symlow  * range // total
        newhigh = low + symhigh * range // total - 1
        self.low = newlow
        self.high = newhigh

        while ((self.low ^ self.high) & self.half_range) == 0: # tikrinam ar low ir high vyriausi bitai yra vienodi
            self.shift()
            self.low  = ((self.low  << 1) & self.state_mask)
            self.high = ((self.high << 1) & self.state_mask) | 1
        while (self.low & ~self.high & self.quarter_range) != 0:
            self.underflow()
            self.low = (self.low << 1) ^ self.half_range
            self.high = ((self.high ^ self.half_range) << 1) | self.half_range | 1
        
class ArithmeticEncoder(ArithmeticCoder):
    def __init__(self, bits_num, bitout=None):
        super(ArithmeticEncoder, self).__init__(bits_num)
        self.output = bitout
        self.num_underflow = 0

    # Uzkoduoja simboli
    def write(self, freqs, symbol):
        self.update(freqs, symbol)

    def finish(self):
        self.output.write(1)

    def shift(self):
        bit = self.low >> (self.num_state_bits - 1)
        self.output.write(bit)

        for _ in range(self.num_underflow):
            self.output.write(bit ^ 1)
        self.num_underflow = 0

    def underflow(self):
        self.num_underflow += 1

    def set_bitout(self, bitout):
        self.output = bitout

class ArithmeticDecoder(ArithmeticCoder):
    def __init__(self, bits_num, bitin):
        super(ArithmeticDecoder, self).__init__(bits_num)
        self.input = bitin
        self.code = 0
        for _ in range(self.num_state_bits):
            self.code = self.code << 1 | self.read_code_bit()

    def read(self, freqs):
        total = freqs.get_total()
        range = self.high - self.low + 1
        offset = self.code - self.low
        value = ((offset + 1) * total - 1) // range

        # simbolis toks kad freqs.get_low(symbol) <= value
        start = 0
        end = freqs.get_table_length()

        while end - start > 1:
            middle = (start + end) >> 1
            if freqs.get_low(middle) > value:
                end = middle
            else:
                start = middle

        symbol = start
        self.update(freqs, symbol)

        return symbol

    def shift(self):
        self.code = ((self.code << 1) & self.state_mask) | self.read_code_bit()

    def underflow(self):
        self.code = (self.code & self.half_range) | ((self.code << 1) & (self.state_mask >> 1)) | self.read_code_bit()

    def read_code_bit(self):
        bit = self.input.read()
        if bit == -1:
            bit = 0
        return bit
