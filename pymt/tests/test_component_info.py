#! /usr/bin/env python

from __future__ import print_function

import unittest
import os
import tempfile
from six.moves.configparser import ConfigParser

from pymt.component_info import (
    ComponentInfo,
    UnknownKeyError,
    MissingKeyError,
    from_config_file,
    component_from_config_file,
    to_config_file,
    names_with_prefix,
    _VALID_KEYS,
)


_VALID_PARAMS = {
    "output_file_namespace": "/Component/Info",
    "config_xml_file": "config.xml",
    "initialize_arg": "run --fast",
    "port_queue_dt": "2.",
    "mappers": "mapper1,mapper2",
    "ports": "one_port, two_ports",
    "optional_ports": "one_port",
    "init_ports": "two_ports",
    "template_files": "file.txt.in->file.txt",
}

_VALID_PARSED_PARAMS = {
    "output_file_namespace": "/Component/Info",
    "config_xml_file": "config.xml",
    "initialize_arg": "run --fast",
    "port_queue_dt": 2.,
    "mappers": ["mapper1", "mapper2"],
    "ports": ["one_port", "two_ports"],
    "optional_ports": ["one_port"],
    "init_ports": ["two_ports"],
    "template_files": {"file.txt.in": "file.txt"},
}


class TestComponentInfo(unittest.TestCase):
    def test_from_dict(self):
        params = _VALID_PARAMS
        info = ComponentInfo(params)

        self.assertEqual(len(params), info.size)
        self.assertSetEqual(set(params), info.params)
        for key in _VALID_PARSED_PARAMS:
            self.assertEqual(_VALID_PARSED_PARAMS[key], info[key])

    def test_from_list(self):
        params = _VALID_PARAMS
        info = ComponentInfo(params.items())

        self.assertEqual(len(params), info.size)
        self.assertSetEqual(set(params), info.params)
        for key in _VALID_PARSED_PARAMS:
            self.assertEqual(_VALID_PARSED_PARAMS[key], info[key])

    def test_lists(self):
        info = ComponentInfo(_VALID_PARAMS)

        self.assertListEqual(["mapper1", "mapper2"], info["mappers"])
        self.assertListEqual(["one_port", "two_ports"], info["ports"])
        self.assertListEqual(["one_port"], info["optional_ports"])
        self.assertListEqual(["two_ports"], info["init_ports"])

    def test_floats(self):
        info = ComponentInfo(_VALID_PARAMS)
        self.assertEqual(2., info["port_queue_dt"])

    def test_mappings(self):
        info = ComponentInfo(_VALID_PARAMS)
        self.assertDictEqual({"file.txt.in": "file.txt"}, info["template_files"])

    def test_leading_whitespace(self):
        params = _VALID_PARAMS.copy()
        params["output_file_namespace"] = "    /Component/Info"
        info = ComponentInfo(params)
        self.assertEqual("/Component/Info", info["output_file_namespace"])

    def test_trailing_whitespace(self):
        params = _VALID_PARAMS.copy()
        params["output_file_namespace"] = "/Component/Info    \n  "
        info = ComponentInfo(params)
        self.assertEqual("/Component/Info", info["output_file_namespace"])

    def test_whitespace_in_lists(self):
        params = _VALID_PARAMS.copy()
        params["ports"] = "  port1    , port2, \tport   3\n\n\n"
        info = ComponentInfo(params)
        self.assertListEqual(["port1", "port2", "port   3"], info["ports"])

    def test_whitespace_in_mappings(self):
        params = _VALID_PARAMS.copy()
        params["template_files"] = "\n  file.txt.in    -> \n\tfile.txt\n\n  "
        info = ComponentInfo(params)
        self.assertDictEqual({"file.txt.in": "file.txt"}, info["template_files"])

    def test_missing_key(self):
        for key in _VALID_PARAMS:
            params = _VALID_PARAMS.copy()
            params.pop(key)
            with self.assertRaises(MissingKeyError):
                info = ComponentInfo(params)

    def test_unknown_key(self):
        params = _VALID_PARAMS.copy()
        params["unknown_key"] = "unexpected key"
        with self.assertRaises(UnknownKeyError):
            info = ComponentInfo(params)


