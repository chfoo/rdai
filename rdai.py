'''Recursive deep archive iterator'''
# Copyright 2013 by Christopher Foo <chris.foo@gmail.com>
# Licensed under GNU GPL v3.
import os.path
import bz2
import gzip
import lzma
import zipfile
import tarfile
import argparse
import logging
import json


__version__ = '1.0'

_logger = logging.getLogger(__name__)


STREAM_FILE_EXTENSIONS = ('gzip', 'bz2', 'xz',)
MULTI_FILE_ARCHIVE_EXTENSIONS = ('tar', 'zip',)


STREAM_EXTENSION_MAP = {
    'bz2': bz2.open,
    'gz': gzip.open,
    'xz': lzma.open,
}


def get_extension(filename):
    '''Returns the file extension for given filename.'''
    ext = os.path.splitext(filename)[1].lstrip('.')
    _logger.debug('Ext: {}'.format(ext))
    return ext


def read_archive(file_obj, filename):
    '''Reads a multi file archive.'''
    _logger.info('Archive: {}'.format(filename))
    extension = get_extension(filename)

    if extension == 'zip':
        _logger.debug('Opening as zip')
        archive = zipfile.ZipFile(file_obj)

        for info in archive.infolist():
            file_obj = archive.open(info.filename)
            yield from read_file(file_obj, info.filename)
    else:
        _logger.debug('Opening as tar')
        archive = tarfile.TarFile(file_obj)

        while True:
            info = archive.next()

            if not info:
                break

            if info.isfile():
                yield from read_file(archive.extractfile(info), info.name)


def read_stream(file_obj, filename):
    '''Read a compressed file.'''
    _logger.info('Stream: {}'.format(filename))
    stream_extension = get_extension(filename)
    content_extension = get_extension(stream_extension)

    _logger.debug('Stream content extension: {}'.format(content_extension))

    yield from read_file(file_obj, content_extension)


def read_plain(file_obj, filename):
    '''Reads a plain text file.'''
    _logger.info('Plain text: {}'.format(filename))
    for line in file_obj:
        yield line.strip()


def read_file(file_obj, filename):
    '''Reads a file with automatic type detection.'''
    extension = get_extension(filename)

    if extension in MULTI_FILE_ARCHIVE_EXTENSIONS:
        yield from read_archive(file_obj, filename)
    elif extension in STREAM_FILE_EXTENSIONS:
        yield from read_stream(STREAM_EXTENSION_MAP[extension](file_obj),
            filename)
    else:
        yield from read_plain(file_obj, filename)


def open_file(filename):
    '''Opens a file recursively and return its lines.'''
    _logger.info('Opening: {}'.format(filename))
    with open(filename, 'rb') as f:
        yield from read_file(f, filename)


def main():
    '''Runs as a program.'''
    arg_parser = argparse.ArgumentParser(
        description='Recursive deep archive iterator')
    arg_parser.add_argument('file')
    arg_parser.add_argument('--verbose', action='count')
    arg_parser.add_argument('--version', action='version', version=__version__)
    arg_parser.add_argument('--json', action='store_true',
        help='Attempt to decode line as JSON to printed Python dict')
    args = arg_parser.parse_args()

    if args.verbose:
        if args.verbose == 1:
            logging.basicConfig(level=logging.INFO)
        else:
            logging.basicConfig(level=logging.DEBUG)

    _logger.debug('Got path {}'.format(args.file))
    for line in open_file(args.file):
        if args.json:
            try:
                dict_obj = json.loads(line.decode())
            except ValueError:
                print(line)
            else:
                print(dict_obj)
        else:
            print(line)


if __name__ == '__main__':
    main()
