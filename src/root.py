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
        except Exception as ie:
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



class OutputElement(object):
    def __init__(self, name, splitting_character='#'):
        self.container_name, self.name = name.split(splitting_character)
        self.children = []
        self.is_aux = ('aux' in self.name or 'Aux' in self.name)
        self.aux_base_container = 'xAOD::AuxContainerBase'
        self.split_char = splitting_character

    def add_child(self, child_name):
        self.children.append(child_name)

    def remove_dyn_substring(self):
        if 'dyn' in self.name:
            self.name = self.name.replace('dyn', '')
        if 'Dyn' in self.name:
            self.name = self.name.replace('Dyn', '')

    def prepare_name(self):
        self.remove_dyn_substring()
        if self.is_aux or len(self.children)>0:
            children_string = '.'.join(self.children)
            self.name += '.{}'.format(children_string)

    def get_names(self):
        self.prepare_name()
        names = [self.split_char.join((self.container_name, self.name))]
        if self.container_name != self.aux_base_container and self.is_aux:
            names.append(self.split_char.join((self.aux_base_container, self.name)))
        return names



class OutputElementsDict(object):
    def __init__(self):
        self.elements_dict = {}    

    def add_element(self, element):
        if not element.parent:
            self.elements_dict[element.name] = OutputElement(element.name)
        else:
            p = element.parent
            while p.parent:
                p = p.parent
            if p.name in self.elements_dict:
                self.elements_dict[p.name].add_child(element.name)
            else:
                new_element = OutputElement(p.name)
                new_element.add_child(element.name)
                self.elements_dict[p.name] = new_element
                
    def get_elements(self):
        elems =  [value.get_names() for (key, value) in self.elements_dict.iteritems()]
        return elems



class OutputGenerator(object):
    def __init__(self, items):
        self.items = items
        self.elements_dict = OutputElementsDict()

    def generate_beginning_lines(self):
        return ['obj = MSMgr.GetStream(0)', 'items = (obj.GetItems())[:]', 'for i in items:', '\tobj.RemoveItem(i)']

    def generate_adding_statement(self, name):
        return 'obj.AddItem("{}")'.format(name)

    def generate_elements_adding_statements(self):
        elements_adding_statements = []
        for item in self.items:
            self.elements_dict.add_element(item)
        elements = self.elements_dict.get_elements()
        for names in elements:
            for name in names:
                elements_adding_statements.append(self.generate_adding_statement(name))
        return elements_adding_statements

    def save_to_output_file(self, file_path):
        beginning = self.generate_beginning_lines()
        adding = self.generate_elements_adding_statements()
        lines = beginning + adding
        file = open(file_path, 'w')
        file.write('\n'.join(lines) + '\n')
        file.close()
    
    def save_items_to_pkl_file(self, file_path):
        output = open(file_path, 'wb')
        pickle.dump(map(lambda x: x.name, self.items), output)
        output.close()



# def save_results(results, path):
#     f = open(path, 'w')
#     f.write('obj = MSMgr.GetStream(0)\n')
#     f.write('items = (obj.GetItems())[:]\n')
#     f.write('for i in items:\n')
#     f.write('\tobj.RemoveItem(i)\n')
#     for item in results:
#         name = item.name
#         while item.parent:
#             name = item.parent.name + '.' + name
#             item = item.parent
#         if 'aux' in name or 'Aux' in name:
#             name += '.'
#         if 'dyn' in name:
#             name = name.replace('dyn', '')
#         if 'Dyn' in name:
#             name = name.replace('Dyn', '')
#         f.write('obj.AddItem("' + name + '")\n')
#         container_name = name.split('#')[0]
#         aux_base_container = 'xAOD::AuxContainerBase'
#         if container_name != aux_base_container and ('aux' in name or 'Aux' in name):
#             name_with_base_container = aux_base_container + '#' + name.split('#')[1]
#             f.write('obj.AddItem("' + name_with_base_container + '")\n')
#     f.close()
#     if len(sys.argv)>3:
#         import pickle
#         output = open(sys.argv[3], 'wb')
#         pickle.dump(map(lambda x: x.name, results), output)
#         output.close()