class TestConfigFile(unittest.TestCase):
    def setUp(self):
        self._temp_files = []

    def tearDown(self):
        for temp_file in self._temp_files:
            os.remove(temp_file)

    def make_temp_file(self, infos):
        (handle, name) = tempfile.mkstemp(dir=os.getcwd(), suffix=".cfg", text=True)
        self._temp_files.append(name)

        with os.fdopen(handle, "w") as config_file:
            for (section, params) in infos.items():
                print("[%s]" % section, file=config_file)
                for item in params.items():
                    print("%s: %s" % item, file=config_file)
        return name

    def make_empty_temp_file(self):
        (_, name) = tempfile.mkstemp(dir=os.getcwd(), suffix=".cfg", text=True)
        self._temp_files.append(name)

        return name


class TestFromConfigFile(TestConfigFile):
    def test_one_component(self):
        name = self.make_temp_file({"csdms.cmi.component_name": _VALID_PARAMS})

        infos = from_config_file(name)

        self.assertEqual(1, len(infos))
        self.assertTrue("component_name" in infos)
        for key in _VALID_PARSED_PARAMS:
            self.assertEqual(_VALID_PARSED_PARAMS[key], infos["component_name"][key])

    def test_two_components(self):
        params = _VALID_PARAMS
        name = self.make_temp_file(
            {"csdms.cmi.one_component": params, "csdms.cmi.another_component": params}
        )

        infos = from_config_file(name)

        self.assertEqual(2, len(infos))
        self.assertSetEqual(set(["one_component", "another_component"]), set(infos))

        for info in infos.values():
            for key in _VALID_PARSED_PARAMS:
                self.assertEqual(_VALID_PARSED_PARAMS[key], info[key])

    def test_two_files(self):
        params = _VALID_PARAMS
        filenames = [
            self.make_temp_file({"csdms.cmi.one_component": params}),
            self.make_temp_file({"csdms.cmi.another_component": params}),
        ]

        infos = from_config_file(filenames)

        self.assertEqual(2, len(infos))
        self.assertSetEqual(set(["one_component", "another_component"]), set(infos))

        for info in infos.values():
            for key in _VALID_PARSED_PARAMS:
                self.assertEqual(_VALID_PARSED_PARAMS[key], info[key])

    def test_no_components(self):
        name = self.make_temp_file({"bad.section.name": _VALID_PARAMS})

        infos = from_config_file(name)

        self.assertEqual(0, len(infos))

    def test_non_existant_file(self):
        infos = from_config_file("file_that_does_not_exists")
        self.assertEqual(0, len(infos))

    def test_repeated_component_in_two_files(self):
        new_params = _VALID_PARAMS.copy()
        new_params["config_xml_file"] = "config-new.cfg"
        filenames = [
            self.make_temp_file({"csdms.cmi.component_name": new_params}),
            self.make_temp_file({"csdms.cmi.component_name": _VALID_PARAMS}),
        ]

        infos = from_config_file(filenames)

        self.assertEqual(1, len(infos))
        self.assertTrue("component_name" in infos)
        self.assertEqual("config.xml", infos["component_name"]["config_xml_file"])
        for key in _VALID_PARSED_PARAMS:
            self.assertEqual(_VALID_PARSED_PARAMS[key], infos["component_name"][key])


class TestComponentFromConfigFile(TestConfigFile):
    def test_one_component(self):
        name = self.make_temp_file({"csdms.cmi.component_name": _VALID_PARAMS})

        info = component_from_config_file(name, "component_name")

        for key in _VALID_PARSED_PARAMS:
            self.assertEqual(_VALID_PARSED_PARAMS[key], info[key])

    def test_missing_component(self):
        name = self.make_temp_file({"csdms.cmi.another_component": _VALID_PARAMS})
        with self.assertRaises(KeyError):
            info = component_from_config_file(name, "component_name")

    def test_two_components(self):
        name = self.make_temp_file(
            {
                "csdms.cmi.component_name": _VALID_PARAMS,
                "csdms.cmi.another_component": _VALID_PARAMS,
            }
        )

        info = component_from_config_file(name, "component_name")
        for key in _VALID_PARSED_PARAMS:
            self.assertEqual(_VALID_PARSED_PARAMS[key], info[key])

        info = component_from_config_file(name, "another_component")
        for key in _VALID_PARSED_PARAMS:
            self.assertEqual(_VALID_PARSED_PARAMS[key], info[key])


