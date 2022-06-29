import sys

from Bio.SeqRecord import SeqRecord
from Bio import SeqIO


PROGRAM_NAME = sys.argv[0]
DEFAULT_ORF_LENGTH = 300
DEFAULT_OUTPUT_PREFIX = 'ORF_'
OUTPUT_FILE_SUFFIX = '.fasta'


def print_error(error, ex=None):
    print('Error ' + error + (': {}'.format(ex) if ex else ''))


def terminate(error, ex=None):
    print_error(error, ex)
    exit(1)


def print_help():
    print('Usage: python {} <genbank file> [-l <orf length>] [-o <output file>]'.format(PROGRAM_NAME))
    print('where: <genbank filename> is the file location of the file in interest in genbank format')
    print('       -l <orf length> is the min orf length to search for (integer)')
    print('       -o <output prefix> is the file prefix of the output file. Defaults to \'{}_<ORF#>{}\''.format(DEFAULT_OUTPUT_PREFIX, OUTPUT_FILE_SUFFIX))


def parse_args(args):
    if len(args) == 1:
        print_help()
        exit(1)

    input_file = args[1]
    output_prefix = DEFAULT_OUTPUT_PREFIX
    orf_len = DEFAULT_ORF_LENGTH

    try:
        for i in range(2, len(args) - 1, 2):
            if args[i] == '-l':
                orf_len = int(args[i + 1])
            elif args[i] == '-o':
                output_prefix = args[i + 1]
            else:
                print_help()
                exit(1)
    except Exception as e:
        terminate('parsing arguments', e)

    return input_file, orf_len, output_prefix


def save_orfs(orfs, output_prefix):
    error = False
    for i in range(1, len(orfs) + 1):
        try:
            save_sequence(orfs[i - 1], i, output_prefix)
        except Exception as e:
            error = True
            print_error('saving orf #{}'.format(i), e)
    if error:
        exit(1)


def save_sequence(seq, i, output_prefix):
    seq.id = 'e1'
    seq.description = 'ORF' + str(i)
    filename = '{}{}'.format(output_prefix, OUTPUT_FILE_SUFFIX)
    SeqIO.write(seq, filename, 'fasta')
    print('Stored file \'{}\''.format(filename))


def parse_genbank(filename):
    try:
        return SeqIO.read(filename, 'genbank')
    except Exception as e:
        terminate('reading input file', e)


def get_orfs(data, orf_len):
    results = []
    for _, nuc in [(1, data.seq), (-1, data.seq.reverse_complement())]:
        for frame in range(3):
            length = 3 * ((len(data) - frame) // 3)
            for protein in nuc[frame:frame + length].translate(1).split("*"):
                if len(protein) >= orf_len:
                    results.append(SeqRecord(protein))
    return results


def main():
    input_file, orf_len, output_prefix = parse_args(sys.argv)
    data = parse_genbank(input_file)
    print('Parsed input file, searching ORFs...')
    orfs = get_orfs(data, orf_len)
    print('Found {} proteins of min length {}, saving them...'.format(len(orfs), orf_len))
    save_orfs(orfs, output_prefix)

    print('All done.')


if __name__ == '__main__':
    main()
