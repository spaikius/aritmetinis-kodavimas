class FrequencyTable(object):
    def __init__(self, freqs):
        self.frequencies = list(freqs)
        self.total = sum(self.frequencies)

        self.bits_length = None
        self.cumulative = None

    def get_table_length(self):
        return len(self.frequencies)

    def get(self, symbol):
        return self.frequencies[symbol]

    def increment(self, symbol):
        self.total += 1
        self.frequencies[symbol] += 1
        self.cumulative = None
        self.bits_length = None

    def get_total(self):
        return self.total

    def get_low(self, symbol):
        if self.cumulative is None:
            self._init_cumulative()
        return self.cumulative[symbol]

    def get_high(self, symbol):
        if self.cumulative is None:
            self._init_cumulative()
        return self.cumulative[symbol + 1]

    def get_bits_length(self):
        if self.bits_length is None:
            self._init_bit_length()
        return self.bits_length


    def normalize_freq_table(self, maximum_total):
        scale_factor = float(maximum_total) / self.total / 2
        print("Scale factor: ",scale_factor)
        new_freqs = list()
        for freq in self.frequencies:
            new_freq = int(freq * scale_factor)
            if freq != 0 and new_freq == 0:
                new_freqs.append(1)
            else:
                new_freqs.append(new_freq)

        new_freqs[-1] = 1
        self.frequencies = new_freqs
        self.cumulative = None
        self.bits_length = None
        self.total = sum(self.frequencies)




    def _init_cumulative(self):
        cumul = [0]
        sum = 0
        for freq in self.frequencies:
            sum += freq
            cumul.append(sum)
        self.cumulative = cumul

    def _init_bit_length(self):
        biggest = max(self.frequencies)
        self.bits_length = len(bin(biggest)[2:])

    def __str__(self):
        result = ""
        for (i, freq) in enumerate(self.frequencies):
            if i != 256:
                result += "{}\t{}\t{}\n".format(chr(i), i, freq)
            elif i == 256:
                result += "{}\t{}\t{}\n".format("EOF", i, freq)
            else:
                raise ValueError("Symbol out of range")

        return result
