#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import re
import pickle
import ROOT
import logger


logger = logger.get_logger()

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

def load_pickle_file(path):
    f = open(path, 'rb')
    data = pickle.load(f)
    f.close()
    return data


class RootFileReader(object):
    def __init__(self, file_path, names_dict_path):
        self.input_file = file_path
        file = ROOT.TFile.Open(file_path)
        self.branches = file.CollectionTree.GetListOfBranches()
        self.global_classes_dict = load_pickle_file(names_dict_path)
        self.load_input_classes()
        self.splitting_regexp = '[.]'
        self.load_names_arrays()

    def get_class_name(self, branch):
        class_name = branch.GetClassName()
        name = re.split(self.splitting_regexp, branch.GetName())[0]
        if name in self.input_classes:
            class_name = self.input_classes[name]
        elif 'aux' in name or 'Aux' in name or class_name.startswith('vector') or not class_name:
            class_name = 'xAOD::AuxContainerBase'
        elif class_name in self.global_classes_dict:
            class_name = self.global_classes_dict[class_name]
        return re.sub('_v[1-9]', '', class_name)


    def load_names_arrays(self):
        self.names_arrays =  map(lambda x: re.split(self.splitting_regexp, self.get_class_name(x) + '#' + x.GetName()), self.branches)
    
    def load_input_classes(self):
        try:
            from AthenaCommon.AthenaCommonFlags import athenaCommonFlags
            athenaCommonFlags.FilesInput = [self.input_file]
            from RecExConfig.InputFilePeeker import inputFileSummary
            logger.info('Reading class names from input file')
            itemsdict = inputFileSummary['eventdata_itemsDic']
            classes = {}
            for key in itemsdict:
                for n in itemsdict[key]:
                    name = n if not n.endswith('.') else n[:-1]
                    classes[name] = key 
            self.input_classes = classes
        except ImportError as ie:
            self.input_classes = {}
            logger.warning('Cannot load class names from input file. Reason: ' + ie.message)


    def generate_data_dict(self):
        data_dict = {}
        for array in self.names_arrays:
            element = data_dict
            for name in array:
                if name.strip():
                    if name not in element:
                        element[name] = {}
                    element = element[name]
        return data_dict
