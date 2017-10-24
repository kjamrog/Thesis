#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
 
import sys
import curses
import curses.textpad
from root import RootFileReader
import logger as logging

logger = logging.get_logger()

class Element(object):
    def __init__(self, name, x_pos, parent=None):
        self.name = name
        self.x_pos = x_pos
        self.parent = parent
        self.children = []
        self.show_children = False
        self.selected = False
        self.selected_children_number = 0

    def check_filter(self, filter_text):
        if filter_text in self.name:
            return True
        for child in self.children:
            if child.check_filter(filter_text):
                # self.show_children = True
                return True
        return False

    def get_mark_character(self):
        if self.selected:
            return 'X'
        elif self.selected_children_number > 0:
            return 'O'
        else:
            return ' '

    def add_child(self, child):
        if type(child) is str:
            child = Element(child, self.x_pos + 3, self)
        self.children.append(child)

    def add_children(self, child, x_pos):
        if type(child) is dict:
            self.add_children(Element.create_elements_structure(child, x_pos, self), x_pos)
        elif type(child) is str:
            self.add_child(child)

    @staticmethod
    def create_elements_structure(d, x_pos, parent=None):
        elements = []
        for i in d:
            element = Element(i, x_pos, parent)
            elements.append(element)
            if parent is not None:
                parent.add_child(element)
            if d[i] is not None:
                element.add_children(d[i], x_pos + 3)
        return elements

    @staticmethod
    def generate_structure(d, x_pos):
        structure = Element.create_elements_structure(d, x_pos)
        structure.sort(key=lambda x: x.name)
        return structure



class Pad(object):
    
    def __init__(self, data_dict, width, height):
        self.data_dict = data_dict
        self.width = width
        self.pad = curses.newpad(32000, width)
        self.actual_offset = 0
        self.pad_height = height - 1
        
        self.initialize_styles()
        self.initialize_structures()
        self.draw_all_structures()
        self.initialize_cursor()
        self.refresh()


    def initialize_styles(self):
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)  # Sets up color pair
        highlighted = curses.color_pair(1)  # coloring for a highlighted menu option
        normal = curses.A_NORMAL  # coloring for a non highlighted menu option
        self.styles = {'normal': normal, 'highlighted': highlighted}


    def initialize_structures(self):
        self.all_structures = Element.generate_structure(self.data_dict, 0)
        self.structures = self.all_structures[:]
        self.lines = []
        self.chosen_items = set()

        # Select all structures (to be removed)
        for i in self.structures:
            i.selected = True
            self.chosen_items.add(i)

    def initialize_cursor(self):
        # Highlight cursor on initial position
        try:
            self.actual_y = 0
            element = self.lines[self.actual_y]
            curses.setsyx(0, element.x_pos + 1)
            self.pad.addch(curses.getsyx()[0], curses.getsyx()[1], element.get_mark_character(), self.styles['highlighted'])
            curses.curs_set(0)
        except IndexError:
            # Handle situation when self.lines list is empty
            pass


    def draw_structure(self, structure, y):
        self.pad.insnstr(y, structure.x_pos, '[' + structure.get_mark_character() + '] ' + structure.name, self.styles['normal'])
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

    def get_character(self, y, x):
        actual_character = chr(self.pad.inch(y, x) & 0xFF)
        return actual_character

    def refresh(self):
        self.pad.refresh(self.actual_offset, 0, 0, 0, self.pad_height, self.width/2)
        # self.second_pad.refresh(0, 0, 0, self.width/2 + 1, self.pad_height, self.width)


    def redraw(self, reinit_cursor=False):
        cursor_pos = curses.getsyx()
        self.pad.clear()
        self.draw_all_structures()
        self.pad.move(cursor_pos[0] + self.actual_offset, cursor_pos[1])
        self.actual_y = cursor_pos[0] + self.actual_offset
        actual_character = self.get_character(cursor_pos[0] + self.actual_offset, cursor_pos[1] - 1)
        if reinit_cursor:
            self.actual_offset = 0
            self.initialize_cursor()
        else:
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
        element.selected = True
        self.chosen_items.add(element)
        while element.parent and (element.selected or element.selected_children_number > 0):
            parent = element.parent
            parent.selected_children_number += 1
            element = parent

    def diselect_element(self, y):
        element = self.lines[y]
        element.selected = False
        self.chosen_items.discard(element)
        while element.parent and (not element.selected or element.selected_children_number == 0):
            parent = element.parent
            parent.selected_children_number -= 1
            element = parent

    def scroll(self, number):
        cursor_pos = curses.getsyx()
        self.pad.move(cursor_pos[0] + self.actual_offset, cursor_pos[1])
        self.actual_offset += number
        self.refresh()


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

        if event == curses.KEY_PPAGE:
            if self.actual_offset > 0:
                self.scroll(-1)

        if event == curses.KEY_NPAGE:
            self.scroll(1)

        if event == ord(" "):
            element = self.lines[self.actual_y]
            if element.selected:
                self.diselect_element(self.actual_y)
            else:
                self.select_element(self.actual_y)
            self.redraw()

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




class GuiLoader(object):
    
    def __init__(self, data_dict):
        self.data_dict = data_dict

    def initialize_window(self, initialize_offset=True):
        self.height, self.width = self.screen.getmaxyx()
        # self.win = curses.newwin(self.height, self.width,start_y, start_x)
        self.pad = Pad(self.data_dict, self.width, self.height)
        self.actual_offset = 0
        self.pad_height = self.height - 1
        # self.win.keypad(1)

    def initialize(self, stdscreen):        
        self.screen = stdscreen
        curses.initscr() 
        self.initialize_window()
        self.start_event_loop()        
        curses.endwin()

        ##########################################
        ## Currently unnecessary settings ########
        ###########################################
        # curses.noecho()
        # curses.mousemask(1)
        # curses.cbreak()
        # curses.start_color()
        # self.screen.keypad(1)
        # self.screen.nodelay(True)



    def load_gui(self):
        curses.wrapper(self.initialize)
        return self.pad.chosen_items

    def start_event_loop(self):
        while True:
            event = self.screen.getch()
            if event == ord("q"):
                break

            elif event == ord('f'):
                ## initializing search input
                search_size = 50
                b_starty = 0
                b_startx = self.width - search_size
                b_width = search_size
                b_height = 3
                # search_border = self.win.derwin(b_height, b_width, b_starty, b_startx)
                search_border = curses.newwin(b_height, b_width, b_starty, b_startx)
                search_border.border()
                search_window = search_border.derwin(b_height-2, b_width-2, 1, 1)
                search = curses.textpad.Textbox(search_window)
                self.pad.refresh()
                search_border.refresh()
                text = search.edit().rstrip()
                self.pad.filter(text)
            
            else:
                self.pad.handle_event(event)
