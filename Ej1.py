import math
import sys

from Bio.SeqRecord import SeqRecord
from Bio import SeqIO


def save_sequence(seq, i):
    seq.id = 'e1'
    seq.description = 'ORF' + str(i)
    SeqIO.write(seq, 'out1/out-' + str(i) + '.fasta', 'fasta')


def parse_genbank(filename):
    return SeqIO.read(filename, 'genbank')


def ej1(data, min_len=300):
    i = 1
    for _, nuc in [(1, data.seq), (-1, data.seq.reverse_complement())]:
        for frame in range(3):
            length = math.floor(3 * ((len(data) - frame) / 3))
            for protein in nuc[frame:frame + length].translate(1).split("*"):
                if len(protein) >= min_len:
                    save_sequence(SeqRecord(protein), i)
                    i += 1
    i -= 1
    print('Found ' + str(i) + ' proteins of length >= ' + str(min_len))


def main():
    if len(sys.argv) > 1:
        filename = sys.argv[0]
    else:
        filename = 'sequence.gb'

    data = parse_genbank(filename)
    ej1(data)


if __name__ == '__main__':
    main()
