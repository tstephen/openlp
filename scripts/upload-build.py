#!/usr/bin/env python3
import os
import sys
from argparse import ArgumentParser, Namespace
from pathlib import Path
from packaging.version import parse
from urllib.parse import quote_plus

try:
    import requests
    HAS_REQUESTS = True
except ImportError:
    HAS_REQUESTS = False


def parse_args() -> Namespace:
    parser = ArgumentParser()
    parser.add_argument('filename', type=Path, help='File to upload')
    parser.add_argument('--env-var', '-e', metavar='ENV_VAR', default='UPLOAD_TOKEN',
                        help='Name of the environment variable containing the token. Defaults to UPLOAD_TOKEN')
    parser.add_argument('--upload-url', '-u', metavar='UPLOAD_URL', default='https://get.openlp.io/api/files/',
                        help='The base URL to use when uploading. Needs a trailing slash.')
    return parser.parse_args()


def upload_file(upload_url: str, filename: Path, destination: str, upload_token: str) -> bool:
    """Upload a file to object storage"""
    print(f'Uploading {filename.name} to {upload_url}{destination}')
    response = requests.post(upload_url + destination, files={'file': filename.open('rb')},
                             headers={'X-Upload-Token': upload_token})
    is_success = response.status_code == 201
    if is_success:
        print('Uploaded successfully')
    return is_success


def get_upload_token(env_var: str) -> str:
    """Get the upload token from the environment"""
    if not os.environ.get(env_var):
        raise KeyError(f'{env_var} not found in environment')
    return os.environ[env_var]


def get_version_number(filename: Path) -> str:
    """Strip down a filename to just the version number"""
    basename = filename.stem.replace('.tar', '')
    version_number = basename.split('-')[1]
    return version_number


def get_destination(filename: Path) -> str:
    """Determine where in the object storage this file should be going"""
    version = parse(get_version_number(filename))
    base_dir = 'builds'
    vname = quote_plus(version.public)
    fname = quote_plus(filename.name)
    if version.local:
        base_dir = 'builds'
        vname += f'+{version.local}'
    elif version.is_devrelease:
        base_dir = 'nightlies'
    elif version.is_prerelease:
        base_dir = 'prereleases'
    elif not version.local and not version.is_devrelease and not version.is_prerelease:
        base_dir = 'releases'
    return f'{base_dir}/{vname}/{fname}'


def main():
    """Run the script"""
    if not HAS_REQUESTS:
        print('ERROR: The requests library is not installed. Please install it before running this script again.')
        sys.exit(1)
    args = parse_args()
    try:
        upload_token = get_upload_token(args.env_var.upper())
    except KeyError as e:
        print(e)
        sys.exit(2)
    destination = get_destination(args.filename)
    is_success = upload_file(args.upload_url, args.filename, destination, upload_token)
    if not is_success:
        print('ERROR: Unable to upload file')
        sys.exit(3)


if __name__ == '__main__':
    main()
