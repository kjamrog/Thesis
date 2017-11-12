#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys
from src.cursesWrapper import GuiLoader
from src.root import RootFileReader, OutputGenerator
import src.logger as logging
import argparse


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
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help='Input file path')
    parser.add_argument('-o', '--output', type=str, help='Path to file to which results will be saved')
    parser.add_argument('-p', '--pickle', type=str, help='Path to file to which selected elements will be saved in pickle format')
    args = parser.parse_args()

    logger.info(args)

    input_file_path = args.input
    if not input_file_path:
        logger.error('Missing input file path')
        exit_app(1)
    
    logger.info('Loading data form input file: ' + input_file_path)
    
    root_reader = RootFileReader(input_file_path, './container_names.pkl')
    data_dict = root_reader.generate_data_dict()  

    logger.info('Data loaded')

    gui_loader = GuiLoader(data_dict)
    results = gui_loader.load_gui()
    print_results(results)
    output_generator = OutputGenerator(results)

    output_file = args.output
    if output_file:  
        output_generator.save_to_output_file(output_file)
    else:
        logger.warning('Missing second argument. Results will not be saved')

    pkl_output = args.pickle
    if pkl_output:
        output_generator.save_items_to_pkl_file(pkl_output)
    else:
        logger.warning('Missing third argument. Items will not be saved to pickle file')

    exit_app()
