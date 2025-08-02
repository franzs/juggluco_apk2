#!/usr/bin/env python

import argparse
import html2text
import os
import re

import sys

from bs4 import BeautifulSoup


extra_changelog = {
    '9.0.17': 'Bug fix',
    '9.0.25': 'Bug fix.',
    '9.3.2': 'Bug Fixes.',
    '9.8.1': 'Juggluco 9.8.1 is still beta. People making use of Sibionics sensor can use it to get glucose values more in line with newer versions of the official Sibionics app.',
}

version_mappings = {
    '9.0.15': '9.0.16',
    '9.2.0': '9.2.1',
    '9.4.2': '9.4.3',
    '9.5.0': '9.5.2',
}


def parse_changelog(html_content):
    changelog_dict = {}

    soup = BeautifulSoup(html_content, 'html.parser')
    h = html2text.HTML2Text()

    body = soup.body
    for p in body.find_all('p'):
        stripped_p_text = p.text.strip()
        if re.match(r'\d+\.\d+(\.\d+)?', stripped_p_text):
            version_number = stripped_p_text

            if version_number in version_mappings:
                version_number = version_mappings[version_number]

            changes = []

            for sibling in p.next_siblings:
                stripped_sibling_text = sibling.text.strip()
                if sibling.name == 'p' and (re.match(r'\d+\.\d+(\.\d+)?', stripped_sibling_text) or stripped_sibling_text == 'Goto Start'):
                    break

                changes.append(str(sibling))

            changes_markdown = h.handle('\n'.join(changes))
            changes_markdown = re.sub(r'^ *', '', changes_markdown, flags=re.MULTILINE)

            changelog_dict[version_number] = changes_markdown

    return changelog_dict | extra_changelog


parser = argparse.ArgumentParser(prog=os.path.basename(__file__), description="Parses Juggluco's changelog")
parser.add_argument('filename')
parser.add_argument('version')

args = parser.parse_args()

with open(args.filename, 'r', encoding='utf-8') as file:
    html_content = file.read()
    changelog = parse_changelog(html_content)

    try:
        print(changelog[args.version].strip())
    except KeyError:
        print(f"No changes for version {args.version} found.", file=sys.stderr)
        sys.exit(1)
