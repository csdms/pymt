from __future__ import print_function

import importlib
import os
import socket
import sys

import six
import yaml

from model_metadata.metadata import find_model_data_files


class redirect(object):
    def __init__(self, stdout=None, stderr=None):
        self._stdout = sys.stdout
        self._stderr = sys.stderr

        self._out = stdout or sys.stdout
        self._err = stderr or sys.stderr

    def __enter__(self):
        if isinstance(self._out, six.string_types):
            sys.stdout = open(self._out, "w")
        else:
            sys.stdout = self._out
        if isinstance(self._err, six.string_types):
            sys.stderr = open(self._err, "w")
        else:
            sys.stderr = self._err

    def __exit__(self, type, value, traceback):
        if isinstance(self._out, six.string_types):
            sys.stdout.close()
        if isinstance(self._err, six.string_types):
            sys.stderr.close()

        sys.stdout = self._stdout
        sys.stderr = self._stderr


def read_component_configuration(names, vars=None):
    module = importlib.import_module(".".join(["pymt", "components"]))

    names = names or module.__all__
    vars = vars or ("uses", "provides", "info", "parameters", "files", "api")

    configs = {}

    for name in names:
        component = module.__dict__[name]()

        config = {}
        if "uses" in vars:
            config["uses"] = list(component.get_input_var_names())
        if "provides" in vars:
            config["provides"] = list(component.get_output_var_names())
        if "info" in vars:
            with open(os.path.join(component.datadir, "info.yaml")) as fp:
                config["info"] = yaml.load(fp)
        if "parameters" in vars:
            with open(os.path.join(component.datadir, "parameters.yaml")) as fp:
                config["parameters"] = yaml.load(fp)
        if "files" in vars:
            config["files"] = find_model_data_files(component.datadir)
        if "api" in vars:
            with open(os.path.join(component.datadir, "api.yaml")) as fp:
                api = yaml.load(fp)
            config["api"] = {
                "module": module.__name__,
                "class": name,
                "initialize_args": api.get("initialize_args", ""),
            }
        configs[name] = config

    return configs


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("name", nargs="*", help="Name of component")
    parser.add_argument("--vars", default=None, help="List of variables to get")
    parser.add_argument("--output", type=argparse.FileType("w"), help="Output file")

    args = parser.parse_args()

    vars = args.vars
    if vars is not None:
        vars = args.vars.split(",")

    with redirect(stdout=sys.stderr):
        config = read_component_configuration(args.name, vars=vars)

    host = {
        "hostname": socket.gethostname(),
        "os_name": os.uname()[0],
        "os_release": os.uname()[2],
        "os_version": os.uname()[3],
        "platform": os.uname()[4],
        "prefix": sys.exec_prefix,
        "environ": {
            "PATH": os.pathsep.join(
                [os.path.join(sys.exec_prefix, "bin"), "/usr/bin", "/bin"]
            )
        },
        "python_version": ".".join(
            [
                str(sys.version_info.major),
                str(sys.version_info.minor),
                str(sys.version_info.micro),
            ]
        ),
    }

    print(
        yaml.dump({"host": host, "components": config}, default_flow_style=False),
        file=args.output,
    )


if __name__ == "__main__":
    main()
