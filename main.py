#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys
from src.cursesWrapper import GuiLoader
from src.root import RootFileReader, OutputGenerator
import src.logger as logging


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
    output_generator = OutputGenerator(results)

    try:
        output_generator.save_to_output_file(sys.argv[2])
    except IndexError:
        logger.warning('Missing second argument. Results will not be saved')

    try:
        output_generator.save_items_to_pkl_file(sys.argv[3])
    except IndexError:
        logger.warning('Missing third argument. Items will not be saved to pickle file')

    exit_app()
