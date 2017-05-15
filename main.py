#!/usr/bin/env python3.5

import time
import curses
import sys



class Element(object):
    def __init__(self, name, x_pos, parent=None):
        self.name = name
        self.x_pos = x_pos
        self.parent = parent
        self.children = []
        self.show_children = False
        self.selected = False
        self.selected_children_number = 0

    def add_child(self, child):
        if type(child) is str:
            child = Element(child, self.x_pos+3, self)
        self.children.append(child)
        

    @staticmethod
    def create_elements_structure(d, x_pos, parent=None):
        elements = []
        for i in d:
            element = Element(i, x_pos, parent)
            elements.append(element)
            if len(d[i])>0:
                element.add_children(d[i], x_pos+3)
        return elements;
            

    def add_children(self, children, x_pos):
        for child in children:
            if type(child) is dict:
                self.add_children(Element.create_elements_structure(child, x_pos, self), x_pos)
            elif type(child) is str:
                self.add_child(child)
            elif type(child) is Element:
                self.add_child(child)



class Main(object):

    def __init__(self, stdscreen):
        self.screen = stdscreen
        curses.initscr()
        curses.noecho()
        curses.mousemask(1)
        curses.cbreak()
        curses.start_color()
        self.screen.keypad(1)

        curses.init_pair(1,curses.COLOR_BLACK, curses.COLOR_WHITE) # Sets up color pair #1, it does black text with white background
        highlighted = curses.color_pair(1) #h is the coloring for a highlighted menu option
        normal = curses.A_NORMAL #n is the coloring for a non highlighted menu option
        self.styles = {'normal': normal, 'highlighted': highlighted}


        start_x = start_y = 0
        height = 10000
        width = 100

        self.lines = []
        self.chosen_items = set()

        self.win = curses.newwin(height, width, start_y, start_x)
        self.pad = curses.newpad(32000, 100)
        self.actual_offset = 0
        self.pad_height = 30
        self.win.keypad(1)

        # Creating and drawing structures
        test_dict = self.get_simple_dict()
        for i in range(1000):
            test_dict['first'].append('ssssssss')
        self.structures = Element.create_elements_structure(test_dict, 0)
        self.draw_all_structures()
        self.actual_y = 0
        
        # Highlighting cursor on initial position
        curses.setsyx(0,self.lines[self.actual_y].x_pos + 1)
        self.pad.addch(curses.getsyx()[0], curses.getsyx()[1], ' ', highlighted)
        curses.curs_set(0)
        self.screen.nodelay(True)
        self.refresh_pad()


        self.test_data = []

        event = None
        while True:
            event = self.screen.getch() 
            if event == ord("q"): break 

            if event == curses.KEY_DOWN: 
                if(self.actual_y < len(self.lines)-1):
                    self.move_cursor(1)
                    cursor_pos = curses.getsyx()
                    if cursor_pos[0] > self.pad_height-4:
                        self.scroll(1)
                    
            if event == curses.KEY_UP: 
                if(self.actual_y >= 1):
                    self.move_cursor(-1)
                    cursor_pos = curses.getsyx()
                    if cursor_pos[0] < 4 and self.actual_offset > 0:
                        self.scroll(-1)
                    
            if event == curses.KEY_PPAGE:
                if self.actual_offset>0:
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


        curses.endwin()
        self.print_results()


    def show_children(self, d):
        if 'show_children' in d and d['show_children'] and 'children' in d and type(d['children']) is list:
            return True
        else:
            return False
    

    def get_simple_dict(self):
        return {
            'first': ['aa', 'bb', 'cc', 'mm', 'nn'],
            'second': ['dd', {
                'third': ['ee'],
                'forth': ['ff', {
                    'fifth': ['sss', 'sadasdsd']
                }]
            }]
        }


    def draw_structure(self, structure, y):
        mark_character = ' '
        if structure.selected:
            mark_character = 'X'
        elif structure.selected_children_number > 0:
            mark_character = 'O'
        self.pad.insnstr(y, structure.x_pos, '[' + mark_character + '] ' + structure.name, self.styles['normal'])
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

    
    def refresh_pad(self):
        self.pad.refresh(self.actual_offset,0, 0,0, self.pad_height,75)


    def redraw(self):
        cursor_pos = curses.getsyx()
        self.pad.clear()
        self.draw_all_structures()
        self.pad.move(cursor_pos[0]+self.actual_offset, cursor_pos[1])
        self.actual_y = cursor_pos[0] + self.actual_offset
        actual_character = self.get_character(cursor_pos[0]+self.actual_offset, cursor_pos[1]-1)
        self.pad.addch(cursor_pos[0]+self.actual_offset, cursor_pos[1]-1, actual_character, self.styles['highlighted'])
        self.refresh_pad()


    def move_cursor(self, number):
        cursor_pos = curses.getsyx()
        actual_character = self.get_character(cursor_pos[0]+self.actual_offset, cursor_pos[1]-1)
        self.pad.addch(cursor_pos[0]+self.actual_offset, cursor_pos[1] - 1 , actual_character, self.styles['normal'])
        self.actual_y += number
        curses.setsyx(cursor_pos[0]+number, self.lines[self.actual_y].x_pos + 1)
        cursor_pos = curses.getsyx()
        actual_character = self.get_character(cursor_pos[0]+self.actual_offset, cursor_pos[1])
        self.pad.addch(cursor_pos[0]+self.actual_offset, cursor_pos[1], actual_character, self.styles['highlighted'])
        self.refresh_pad()


    def select_element(self, y):
        element = self.lines[y]
        element.selected = True 
        self.chosen_items.add(element)
        while element.parent and (element.selected or element.selected_children_number>0):
            parent = element.parent
            parent.selected_children_number += 1
            element = parent
        

    def diselect_element(self, y):
        element = self.lines[y]
        element.selected = False 
        self.chosen_items.discard(element)
        while element.parent and (not element.selected or element.selected_children_number==0):
            parent = element.parent
            parent.selected_children_number -= 1
            element = parent


    def scroll(self, number):
        cursor_pos = curses.getsyx()
        self.pad.move(cursor_pos[0]+self.actual_offset, cursor_pos[1])
        self.actual_offset += number
        self.refresh_pad()


    def print_results(self):
        for item in self.chosen_items:
            name = item.name
            while item.parent:
                name = item.parent.name + '.' + name
                item = item.parent
            print(name)



curses.wrapper(Main)
