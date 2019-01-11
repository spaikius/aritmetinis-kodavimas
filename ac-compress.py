#  Aritmetinis kodavimas
#  Rimvydas Noreika, Rolandas Porejus

import sys
import os

if os.name == 'nt': # windows
    sys.path.append(os.path.dirname(__file__))

import contextlib
import arithmeticcoding
import bitIO
import freqtable

# --Main--
def main(args):
    # Argumentu apdorojimas
    if len(args) != 3:
        sys.exit("Usage: python ac-compress.py InputFile OutputFile BitsNum")

    input_file, output_file, bits_len = args[0], args[1], int(args[2])

    if bits_len < 1 or bits_len > 124:
	print bits_len, bits_len < 1, bits_len > 124
	sys.exit("Neleistina numBits reiksme, galimos reiksmes: [1 .. 124]")
        
    # Failo skaitymas ir dazniu lenteles sudarymas
    freqs = get_frequencies(input_file)

    enc = arithmeticcoding.ArithmeticEncoder(bits_len)

    max_total =  enc.maximum_total
    freq_total = freqs.get_total()

    if freq_total > max_total:
        print("Kumuliatyvus dazniu lenteles dydis yra perdidelis nuruodytam kodavimo intervalui.")
        print("Pradedama dazniu lenteles normalizacija.")
        freqs.normalize_freq_table(max_total)
        # sys.exit()
        
    # Failas skaitomas antra karta, pritaikomas aritmetiko kodavimas suspaudymas ir sukuriamas isvesties failas
    with open(input_file, "rb") as inp, \
            contextlib.closing(bitIO.BitOutputStream(open(output_file, "wb"))) as outp:
        write_header(outp, bits_len, freqs.get_bits_length())
        write_frequencies(outp, freqs, freqs.get_bits_length()) # rasoma dazniu lentele
        enc.set_bitout(outp)
        compress(freqs, inp, enc) # suspaudzia duomenys


# Pateiktam failui sukuria dazniu lentele
def get_frequencies(filepath):
    freqs = freqtable.FrequencyTable([0] * 257)
    with open(filepath, "rb") as input:
        while True:
            b = input.read(1)
            if len(b) == 0: # Pasiektas EOF
                freqs.increment(256)  # EOF symbolis gauna dazni lygu 1. (EOF nera skaitomas, todel reikia paciam pridet)
                break

            freqs.increment(ord(b))

    return freqs


def write_header(outp, bits_len, freq_bites_len):

    # pirmi 5 bitai apraso kas kiek bitu skaityt dazniu lentele
    # Max 32bitai
    for bit in reversed(range(5)):
        outp.write((freq_bites_len >> bit) & 1)

    # kiti 7 bitai apraso bits_nums
    for bit in reversed(range(7)):
        outp.write((int(bits_len) >> bit) & 1)


def write_frequencies(outp, freqs, freq_bites_len):
    for i in range(256):
        for bit in reversed(range(freq_bites_len)):
            outp.write((freqs.get(i) >> bit) & 1)


def compress(freqs, inp, enc):
    while True:
        symbol = inp.read(1)
        if len(symbol) == 0:
            break
        enc.write(freqs, ord(symbol))
    
    enc.write(freqs, 256)  # EOF
    enc.finish()


if __name__ == "__main__":
    main(sys.argv[1:])
