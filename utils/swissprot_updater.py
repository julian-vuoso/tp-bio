import json
import subprocess
import sys

import requests
from datetime import datetime
import tarfile
from tqdm.auto import tqdm
import functools


SWISS_PROT_DB = 'https://ftp.ncbi.nlm.nih.gov/blast/db/FASTA/swissprot.gz'
SWISS_PROT_DB_METADATA = 'https://ftp.ncbi.nlm.nih.gov/blast/db/swissprot-prot-metadata.json'
LOCAL_DATABASE_ZIPPED = 'swissprot.gz'
LOCAL_DATABASE_ZIPPED_MEMBER = 'swissprot'
LOCAL_DATABASE = 'swissprot.db'
LOCAL_METADATA = 'swissprot.metadata.json'
METADATA_UPDATED_KEY = 'last-updated'

current_request = None
zipped_database_file = None


def close_request():
    global current_request
    if current_request is not None:
        current_request.close()
        current_request = None


def close_files():
    global zipped_database_file
    if zipped_database_file is not None:
        zipped_database_file.close()
        zipped_database_file = None


def terminate(error, ex=None):
    close_request()
    close_files()
    if error:
        print('Error ' + error + (': {}'.format(ex) if ex else ''))
        exit(1)
    exit(0)


def parse_date(date):
    return datetime.strptime(date, "%Y-%m-%dT%H:%M:%S")


def extract_date_from_metadata(metadata):
    try:
        return parse_date(json.loads(metadata)[METADATA_UPDATED_KEY])
    except Exception as e:
        terminate('parsing metadata, maybe it\'s not JSON formatted?', e)


def download_request():
    data = bytearray([])
    total_length = int(current_request.headers.get('content-length'), 0)
    desc = "(Unknown total file size)" if total_length == 0 else ""

    current_request.raw.read = functools.partial(current_request.raw.read, decode_content=True)  # Decompress if needed
    with tqdm.wrapattr(current_request.raw, "read", total=total_length, desc=desc) as r_raw:
        data.extend(r_raw.read())

    return data


def download_metadata():
    global current_request

    current_request = requests.get(SWISS_PROT_DB_METADATA, allow_redirects=True, stream=True)

    data = download_request().decode('utf8')

    close_request()
    return data


def current_metadata():
    try:
        with open(LOCAL_METADATA, 'r') as f:
            data = f.read()
    except:
        print('Couldn\'t read the local metadata, probably doesn\'t exist')
        return None

    return data


def save_metadata(data):
    try:
        with open(LOCAL_METADATA, 'w') as f:
            f.write(data)
    except Exception as e:
        terminate('couldn\'t save the downloaded metadata', e)


def save_database(data, metadata):
    try:
        with open(LOCAL_DATABASE_ZIPPED, 'wb') as f:
            f.write(data)
    except Exception as e:
        terminate('couldn\'t save the downloaded database', e)

    save_metadata(metadata)


def new_metadata():
    data = download_metadata()
    old_data = current_metadata()

    if old_data is None:
        return data

    date = extract_date_from_metadata(data)
    old_date = extract_date_from_metadata(old_data)

    if date > old_date:
        return data
    return None


def download_database():
    global current_request

    current_request = requests.get(SWISS_PROT_DB, allow_redirects=True, stream=True)
    data = download_request()
    close_request()
    return data


def unzip_database():
    global zipped_database_file

    zipped_database_file = tarfile.open(LOCAL_DATABASE_ZIPPED)
    zipped_database_file.extractfile(LOCAL_DATABASE_ZIPPED_MEMBER)


def build_database(makeblastdb):
    process = subprocess.Popen([makeblastdb, "-in swissprot -out swissprot -type prot"], stdout=subprocess.PIPE)
    print('Built with result: {}'.format(process.communicate()))


def main():
    if len(sys.argv) < 2:
        print('Expects the makeblastdb filepath as only argument')
        exit(1)

    print('Downloading database metadata...')
    metadata = new_metadata()
    if metadata is not None:
        print('New database version found, downloading...')
        database = download_database()
        print('New database downloaded, saving it...')
        save_database(database, metadata)
        print('Saved new database, unzipping...')
        unzip_database()
        print('Unzipped. Building database...')
        build_database(sys.argv[1])
        print('Database built')
    else:
        print('Database up to date.')

    print('All done.')


if __name__ == '__main__':
    main()
