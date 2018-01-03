#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-

import sys
from src.cursesWrapper import GuiLoader, Element
from src.root import RootFileReader, OutputGenerator
import src.logger as logging
import argparse
import src.utils as utils


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
    logging.setup()
    logger = logging.get_logger()
    
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', type=str, help='xAOD input file path')
    parser.add_argument('-pi', '--pickle-input', type=str, help='pickle input file path')
    parser.add_argument('-o', '--output', type=str, help='Path to file to which results will be saved')
    parser.add_argument('-p', '--pickle', type=str, help='Path to file to which selected elements will be saved in pickle format')
    args = parser.parse_args()

    input_file_path = args.input
    pickle_input_file_path = args.pickle_input
    if not input_file_path and not pickle_input_file_path:
        logger.error('Missing input file')
        exit_app(1)
     
    data_structures = None

    if input_file_path:
        logger.info('Loading data from input file: ' + input_file_path)
        root_reader = RootFileReader(input_file_path, './container_names.pkl')
        data_dict = utils.generate_data_dict(root_reader.names_arrays)  
        data_structures = Element.generate_structure(data_dict, 0)
        initial_chosen_items = set()
    else:
        logger.info('Loading data from pickle file')
        try:
            initial_data = utils.load_initial_data(pickle_input_file_path)
            data_structures = initial_data['structures']
            initial_chosen_items = initial_data['chosen_items']
        except TypeError as e:
            logger.error('Invalid data in pickle file: {}'.format(e.message))
            exit_app(1)

    logger.info('Data loaded. {} elements found'.format(len(data_structures)))

    gui_loader = GuiLoader(data_structures, initial_chosen_items)
    results = gui_loader.load_gui()
    # print_results(results)
    chosen_items = results['chosen_items']
    output_generator = OutputGenerator(chosen_items)

    output_file = args.output
    if output_file:  
        logger.info('Generating output python script: {}'.format(output_file))
        output_generator.save_to_output_file(output_file)
        logger.info('Output script {} generated'.format(output_file))
    else:
        logger.warning('Missing second argument. Results will not be saved')

    pkl_output = args.pickle
    if pkl_output:
        logger.info('Saving configuration')
        utils.save_configuration(pkl_output, results['structures'], chosen_items)
        logger.info('Configuration saved to file: {}'.format(pkl_output))
    else:
        logger.warning('Missing third argument. Items will not be saved to pickle file')

    exit_app()
