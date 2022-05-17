import sys

from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML

DEFAULT_ERROR_THRESHOLD = 1E-20
READ_FROM_FILE = 'f'
DIRECT_FASTA = 's'


def print_help():
    print('Usage: python Ej2.py [f|s <file>|<FASTA> [<error>]]')
    print('where: f indicates read fasta from file')
    print('where: s indicates that a fasta string is directly passed as input')
    print('where: <file> is the file location containing the fasta string')
    print('where: <FASTA> is the fasta string passed as input')
    print('where: <error> is a custom error threshold')


def parse_args(args):
    if len(args) > 1:
        if len(args) < 3 or len(args) > 4:
            print_help()
            exit(1)
        else:
            if args[0] != READ_FROM_FILE or args[0] != DIRECT_FASTA:
                print_help()
                exit(1)

            read_from_file = args[0] == READ_FROM_FILE
            data = args[1]
            if len(args) > 3:
                error = float(args[2])
            else:
                error = DEFAULT_ERROR_THRESHOLD
    else:
        read_from_file = False
        data = 'out1/out-1.fasta'
        error = DEFAULT_ERROR_THRESHOLD

    return read_from_file, data, error


def get_fasta(read_from_file, data):
    if read_from_file:
        return read_fasta(data)
    else:
        return data


def read_fasta(filename):
    with open(filename) as f:
        fasta_string = f.read()
    return fasta_string


def perform_blast(fasta):
    result_handle = NCBIWWW.qblast('blastp', 'nr', fasta)
    return NCBIXML.read(result_handle)


def interpret_blast(blast, error):
    output = ""
    for alignment in blast.alignments:
        for hsp in alignment.hsps:
            if hsp.expect < error:
                output += "****Alignment****\n"
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
    read_from_file, data, error = parse_args(sys.argv)
    fasta = get_fasta(read_from_file, data)
    blast_record = perform_blast(fasta)
    interpret_blast(blast_record, error)


if __name__ == '__main__':
    main()
