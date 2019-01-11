#  Aritmetinis kodavimas
#  Rimvydas Noreika, Rolandas Porejus

import sys
import os

if os.name == 'nt': # windows
    sys.path.append(os.path.dirname(__file__))

import arithmeticcoding
import bitIO
import freqtable


# -- Main --
def main(args):
    # Argumentu apdorojimas
    if len(args) != 2:
        sys.exit("Usage: python ac-decompress.py InputFile OutputFile")
    inputfile, outputfile = args

    # skaitymas
    with open(outputfile, "wb") as out, open(inputfile, "rb") as inp:
        bitin = bitIO.BitInputStream(inp)
        freqs_table_bit_len, bits_len = read_header(bitin)
        freqs = read_frequencies(bitin, freqs_table_bit_len)
        decompress(freqs, bits_len, bitin, out)


def read_header(bitin):
    freq_table_bit_range = 0
    for _ in range(5):
        freq_table_bit_range = (freq_table_bit_range << 1) | bitin.read_no_eof()

    bits_len = 0
    for _ in range(7):
        bits_len = (bits_len << 1) | bitin.read_no_eof()

    return freq_table_bit_range, bits_len


def read_frequencies(bitin, bit_len):
    def read_int(n):
        result = 0
        for _ in range(n):
            result = (result << 1) | bitin.read_no_eof()
        return result

    freqs = [read_int(bit_len) for _ in range(256)]
    freqs.append(1)

    return freqtable.FrequencyTable(freqs)


def decompress(freqs, bits_len, bitin, out):
    dec = arithmeticcoding.ArithmeticDecoder(bits_len, bitin)
    try:
        while True:
            symbol = dec.read(freqs)
            if symbol == 256:  # EOF
                break
            # out.write(bytes((symbol,)))
            out.write(chr(symbol))
    except ValueError as err:
        print(err)

if __name__ == "__main__":
    main(sys.argv[1 : ])
