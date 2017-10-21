#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys
from src.cursesWrapper import GuiLoader
from src.root import RootFileReader



def save_results(results, path):
    f = open(path, 'w')
    f.write('obj = MSMgr.GetStream(0)\n')
    f.write('items = (obj.GetItems())[:]\n')
    f.write('for i in items:\n')
    f.write('\tobj.RemoveItem(i)\n')
    for item in results:
        name = item.name
        while item.parent:
            name = item.parent.name + '.' + name
            item = item.parent
        if 'aux' in name or 'Aux' in name:
        # name.startswith('xAOD::AuxContainerBase')):
            name += '.'
        f.write('obj.AddItem("' + name + '")\n')
        # f.write('obj.AddItem("' + name[6:] + '")\n')
    f.close()
    if sys.argv[3]:
        import pickle
        output = open(sys.argv[3], 'wb')
        pickle.dump(map(lambda x: x.name, results), output)
        output.close()


def print_results(results):
    for item in results:
        name = item.name
        while item.parent:
            name = item.parent.name + '.' + name
            item = item.parent
        print(name)
    print(len(results))


# Load data
rootReader = RootFileReader(sys.argv[1], './container_names.pkl')
data_dict = rootReader.generate_data_dict()  

guiLoader = GuiLoader(data_dict)
results = guiLoader.load_gui()
print_results(results)
# save_results(sys.argv[2], path)


# print data_dict