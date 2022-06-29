import sys

from Bio.Blast import NCBIWWW
from Bio.Blast import NCBIXML


BLAST_OUTPUT_TEMPLATE = '''****Alignment****
sequence: {}
accession: {}
length: {:d}
score: {}
identity: {:d}/{:d}({:.2f}%)
E-value: {:f}
query: {}
match: {}
sbjct: {}'''


PROGRAM_NAME = sys.argv[0]
DEFAULT_ERROR_THRESHOLD = 1E-20
DEFAULT_OUTPUT_FILE = 'blast.out'


def print_error(error, ex=None):
    print('Error ' + error + (': {}'.format(ex) if ex else ''))


def terminate(error, ex=None):
    print_error(error, ex)
    exit(1)


def print_help():
    print('Usage: python {} <file> [-e <error>] [-r <previous_result>] [-o <output_file>]'.format(PROGRAM_NAME))
    print('where: <file> is the file location containing the fasta string')
    print('       <FASTA> is the fasta string passed as input')
    print('       <error> is a custom error threshold, default is {:e}'.format(DEFAULT_ERROR_THRESHOLD))
    print('       r specifies a previous BLAST XML result (file) to interpret. Otherwise, it will use the API to perform a BLAST against NCBI')
    print('       o specifies an output file, default is \'{}\''.format(DEFAULT_OUTPUT_FILE))


def parse_args(args):
    output_file = DEFAULT_OUTPUT_FILE
    error = DEFAULT_ERROR_THRESHOLD
    blast_result = None

    if len(args) == 1:
        print_help()
        exit(1)

    fasta = args[1]
    try:
        for i in range(2, len(args) - 2, 2):
            if args[i] == '-f':
                fasta = args[i + 1]
            elif args[i] == '-e':
                error = float(args[i + 1])
            elif args[i] == '-r':
                blast_result = args[i + 1]
            elif args[i] == '-o':
                output_file = args[i + 1]
            else:
                print_help()
                exit(1)
    except Exception as e:
        terminate('parsing arguments', e)

    return fasta, error, blast_result, output_file


def get_fasta(data):
    try:
        return read_fasta(data)
    except Exception as e:
        terminate('reading FASTA file', e)


def read_fasta(filename):
    with open(filename) as f:
        fasta_string = f.read()
    return fasta_string


def perform_blast(fasta, blast_in_file):
    try:
        if blast_in_file is None:
            print('Performing an online BLAST...')
            return NCBIXML.read(NCBIWWW.qblast('blastp', 'nr', fasta))
        else:
            print('Reading BLAST from input file...')
            with open(blast_in_file, 'r') as f:
                data = NCBIXML.read(f)
    except Exception as e:
        terminate('performing BLAST', e)

    return data


def format_blast_result(alignment, hsp):
    return BLAST_OUTPUT_TEMPLATE.format(
        alignment.hit_def.split(' >')[0],
        alignment.hit_id.split('|')[1],
        alignment.length,
        str(hsp.score),
        hsp.identities, hsp.align_length, (100 * hsp.identities / hsp.align_length),
        hsp.expect,
        hsp.query,
        hsp.match,
        hsp.sbjct
    )


def get_blast_results(blast, error):
    results = []
    for alignment in blast.alignments:
        for hsp in alignment.hsps:
            if hsp.expect < error:
                results.append(format_blast_result(alignment, hsp))
    return results


def save_results(results, output_file):
    try:
        with open(output_file, 'w') as f:
            f.write('\n\n'.join(results))
    except Exception as e:
        terminate('saving BLAST results', e)


def main():
    filename, error, blast_in_file, output_file = parse_args(sys.argv)
    print('Parsed arguments, getting FASTA string...')
    fasta = get_fasta(filename)
    print('Got FASTA, performing BLAST...')
    blast_record = perform_blast(fasta, blast_in_file)
    print('Performed BLAST, interpreting BLAST...')
    results = get_blast_results(blast_record, error)
    print('Interpreted BLAST, found {} results, saving them...'.format(len(results)))
    save_results(results, output_file)
    print('Saved results to {}'.format(output_file))

    print('All done.')


if __name__ == '__main__':
    main()
