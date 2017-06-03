#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import ROOT
import re


def get_simple_dict():
    return {
        'first': {'aa': {}, 'bb': {}, 'cc': {}, 'mm': {}, 'nn': {}},
        'second': {
            'dd': {},
            'third': {'ee': {}},
            'forth': {
                'ff': {},
                'fifth': {'sss': {}, 'sadasdsd': {}}
            }
        }
    }


def load_data_file(path):
    return ROOT.TFile.Open(path)


def get_names_arrays(data_file, splitting_regexp):
    return map(lambda x: re.split(splitting_regexp, x.GetName()), data_file.CollectionTree.GetListOfBranches())


def generate_data_dict(path):
    names_arrays = get_names_arrays(load_data_file(path), '[.,_]')
    data_dict = {}
    for array in names_arrays:
        element = data_dict
        for name in array:
            if name.strip():
                if name not in element:
                    element[name] = {}
                element = element[name]
    return data_dict