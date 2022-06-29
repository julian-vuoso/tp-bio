import sys

from Bio import AlignIO
from Bio.Align.Applications import MuscleCommandline

PROGRAM_NAME = sys.argv[0]
DEFAULT_OUTPUT_FILE = 'msa.out'
DEFAULT_PRINT_RESULTS = True


def print_error(error, ex=None):
    print('Error ' + error + (': {}'.format(ex) if ex else ''))


def terminate(error, ex=None):
    print_error(error, ex)
    exit(1)


def print_help():
    print('Usage: python {} <file> [-q] [-o <output_file>] [-m <muscle_file>]'.format(PROGRAM_NAME))
    print('where: <file> is the file location containing the BLAST output in FASTA format')
    print('       q doesn\'t print MSA preliminary results to console, defaults to {}'.format(DEFAULT_PRINT_RESULTS))
    print('       o specifies an output file, default is \'{}\', in fasta format'.format(DEFAULT_OUTPUT_FILE))
    print('       m if specified, uses MUSCLE to perform MSA')


def parse_args(args):
    output_file = DEFAULT_OUTPUT_FILE
    should_print_results = DEFAULT_PRINT_RESULTS
    muscle_exe = None

    if len(args) == 1:
        print_help()
        exit(1)

    input_file = args[1]
    skip = 0
    try:
        for i in range(2, len(args) - 2):
            if skip > 0:
                skip -= 1
                continue

            if args[i] == '-q':
                should_print_results = False
            elif args[i] == '-o':
                skip = 1
                output_file = args[i + 1]
            elif args[i] == '-m':
                skip = 1
                muscle_exe = args[i + 1]
            else:
                print_help()
                exit(1)

    except Exception as e:
        terminate('parsing arguments', e)

    return input_file, should_print_results, output_file, muscle_exe


def align_biopython(filename):
    try:
        with open(filename) as f:
            alignments = list(AlignIO.parse(f, 'fasta'))
    except Exception as e:
        terminate('reading input file and performing MSA', e)

    return alignments


def align_muscle(filename, output_file, muscle_exe):
    try:
        muscle_cline = MuscleCommandline(muscle_exe,
                                         input=filename,
                                         out=output_file,
                                         diags=True,
                                         maxiters=1,
                                         )
        muscle_cline()
    except Exception as e:
        terminate('performing MSA with muscle', e)

    return None


def align(filename, output_file, muscle_exe):
    if muscle_exe is not None:
        return align_muscle(filename, output_file, muscle_exe)
    else:
        return align_biopython(filename)


def save_results(alignments, output_file):
    try:
        AlignIO.write(alignments, output_file, "fasta")
    except Exception as e:
        terminate('saving BLAST results', e)


def print_results(alignments):
    for alignment in alignments:
        print(alignment)


def main():
    input_file, should_print_results, output_file, muscle_exe = parse_args(sys.argv)
    print('Parsed arguments, performing local MSA{}...'.format(' and saving results' if muscle_exe is not None else ''))

    if muscle_exe is None:
        alignments = align(input_file, output_file, muscle_exe)
        print('Performed local MSA, {}saving alignments...'.format('printing and ' if should_print_results else ''))
        if should_print_results:
            print_results(alignments)
        save_results(alignments, output_file)

    print('Saved results to \'{}\''.format(output_file))

    print('All done.')


if __name__ == '__main__':
    main()
