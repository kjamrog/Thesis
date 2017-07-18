#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import ROOT
import re
import pickle


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


def load_names_dict(dict_path):
    dict_file = open(dict_path, 'rb')
    names = pickle.load(dict_file)
    dict_file.close()
    return names


def get_class_name(branch, names_dict):
    # return re.sub('_v[1-9]', '', branch.GetClassName())
    original_name = branch.GetClassName()
    if original_name in names_dict:
        return names_dict[original_name]
    else:
        return original_name


def get_names_arrays(data_file, splitting_regexp):
    names_dict = load_names_dict('./container_names.pkl')
    return map(lambda x: re.split(splitting_regexp, get_class_name(x) + '#' + x.GetName()), data_file.CollectionTree.GetListOfBranches())


def generate_data_dict(path):
    names_arrays = get_names_arrays(load_data_file(path), '[.]')
    data_dict = {}
    for array in names_arrays:
        element = data_dict
        for name in array:
            if name.strip():
                if name not in element:
                    element[name] = {}
                element = element[name]
    return data_dict
