#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
 
import sys
import curses
import curses.textpad
from root import RootFileReader, OutputElementsDict
import logger as logging
import utils
from element import Element
import copy

logger = logging.get_logger()


class Pad(object):
    def __init__(self, data_structures, chosen_items, width, height, start_x=0):
        self.all_structures = data_structures
        self.width = width
        self.start_x = start_x
        self.pad = curses.newpad(32000, width)
        self.actual_offset = 0
        self.pad_height = height - 1
        
        self.initialize_styles()
        self.chosen_items = chosen_items if chosen_items else set()
        self.initialize_structures()
        self.actual_y = 0
        self.initialize_cursor()
        self.refresh()

    def initialize_styles(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Sets up color pair
        highlighted = curses.color_pair(1)  # coloring for a highlighted menu option
        normal = curses.A_NORMAL  # coloring for a non highlighted menu option
        self.styles = {'normal': normal, 'highlighted': highlighted}


    def initialize_structures(self):
        # self.all_structures = Element.generate_structure(self.data_dict, self.start_x)
        self.structures = self.all_structures[:]
        self.draw_all_structures()

        # # Select all structures (to be removed)
        # for i in self.structures:
        #     i.selected = True
        #     self.chosen_items.add(i)

    def initialize_cursor(self):
        # Highlight cursor on initial position
        try:
            if self.actual_y > len(self.lines):
                self.actual_y = 0
            element = self.lines[self.actual_y]
            curses.setsyx(self.actual_y, element.x_pos + 1)
            self.pad.addch(curses.getsyx()[0], curses.getsyx()[1], self.get_mark_character(element), self.styles['highlighted'])
            curses.curs_set(0)
        except IndexError:
            # Handle situation when self.lines list is empty
            pass

    def get_mark_character(self, structure):
        return structure.get_mark_character()

    def draw_structure(self, structure, y):
        self.pad.addstr(y, structure.x_pos, '[' + self.get_mark_character(structure) + '] ' + structure.name, self.styles['normal'])
        self.lines.insert(y, structure)
        y += 1
        if structure.show_children:
            for child in structure.children:
                y = self.draw_structure(child, y)
        return y

    def draw_all_structures(self):
        self.lines = []
        y = 0
        for i in self.structures:
            y = self.draw_structure(i, y)
        self.refresh()

    def get_character(self, y, x):
        actual_character = chr(self.pad.inch(y, x) & 0xFF)
        return actual_character

    def refresh(self):
        cursor_pos = curses.getsyx()
        self.pad.refresh(self.actual_offset, 0, 0, self.start_x, self.pad_height, self.width + self.start_x - 2)
        cursor_pos = curses.getsyx()
        curses.setsyx(cursor_pos[0], cursor_pos[1] - self.start_x)

    def redraw(self, reinit_cursor=False):
        cursor_pos = curses.getsyx()
        self.pad.clear()
        self.draw_all_structures()
        actual_character = self.get_character(cursor_pos[0] + self.actual_offset, cursor_pos[1] - 1)
        if reinit_cursor:
            self.actual_offset = 0
            self.initialize_cursor()
        else:
            self.actual_y = cursor_pos[0] + self.actual_offset
            self.pad.move(cursor_pos[0] + self.actual_offset, cursor_pos[1])
            self.pad.addch(cursor_pos[0] + self.actual_offset, cursor_pos[1] - 1, actual_character, self.styles['highlighted'])
        self.refresh()

    def hide_cursor(self):
        cursor_pos = curses.getsyx()
        actual_character = self.get_character(cursor_pos[0] + self.actual_offset, cursor_pos[1] - 1)
        self.pad.addch(cursor_pos[0] + self.actual_offset, cursor_pos[1] - 1, actual_character, self.styles['normal'])
        self.refresh()

    def show_cursor(self):
        cursor_pos = curses.getsyx()
        actual_character = self.get_character(cursor_pos[0] + self.actual_offset, cursor_pos[1] - 1)
        self.pad.addch(cursor_pos[0] + self.actual_offset, cursor_pos[1] - 1, actual_character, self.styles['highlighted'])
        self.refresh()

    def filter(self, text):
        if len(text) > 0:
            self.structures = filter(lambda el: el.check_filter(text), self.all_structures)
        else:
            self.structures = self.all_structures[:]
        self.redraw(True)
        
    def move_cursor(self, number):
        cursor_pos = curses.getsyx()
        actual_character = self.get_character(cursor_pos[0] + self.actual_offset, cursor_pos[1] - 1)
        self.pad.addch(cursor_pos[0] + self.actual_offset, cursor_pos[1] - 1, actual_character, self.styles['normal'])
        self.actual_y += number
        curses.setsyx(cursor_pos[0] + number, self.lines[self.actual_y].x_pos + 1)
        cursor_pos = curses.getsyx()
        actual_character = self.get_character(cursor_pos[0] + self.actual_offset, cursor_pos[1])
        self.pad.addch(cursor_pos[0] + self.actual_offset, cursor_pos[1], actual_character, self.styles['highlighted'])
        self.refresh()

    def select_element(self, y):
        element = self.lines[y]
        element.select()
        self.chosen_items.add(element)

    def diselect_element(self, y):
        element = self.lines[y]
        self.chosen_items.discard(element)
        element.diselect()

    def scroll(self, number):
        cursor_pos = curses.getsyx()
        self.pad.move(cursor_pos[0] + self.actual_offset, cursor_pos[1])
        self.actual_offset += number
        self.refresh()

    def update_selection(self):
        element = self.lines[self.actual_y]
        if element.selected:
            self.diselect_element(self.actual_y)
        else:
            self.select_element(self.actual_y)
        self.redraw()


    def handle_event(self, event):
        if event == curses.KEY_DOWN:
            if self.actual_y < len(self.lines) - 1:
                self.move_cursor(1)
                cursor_pos = curses.getsyx()
                if cursor_pos[0] > self.pad_height - 4:
                    self.scroll(1)

        if event == curses.KEY_UP:
            if self.actual_y >= 1:
                self.move_cursor(-1)
                cursor_pos = curses.getsyx()
                if cursor_pos[0] < 4 and self.actual_offset > 0:
                    self.scroll(-1)

        if event == ord('i'):
            element = self.lines[self.actual_y]
            if not element.show_children:
                element.show_children = True
            else:
                element.show_children = False
            self.redraw()

        if event == curses.KEY_RIGHT:
            element = self.lines[self.actual_y]
            element.show_children = True
            self.redraw()

        if event == curses.KEY_LEFT:
            element = self.lines[self.actual_y]
            element.show_children = False
            self.redraw()

    def save_data(self, path):
        if len(path) > 0:
            if not path.endswith('.pkl'):
                path = path + '.pkl'
            logger.info('Saving configuration')
            try:
                utils.save_configuration(path, self.all_structures, self.chosen_items)
                logger.info('Configuration saved to file: {}'.format(path))
            except TypeError as e:
                logger.error('Error while saving configuration: {}'.format(e.message))
                


class DynamicPad(Pad):
    def __init__(self, data_structures, width, height, start_x=0):
        self.all_structures = data_structures
        self.width = width
        self.start_x = start_x
        self.pad = curses.newpad(32000, width)
        self.actual_offset = 0
        self.pad_height = height - 1
        
        self.initialize_styles()
        self.initialize_structures()
        self.actual_y = 0
        self.refresh()

    def update_data_structure(self, new_structure):
        self.all_structures = new_structure
        self.structures = self.all_structures[:]
        self.redraw(True)
        try:
            self.hide_cursor()
        except:
            pass
        

    def get_mark_character(self, structure):
        return ' '
        
    def update_selection():
        pass

    def save_data(self, path):
        logger.error('Data in dynamic pad cannot be saved')


class GuiLoader(object):
    
    def __init__(self, data_structures, chosen_items):
        self.data_structures = data_structures
        self.initial_chosen_items = chosen_items
        self.width, self.height, self.pad_height = (0, 0, 0)
        self.pad = None
        self.actual_offset = 0
        self.screen = None

    def __initialize_window(self):
        self.height, self.width = self.screen.getmaxyx()
        self.window = curses.newwin(self.height, self.width, 0, 0)
        self.pad = Pad(self.data_structures, self.initial_chosen_items, self.width/2-1 , self.height)
        self.chosen_items_pad = DynamicPad([], self.width / 2 - 1, self.height, self.width / 2 + 2)
        self.reinit_chosen_items_pad()
        self.actual_pad = self.pad
        self.inactive_pad = self.chosen_items_pad
        self.pad_height = self.height - 1
        self.actual_pad.refresh()

    def __initialize(self, stdscreen):        
        self.screen = stdscreen
        # curses.initscr() 
        self.screen.refresh()
        self.__initialize_window()
        self.__start_event_loop()

    def load_gui(self):
        curses.wrapper(self.__initialize)
        return {
            'chosen_items': self.pad.chosen_items,
            'structures': self.pad.all_structures
        }

    def search(self):
        search_size = 50
        b_starty = 0
        b_startx = self.width - search_size
        b_width = search_size
        b_height = 3
        search = SearchModal(b_startx, b_starty, b_width, b_height)
        text = search.edit()
        self.pad.filter(text)

    def reinit_chosen_items_pad(self):
        chosen_items_structure = []
        structure_copy = copy.deepcopy(self.data_structures)
        for element in structure_copy:
            chosen = element.get_selected()
            if chosen:
                chosen_items_structure.append(chosen)
        self.chosen_items_pad.update_data_structure(chosen_items_structure)

    def __start_event_loop(self):
        while True:
            event = self.screen.getch()
            if event == ord('q'):
                break
            
            elif event == ord(' '):
                if self.actual_pad == self.pad:
                    self.pad.update_selection()
                    self.reinit_chosen_items_pad()
                    self.pad.refresh()

            elif event == ord('\t'):
                if len(self.inactive_pad.all_structures) == 0:
                    continue
                self.actual_pad.hide_cursor()
                self.actual_pad, self.inactive_pad = self.inactive_pad, self.actual_pad
                self.actual_pad.refresh()
                self.actual_pad.show_cursor()

            elif event == ord('f'):
                self.search()
            
            elif event == ord('s'):
                input_size = 50
                b_starty = (self.height/2) - 2
                b_startx = (self.width/2) - (input_size/2)
                b_width = input_size
                b_height = 10
                input_modal = InputModal(b_startx, b_starty, b_width, b_height, 'Provide path')
                path = input_modal.get_input()
                self.pad.save_data(path)
                self.window.refresh()
                self.actual_pad.refresh()
                self.inactive_pad.refresh()

            else:
                self.actual_pad.handle_event(event)



class Modal(object):
    def __init__(self, start_x, start_y, width, height):
        self.width = width
        self.height = height
        self.start_x = start_x
        self.start_y = start_y
        self.window = curses.newwin(height, width, start_y, start_x)
        self.window.box()
        self.refresh()

    def refresh(self):
        self.window.refresh()

    def destroy(self):
        del self.window


class SearchModal(Modal):
    def __init__(self, start_x, start_y, width, height):
        super(SearchModal, self).__init__(start_x, start_y, width, height)
        self.search_window = self.window.derwin(self.height-2, self.width-2, 1, 1)
        self.search = curses.textpad.Textbox(self.search_window)

    def edit(self):
        return self.search.edit().strip()


class InputModal(Modal):
    def __init__(self, start_x, start_y, width, height, message):
        super(InputModal, self).__init__(start_x, start_y, width, height)
        self.message_box = self.window.derwin((self.height/2)-2, self.width-2, (self.height/2)-1, 1)
        self.message_box.addstr(0, (self.width/2) - len(message)/2, message, curses.A_NORMAL)
        self.message_box.refresh()
        input_width = 30
        if input_width >= (self.width - 2):
            input_width = self.width -2 
        input_starty, input_startx = (self.height/2+1, self.width/2-input_width/2)
        self.input_box = self.window.derwin(1, input_width, input_starty, input_startx)
        self.input = curses.textpad.Textbox(self.input_box)

    def get_input(self):
        return self.input.edit().strip()