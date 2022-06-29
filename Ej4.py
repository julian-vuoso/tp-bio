import sys


PROGRAM_NAME = sys.argv[0]
DEFAULT_OUTPUT_FILE = 'blast_hits.out'
DEFAULT_INPUT_FILE = 'blast.out'


def print_error(error, ex=None):
    print('Error ' + error + (': {}'.format(ex) if ex else ''))


def terminate(error, ex=None):
    print_error(error, ex)
    exit(1)


def print_help():
    print('Usage: python {} <pattern> [-f <file>] [-o <output_file>]'.format(PROGRAM_NAME))
    print('where: pattern is the pattern to filter the BLAST hits')
    print('       f is the file location containing the BLAST output in FASTA format, defaults to \'{}\''.format(DEFAULT_INPUT_FILE))
    print('       o specifies an output file, default is \'{}\''.format(DEFAULT_OUTPUT_FILE))


def parse_args(args):
    input_file = DEFAULT_INPUT_FILE
    output_file = DEFAULT_OUTPUT_FILE

    if len(args) == 1:
        print_help()
        exit(1)

    pattern = args[1]
    try:
        for i in range(2, len(args), 2):
            if args[i] == '-o':
                output_file = args[i + 1]
            elif args[i] == '-f':
                input_file = args[i + 1]
            else:
                print_help()
                exit(1)

    except Exception as e:
        terminate('parsing arguments', e)

    return pattern, input_file, output_file


def split_blast_input(separator, data):
    return [(separator + e).strip() for e in data.split(separator) if e]


def read_blast(input_file):
    try:
        with open(input_file, 'r') as f:
            data = f.read()

        return split_blast_input('****Alignment****', data)
    except Exception as e:
        terminate('reading BLAST input', e)


def save_results(results, output_file):
    try:
        with open(output_file, 'w') as f:
            f.write('\n\n'.join(results))
    except Exception as e:
        terminate('saving BLAST results', e)


def search_hits(pattern, blast_results):
    hits = []

    pattern = pattern.upper()
    for blast in blast_results:
        try:
            lines = blast.split('\n')

            # sequence: Q02242.1 RecName: Full=Programmed cell death protein 1; Short=Protein PD-1; Short=mPD-1; AltName: CD_antigen=CD279; Flags: Precursor [Mus musculus]
            sequence = lines[1]
            org = sequence[sequence.rindex('[') + 1:sequence.rindex(']')]
            if pattern in org.upper():
                hits.append(blast)
        except Exception as e:
            terminate('searching hits, probably input wrongly formatted', e)

    return hits


def main():
    pattern, input_file, output_file = parse_args(sys.argv)
    print('Parsed arguments, reading input file...')
    blast_results = read_blast(input_file)
    print('Input file read, searching for hits...')
    hits = search_hits(pattern, blast_results)
    print('Found {} hits, saving results...'.format(len(hits)))
    save_results(hits, output_file)
    print('Saved results to \'{}\''.format(output_file))

    print('All done.')


if __name__ == '__main__':
    main()
