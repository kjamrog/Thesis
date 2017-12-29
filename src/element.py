import copy

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

    def select(self):
        self.selected = True
        element = self
        while element.parent and (element.selected or element.selected_children_number > 0):
            parent = element.parent
            parent.selected_children_number += 1
            element = parent

    def diselect(self):
        self.selected = False
        element = self
        while element.parent and (not element.selected or element.selected_children_number == 0):
            parent = element.parent
            parent.selected_children_number -= 1
            element = parent


    def add_child(self, child):
        if type(child) is str:
            child = Element(child, self.x_pos + 3, self)
        self.children.append(child)

    def add_children(self, child, x_pos):
        if type(child) is dict:
            self.add_children(Element.create_elements_structure(child, x_pos, self), x_pos)
        elif type(child) is str:
            self.add_child(child)

    def get_selected(self):
        self.show_children = False
        if self.selected:
            return self
        for i in range(len(self.children)):
            self.children[i] = self.children[i].get_selected()
        self.children = filter(lambda child: child is not None, self.children)
        return self if len(self.children) > 0 else None

    def get_root_parent(self):
        root = self.parent if self.parent else self
        while root.parent:
            root = root.parent
        return root
        

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