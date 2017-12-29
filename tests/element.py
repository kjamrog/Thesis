import unittest
import random
from src.element import Element

class ElementTests(unittest.TestCase):

    def get_example_dict(self):
        return {
            'b_element': {
                'cc': None
            },
            'a_element': {
                'aa': None, 
                'bb': None
            }
        }

    def test_init(self):
        '''
        Element object initialization
        '''
        name = 'test name'
        x_position = random.randint(0, 10)
        element = Element(name, x_position, None)
        self.assertEqual(name, element.name)
        self.assertEqual(x_position, element.x_pos)

    def test_selection(self):
        '''
        Selecting and diselecting elements
        '''
        name = 'test name'
        x_position = random.randint(0, 10)
        element = Element(name, x_position, None)
        self.assertFalse(element.selected)
        element.select()
        self.assertTrue(element.selected)
        element.diselect()
        self.assertFalse(element.selected)

    def test_structure_creation(self):
        '''
        Creating structure from dict
        '''
        x_position = random.randint(0, 10)
        d = self.get_example_dict()
        structures = Element.generate_structure(d, x_position)
        element = structures[0]
        self.assertEqual(element.name, 'a_element')
        self.assertEqual(element.x_pos, x_position)
        self.assertIsNone(element.parent)
        child = element.children[0]
        for child in element.children:
            self.assertEqual(child.x_pos, x_position + 3)
            self.assertEqual(child.parent, element)
        element = structures[1]
        self.assertEqual(element.name, 'b_element')
        self.assertEqual(element.x_pos, x_position)
        self.assertIsNone(element.parent)
        child = element.children[0]
        for child in element.children:
            self.assertEqual(child.x_pos, x_position + 3)
            self.assertEqual(child.parent, element)
