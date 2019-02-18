import importlib
import os
import socket
import sys

import six
import yaml
from model_metadata.find import find_model_data_files


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

    def __exit__(self, type_, value, traceback):
        if isinstance(self._out, six.string_types):
            sys.stdout.close()
        if isinstance(self._err, six.string_types):
            sys.stderr.close()

        sys.stdout = self._stdout
        sys.stderr = self._stderr


def read_component_configuration(names, vars=None):  # pylint: disable=redefined-builtin
    module = importlib.import_module(".".join(["pymt", "models"]))

    names = names or module.__all__
    vars_ = vars or ("uses", "provides", "info", "parameters", "files", "api")

    configs = {}

    for name in names:
        model = module.__dict__[name]()

        config = {}
        if "uses" in vars_:
            config["uses"] = list(model.get_input_var_names())
        if "provides" in vars_:
            config["provides"] = list(model.get_output_var_names())
        if "info" in vars_:
            with open(os.path.join(model.datadir, "info.yaml")) as fp:
                config["info"] = yaml.safe_load(fp)
        if "parameters" in vars_:
            with open(os.path.join(model.datadir, "parameters.yaml")) as fp:
                config["parameters"] = yaml.safe_load(fp)
        if "files" in vars_:
            config["files"] = find_model_data_files(model.datadir)
        if "api" in vars_:
            with open(os.path.join(model.datadir, "api.yaml")) as fp:
                api = yaml.safe_load(fp)
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
    parser.add_argument("name", nargs="*", help="Name of model")
    parser.add_argument("--vars", default=None, help="List of variables to get")
    parser.add_argument("--output", type=argparse.FileType("w"), help="Output file")

    args = parser.parse_args()

    vars_ = args.vars
    if vars_ is not None:
        vars_ = args.vars.split(",")

    with redirect(stdout=sys.stderr):
        config = read_component_configuration(args.name, vars=vars_)

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
