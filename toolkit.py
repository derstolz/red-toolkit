#!/usr/bin/env python3
import os
from pathlib import Path


def get_arguments():
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('--search', dest='search', required=False,
                        help='Optional. A query to search within the toolkit.')
    parser.add_argument('--download', dest='download', required=False,
                        help='Optional. Download a tool by it\'s name. The tool will be downloaded in a newly created '
                             'directory.')
    options = parser.parse_args()

    return options


options = get_arguments()

import logging

logging.basicConfig(format='[%(asctime)s %(levelname)s]: %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p',
                    level='INFO')


class Tool:
    def __init__(self, line):
        assert line and line.strip() != ''
        self.name = line.split('**')[1].split('**')[0]
        self.description = line.split('**')[2].split('http')[0].strip()
        self.url = 'http' + line.split('http')[1]
        self.category = None
        self.is_downloaded = False

    def is_tool_downloaded(self):
        self.is_downloaded = os.path.exists(os.getcwd() + '/' + self.category['alias'] + '/' + self.name)
        return self.is_downloaded

    def find_category(self, readme_file):
        with open(readme_file, 'r') as file:
            sections = file.read().split('## ')
            for sec in sections:
                if self.url in sec:
                    category = sec.split('\n')[0]
                    self.category = {
                        'name': category,
                        'alias': category.lower().replace(' ', '-')
                    }

    def download(self):
        if self.is_downloaded:
            logging.info('%s is already downloaded', self.name)
            return
        from git.repo.base import Repo

        logging.info('Downloading %s', self.name)
        path = Path(os.getcwd() + '/' + self.category['alias'] + '/' + self.name)
        path.mkdir(parents=True, exist_ok=True)
        Repo.clone_from(self.url, path.name)

    def printout(self):
        print(self.name + ' // ' + self.category['name'])
        print('DONWLOADED' if self.is_downloaded else 'NOT_DOWNLOADED')
        print(self.url)
        print(self.description)


def get_tools_from_readme(readme_file):
    tools = []
    with open(readme_file, 'r') as file:
        lines = [line.replace('\n', '') for line in file.readlines()]
        for line in lines:
            if line.startswith('* **'):
                tool = Tool(line)
                tool.find_category(readme_file)
                tools.append(tool)
    return tools


def get_scripts_from_readme(readme_file):
    scripts_url = []
    with open(readme_file, 'r') as file:
        file_content_as_string = [line.replace('\n', '') for line in file.readlines()]
        for line in file_content_as_string:
            if line.startswith('  * '):
                scripts_url.append(line.replace('  * ', ''))
    return scripts_url


def interact(tools):
    prefix = 'toolkit:>> '
    while True:
        search = input(prefix)
        search_in_tools(search, tools)


def search_in_tools(search, tools):
    logging.info('Searching for %s', search)
    matched_tools = []
    for tool in tools:
        if search.lower() in tool.name.lower() or search.lower() in tool.description.lower():
            matched_tools.append(tool)
    logging.info("%s tools found", len(matched_tools))
    for tool in matched_tools:
        tool.printout()
        print('*' * 60)


readme = 'README.md'

scripts = get_scripts_from_readme(readme)
tools = get_tools_from_readme(readme)

logging.info('## Red-Teaming-Toolkit initialized')
logging.info('%s tools loaded', len(tools))
logging.info('%s scripts loaded', len(scripts))

try:
    if options.search:
        search_in_tools(options.search, tools)
    elif options.download:
        for t in tools:
            if t.name == options.download:
                t.download()
    else:
        interact(tools)
except KeyboardInterrupt:
    logging.info('Keyboard interrupt, exiting')
    exit(0)
except Exception as e:
    logging.error('Unexpected error: %s', e)