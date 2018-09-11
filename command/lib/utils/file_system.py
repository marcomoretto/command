import errno
import gzip
import os
import shutil
import string
import tarfile
import time
from zipfile import ZipFile


def path_hierarchy(path, base_path=None, name_filter=''):
    hierarchy = {
        'leaf': False,
        'text': os.path.basename(path),
        'path': path if not base_path else path.replace(base_path, '')
    }
    try:
        hierarchy['children'] = [
            path_hierarchy(os.path.join(path, contents), base_path, name_filter)
            for contents in [e for e in os.listdir(path) if not e.startswith('__')
                             and (not os.path.isfile(os.path.join(path, e)) or name_filter in e)]
        ]
    except OSError as e:
        if e.errno != errno.ENOTDIR:
            raise
        hierarchy['leaf'] = True
        hierarchy['iconCls'] = 'python'

    return hierarchy


def uncompress_file(filename, out_dir):
    output_uncompressed, file_extension = os.path.splitext(filename)
    if file_extension == '.zip':
        extract_zipfile(filename, out_dir)
        os.remove(filename)
    elif file_extension == '.gz':
        extract_gzfile(filename, output_uncompressed)
        output_uncompressed_tar, file_extension = os.path.splitext(output_uncompressed)
        if file_extension == '.tar':
            extract_tarfile(output_uncompressed, out_dir)
            os.remove(output_uncompressed)
        os.remove(filename)

def extract_zipfile(zip_filename, out_dir):
    extracted_files = []
    ENC = 'cp437'
    zf = ZipFile(zip_filename, 'r')
    for info in zf.infolist():
        fn, dtz = info.filename, info.date_time # , info.file_size
        # some zips have dirs listed as files. Catch and bypass those.
        name = os.path.basename(fn)
        if not name:
            continue
        # get our filename converted from bytes to unicode
        bn_uni = os.path.basename(fn)
        # this method is about 15% faster than extractall, and preserves modify and access dates
        c = zf.open(fn)
        outfile = os.path.join(out_dir, bn_uni)
        # try/except to avoid problems with locked files, etc do in chunks to avoid memory problems
        chunk = 2**16
        try:
            with open(outfile, 'wb') as f:
                s = c.read(chunk)
                f.write(s)
                while not len(s) < chunk:
                    s = c.read(chunk)
                    f.write(s)
            c.close()
            # set modify and access dates to that inside the zip
            dtout = time.mktime(dtz + (0, 0, -1))
            os.utime(outfile, (dtout, dtout))
            extracted_files.append(outfile)
        except IOError:
            c.close()
            return False
    return extracted_files


def is_file_compressed(file):
    compressed_dict = {
        "\x1f\x8b\x08": "gz",
        "\x50\x4b\x03\x04": "zip"
    }
    max_len = max(len(x) for x in compressed_dict)

    file_start = file.read(max_len)
    file.seek(0)
    for compressed, filetype in compressed_dict.items():
        if file_start.startswith(compressed):
            return filetype
    return 'plain text'


def is_text(filename):
    s = open(filename).read(512)
    text_characters = "".join(map(chr, range(32, 127)) + list("\n\r\t\b"))
    _null_trans = string.maketrans("", "")
    if not s:
        # Empty files are considered text
        return True
    if "\0" in s:
        # Files with null bytes are likely binary
        return False
    # Get the non-text characters (maps a character to itself then
    # use the 'remove' option to get rid of the text characters.)
    t = s.translate(_null_trans, text_characters)
    # If more than 30% non-text characters, then
    # this is considered a binary file
    if len(t)/len(s) > 0.30:
        return False
    return True


def compress_gz(filename, out_filename):
    with open(filename, 'rb') as f_in:
        with gzip.open(out_filename, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)


def extract_gzfile(gz_filename, outfile):
    zip_file = gzip.open(gz_filename, "rb")
    uncompressed_file = open(outfile, "wb")
    decoded = zip_file.read()
    uncompressed_file.write(decoded)
    zip_file.close()
    uncompressed_file.close()


def extract_tarfile(tar_filename, out_dir):
    tar = tarfile.open(tar_filename)
    tar.extractall(path=out_dir)
    tar.close()
