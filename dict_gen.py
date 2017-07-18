#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import os
import sys
import re
from glob import glob
import pickle


def list_headers(base_path):
    return [f for data in os.walk(base_path) for f in glob(os.path.join(data[0], '*.h'))]


def find_typedefs(headers):
    regex = re.compile('typedef')
    founded = []
    for header in headers:
        with open(header, 'r') as f:
            lines = f.readlines()
            for i in range(len(lines)):
                if regex.search(lines[i]):
                    stripped = lines[i].strip()
                    if not stripped.endswith(';'):
                        j = i
                        next_line = lines[j].strip()
                        while j < (len(lines) - 1) and not next_line.endswith(';'):
                            j += 1
                            next_line = lines[j].strip()
                            stripped += ' ' + next_line.strip()
                    founded.append(stripped)
    return founded


def create_names_dict(typedefs_list):
    names_dict = {}

    for element in typedefs_list:
        words = element.split(' ')
        i = 0
        while i < len(words):
            if words[i] == 'typedef':
                original_name = ''
                j = i + 1
                while j < len(words) and not words[j].endswith(';'):
                    original_name += ' ' + words[j]
                    j += 1
                if j < len(words) and words[j].endswith(';'):
                    names_dict[original_name.strip()] = (words[j])[:-1]
            i += 1
    return names_dict


def generate_names_dict(base_path, dest_file):
    header_files = list_headers(base_path)
    typedefs = find_typedefs(header_files)
    container_names_dict = create_names_dict(typedefs)
    output = open(dest_file, 'wb')
    pickle.dump(container_names_dict, output)
    output.close()


generate_names_dict(sys.argv[1], sys.argv[2])


