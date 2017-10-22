#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys
from src.cursesWrapper import GuiLoader
from src.root import RootFileReader
import src.logger as logging


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
            name += '.'
        f.write('obj.AddItem("' + name + '")\n')
    f.close()
    if len(sys.argv)>3:
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

def exit_app(exit_code=0):
    logging.print_logs()
    sys.exit(exit_code)



if __name__ == '__main__':
    # Set up logger
    logging.setup()
    logger = logging.get_logger()
    
    try:
        inputFilePath = sys.argv[1]
        logger.info('Loading data form input file: ' + inputFilePath)
    except IndexError:
        logger.error('Missing input file path')
        exit_app(1)

    # Load data
    rootReader = RootFileReader(sys.argv[1], './container_names.pkl')
    data_dict = rootReader.generate_data_dict()  

    logger.info('Data loaded')

    guiLoader = GuiLoader(data_dict)
    results = guiLoader.load_gui()
    print_results(results)

    try:
        save_results(sys.argv[2], path)
    except IndexError:
        logger.warning('Missing second argument. Results will not be saved')

    exit_app()
