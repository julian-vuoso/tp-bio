import sys

from Bio import AlignIO


def print_help():
    print('Usage: python Ej3.py [<file>]')
    print('where: <file> is the input file containing all fasta sequences')


def parse_args(args):
    if len(args) > 2:
        print_help()
        exit(1)

    return args[1] if len(args) == 2 else 'in3/sequence.fasta'


def align(filename):
    with open(filename) as f:
        alignment = AlignIO.read(f, 'fasta')
    return alignment


def print_results(msa):
    max_len = 0
    for alignment in msa:
        max_len = max(max_len, len(alignment.id))

    seqs = []
    min_seq_len = 999
    for alignment in msa:
        min_seq_len = min(min_seq_len, len(alignment.seq))
        seqs.append(alignment.seq)
        print(alignment.id + ' ' * ((max_len - len(alignment.id)) + 1) + alignment.seq)


def main():
    filename = parse_args(sys.argv)
    alignment = align(filename)
    print_results(alignment)


if __name__ == '__main__':
    main()
