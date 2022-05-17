import sys

from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML

DEFAULT_ERROR_THRESHOLD = 1E-20
READ_FROM_FILE = 'f'
DIRECT_FASTA = 's'


def print_help():
    print('Usage: python Ej2.py [-f|-s <file>|<FASTA>] [-e <error>] [-r <previous_result>]')
    print('where: f indicates read fasta from file')
    print('       s indicates that a fasta string is directly passed as input')
    print('       <file> is the file location containing the fasta string')
    print('       <FASTA> is the fasta string passed as input')
    print('       <error> is a custom error threshold')
    print('       r specifies a previous BLAST result to interpret. Otherwise, it will use the API to perform a BLAST against NCBI')
    print(sys.argv)


def parse_args(args):
    read_from_file = True
    data = 'out1/out-1.fasta'
    error = DEFAULT_ERROR_THRESHOLD
    blast_result = None

    if len(args) % 2 == 0:
        print_help()
        exit(1)

    found_args = (len(args) - 1) / 2
    for i in range(1, len(args) - 1, 2):
        if args[i] == '-f':
            read_from_file = True
            data = args[i + 1]
            found_args -= 1
        elif args[i] == '-s':
            read_from_file = False
            data = args[i + 1]
            found_args -= 1
        elif args[i] == '-e':
            error = float(args[i + 1])
            found_args -= 1
        elif args[i] == '-r':
            blast_result = args[i + 1]
            found_args -= 1

    if found_args != 0:
        print_help()
        exit(1)

    return read_from_file, data, error, blast_result


def get_fasta(read_from_file, data):
    if read_from_file:
        return read_fasta(data)
    else:
        return data


def read_fasta(filename):
    with open(filename) as f:
        fasta_string = f.read()
    return fasta_string


def perform_blast(fasta, blast_in_file):
    if blast_in_file is None:
        return NCBIXML.read(NCBIWWW.qblast('blastp', 'nr', fasta))
    else:
        with open(blast_in_file) as f:
            data = NCBIXML.read(f)
    return data


def interpret_blast(blast, error):
    output = ""
    for alignment in blast.alignments:
        for hsp in alignment.hsps:
            if hsp.expect < error:
                output += "*Result*\n"
                output += "sequence: %s\n" % alignment.hit_def.split(' >')[0]
                output += "accession: %s\n" % alignment.hit_id.split('|')[1]
                output += "length: %d\n" % alignment.length
                output += "score: %s\n" % str(hsp.score)
                output += "identity: %d/%d(%.2f%%)\n" % (hsp.identities, hsp.align_length, (100 * hsp.identities / hsp.align_length))
                output += "E-value: %f\n" % hsp.expect
                output += "query: %s\n" % hsp.query
                output += "match: %s\n" % hsp.match
                output += "sbjct: %s\n\n" % hsp.sbjct

    f = open('out2/blast.out', 'w')
    f.write(output)
    f.close()


def main():
    read_from_file, data, error, blast_in_file = parse_args(sys.argv)
    fasta = get_fasta(read_from_file, data)
    blast_record = perform_blast(fasta, blast_in_file)
    interpret_blast(blast_record, error)


if __name__ == '__main__':
    main()