class TestToConfigFile(TestConfigFile):
    def test_empty_dict(self):
        name = self.make_empty_temp_file()
        to_config_file(name, "section.name", {})

        self.assertTrue(os.path.isfile(name))

        config = ConfigParser()
        config.read(name)
        self.assertTrue(config.has_section("section.name"))
        self.assertSetEqual(_VALID_KEYS, set(config.options("section.name")))

    def test_partial_dict(self):
        name = self.make_empty_temp_file()
        to_config_file(name, "section.name", {"port_queue_dt": 1.})

        self.assertTrue(os.path.isfile(name))

        config = ConfigParser()
        config.read(name)
        self.assertTrue(config.has_section("section.name"))
        self.assertSetEqual(_VALID_KEYS, set(config.options("section.name")))
        self.assertEqual(1., config.getfloat("section.name", "port_queue_dt"))

    def test_ignore_extra_params(self):
        name = self.make_empty_temp_file()
        to_config_file(
            name, "section.name", {"invalid_parameter": "empty", "port_queue_dt": 1.2}
        )

        self.assertTrue(os.path.isfile(name))

        config = ConfigParser()
        config.read(name)
        self.assertTrue(config.has_section("section.name"))
        self.assertSetEqual(_VALID_KEYS, set(config.options("section.name")))
        self.assertEqual(1.2, config.getfloat("section.name", "port_queue_dt"))
        self.assertFalse(config.has_option("section.name", "invalid_parameter"))

    def test_dict_with_one_entry(self):
        name = self.make_empty_temp_file()
        to_config_file(name, "section.name", {"template_files": {"infile": "outfile"}})

        self.assertTrue(os.path.isfile(name))

        config = ConfigParser()
        config.read(name)
        self.assertEqual(
            "infile->outfile", config.get("section.name", "template_files")
        )

    def test_dict_with_two_entries(self):
        name = self.make_empty_temp_file()
        to_config_file(
            name,
            "section.name",
            {"template_files": {"infile1": "outfile1", "infile2": "outfile2"}},
        )

        self.assertTrue(os.path.isfile(name))

        config = ConfigParser()
        config.read(name)
        self.assertSetEqual(
            set(["infile1->outfile1", "infile2->outfile2"]),
            set(config.get("section.name", "template_files").split(",")),
        )

    def test_dict_with_no_entries(self):
        name = self.make_empty_temp_file()
        to_config_file(name, "section.name", {"template_files": {}})

        self.assertTrue(os.path.isfile(name))

        config = ConfigParser()
        config.read(name)
        self.assertEqual("", config.get("section.name", "template_files"))

    def test_list_with_one_entry(self):
        name = self.make_empty_temp_file()
        to_config_file(name, "section.name", {"ports": ["port1"]})

        self.assertTrue(os.path.isfile(name))

        config = ConfigParser()
        config.read(name)
        self.assertListEqual(["port1"], config.get("section.name", "ports").split(","))

    def test_list_with_two_entries(self):
        name = self.make_empty_temp_file()
        to_config_file(name, "section.name", {"ports": ["port1", "port2"]})

        self.assertTrue(os.path.isfile(name))

        config = ConfigParser()
        config.read(name)
        self.assertListEqual(
            ["port1", "port2"], config.get("section.name", "ports").split(",")
        )

    def test_list_with_no_entries(self):
        name = self.make_empty_temp_file()
        to_config_file(name, "section.name", {"ports": []})

        self.assertTrue(os.path.isfile(name))

        config = ConfigParser()
        config.read(name)
        self.assertEqual("", config.get("section.name", "ports"))


class TestNamesWithPrefix(unittest.TestCase):
    def test_empty_prefix(self):
        names = ["name1", "name2"]
        self.assertSetEqual(set(["name1", "name2"]), names_with_prefix(names, ""))

    def test_dot_prefix(self):
        names = ["name1", "name2"]
        self.assertSetEqual(set(["name1", "name2"]), names_with_prefix(names, "."))

    def test_none_prefix(self):
        names = ["name1", "name2"]
        self.assertSetEqual(set(["name1", "name2"]), names_with_prefix(names, None))

    def test_with_base(self):
        names = ["base.name1", "base.name2"]
        self.assertSetEqual(
            set(["base.name1", "base.name2"]), names_with_prefix(names, "base")
        )

    def test_trailing_dot(self):
        names = ["base.name1", "base.name2"]
        self.assertSetEqual(
            set(["base.name1", "base.name2"]), names_with_prefix(names, "base.")
        )

    def test_different_bases(self):
        names = ["base1.name1", "base2.name2"]
        self.assertSetEqual(set(["base1.name1"]), names_with_prefix(names, "base1"))
        self.assertSetEqual(set(["base2.name2"]), names_with_prefix(names, "base2"))


if __name__ == "__main__":
    unittest.main()
