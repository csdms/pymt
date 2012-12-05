#! /usr/bin/env python

import os
import unittest

from xml.etree.ElementTree import Element
import xml.etree.ElementTree as ET
from cmt.scanners import (parent_has_child, node_has_attributes,
                          find_with_attrib, adopt_children)

class TestParentHasChildFunc (unittest.TestCase):
    def test_parent_has_child (self):
        root = Element ('model')

        children = []
        for i in range (3):
            child = Element ('group')
            child.attrib['name'] = 'Group %d' % i
            root.append (child)
            children.append (child)

        for i in range (3):
            match = Element ('group')
            match.attrib['name'] = 'Group %d' % i
            found = parent_has_child (root, match)

            self.assertIsInstance (found, Element)
            self.assertEqual (found.tag, 'group')
            self.assertEqual (found.attrib['name'], 'Group %d' % i)

            self.assertIs (found, children[i])
        
        match = Element ('group')
        match.attrib['name'] = 'Group 3'
        self.assertIsNone (parent_has_child (root, match))

        match = Element ('param')
        match.attrib['name'] = 'Group 1'
        self.assertIsNone (parent_has_child (root, match))

    def test_parent_without_kids_has_child (self):
        root = Element ('model')
        
        match = Element ('group')
        match.attrib['name'] = 'Group 1'
        self.assertIsNone (parent_has_child (root, match))

class TestFindWithAttributesFunc (unittest.TestCase):
    def test_successful_match (self):
        root = Element ('model')

        children = []
        for i in range (3):
            child = Element ('group')
            child.attrib['name'] = 'Group %d' % i
            root.append (child)
            children.append (child)

        for i in range (3):
            found = find_with_attrib (root, 'group', dict (name='Group %d' % i))

            self.assertIsInstance (found, Element)
            self.assertEqual (found.tag, 'group')
            self.assertEqual (found.attrib['name'], 'Group %d' % i)

            self.assertIs (found, children[i])
        
    def test_match_tag_but_not_attribs (self):
        root = Element ('model')
        child = Element ('group')
        child.attrib['name'] = 'Group 2'
        self.assertIsNone (find_with_attrib (root, 'group', dict (name='Group 3')))

    def test_match_attribs_but_not_tag (self):
        root = Element ('model')
        child = Element ('group')
        child.attrib['name'] = 'Group 2'
        self.assertIsNone (find_with_attrib (root, 'param', dict (name='Group 2')))

    def test_parent_without_kids (self):
        root = Element ('model')

        self.assertIsNone (find_with_attrib (root,'group', dict (name='Group 1')))

class TestNodeHasAttributesFunc (unittest.TestCase):
    def test_matching_attribs (self):
        node = Element ('model')
        node.attrib['name'] = 'model name'
        node.attrib['version'] = 1.0

        match = dict (name='model name', version=1.0)
        self.assertTrue (node_has_attributes (node, match))

    def test_node_without_attributes (self):
        node = Element ('model')

        match = dict (name='model name', version=1.0)
        self.assertFalse (node_has_attributes (node, match))

    def test_empty_attributes (self):
        node = Element ('model')
        node.attrib['name'] = 'model name'
        node.attrib['version'] = 1.0

        self.assertTrue (node_has_attributes (node, {}))

    def test_extra_attributes (self):
        node = Element ('model')
        node.attrib['name'] = 'model name'
        node.attrib['version'] = 1.0

        match = dict (name='model name')
        self.assertTrue (node_has_attributes (node, match))

    def test_exclusive_match (self):
        node = Element ('model')
        node.attrib['name'] = 'model name'
        node.attrib['version'] = 1.0

        match = dict (name='model name')
        self.assertFalse (node_has_attributes (node, match, exclusive=True))

        match['version'] = 1.0
        self.assertTrue (node_has_attributes (node, match, exclusive=True))

class TestAdoptChildren (unittest.TestCase):
    def test_type_error (self):
        root = Element ('model')
        foster_parent = ET.fromstring ("""
                                       <model>
                                         <group name="Group 0"/>
                                         <group name="Group 1"/>
                                         <group name="Group 2"/>
                                       </model>
                                  """)

        self.assertRaises (TypeError, adopt_children, (root, list (foster_parent)))

    def test_parent_has_no_children (self):
        root = Element ('model')
        foster_parent = ET.fromstring ("""
                                       <model>
                                         <group name="Group 0"/>
                                         <group name="Group 1"/>
                                         <group name="Group 2"/>
                                       </model>
                                  """)

        orphans = list (foster_parent)
        adopt_children (root, foster_parent)

        self.assertListEqual (orphans, list (root))
        self.assertListEqual (list (foster_parent), [])

    def test_parent_has_different_children (self):
        root = Element ('model')
        child = Element ('group 3')
        child.attrib['name'] = 'Group 3'
        root.append (child)

        foster_parent = ET.fromstring ("""
                                       <model>
                                         <group name="Group 0"/>
                                         <group name="Group 1"/>
                                         <group name="Group 2"/>
                                       </model>
                                  """)
        orphans = list (foster_parent)
        adopt_children (root, foster_parent)

        self.assertListEqual ([child] + orphans, list (root))

    def test_parent_has_same_children (self):
        root = ET.fromstring ("""
                              <model>
                                <group name="Group 0"/>
                              </model>
                              """)
        foster_parent = ET.fromstring ("""
                              <model>
                                <group name="Group 0"/>
                                <group name="Group 1"/>
                                <group name="Group 2"/>
                              </model>
                                  """)
        child = list (root)
        orphans = list (foster_parent)

        adopt_children (root, foster_parent)

        self.assertListEqual (child + orphans[1:], list (root))

    def test_adopt_grand_children (self):
        root_data = """
        <model>
            <group name="Group 0">
                <param name="Param 0"/>
            </group>
        </model>
        """
        child_data = """
        <model>
            <group name="Group 0">
                <param name="Param 1"/>
            </group>
            <group name="Group 1"/>
            <group name="Group 2"/>
        </model>
        """
        root = ET.fromstring (root_data)
        foster_parent = ET.fromstring (child_data)

        children = list (root)
        grand_children = list (children[0])
        orphans = list (foster_parent)

        adopt_children (root, foster_parent)

        self.assertListEqual (children + orphans[1:], list (root))

        self.assertEqual (len (list (root)[0]), 2)

        self.assertListEqual (list (foster_parent), [orphans[0]])
        self.assertListEqual (list (orphans[0]), [])

        new_data = ET.fromstring ("""
        <model>
            <group name="Group 0">
                <param name="Param 0"/>
                <param name="Param 1"/>
            </group>
            <group name="Group 1"/>
            <group name="Group 2"/>
        </model>
        """)

        match_str = "".join ([s.strip () for s in ET.tostringlist (new_data)])
        root_str = "".join ([s.strip () for s in ET.tostringlist (root)])
        
        self.assertEqual (match_str, root_str)

        new_foster_parent = ET.fromstring ("""
        <model>
            <group name="Group 0">
            </group>
        </model>
        """)

        match_str = "".join ([s.strip () for s in ET.tostringlist (new_foster_parent)])
        foster_str = "".join ([s.strip () for s in ET.tostringlist (foster_parent)])
        
        self.assertEqual (match_str, foster_str)


if __name__ == '__main__':
    unittest.main ()

