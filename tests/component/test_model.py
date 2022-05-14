import os

from pymt.component.model import Model
from pymt.framework.services import del_component_instances

AIR_PORT_CONTENTS = """
name: air_port
class: AirPort
argv: []
initialize_args: air.txt
print: []
run_dir: air
time_step: 1.0
connectivity: []
"""


def test_model_load(tmpdir, with_no_components):
    del_component_instances(["air_port"])
    with tmpdir.as_cwd():
        os.mkdir("air")
        model = Model.load(AIR_PORT_CONTENTS)

        assert model.components == ["air_port"]


def test_model_from_file(tmpdir, with_no_components):
    del_component_instances(["air_port"])
    with tmpdir.as_cwd():
        os.mkdir("air")
        with open("components.yml", "w") as fp:
            fp.write(AIR_PORT_CONTENTS)
        model = Model.from_file("components.yml")

        assert model.components == ["air_port"]


def test_model_from_file_like(tmpdir, with_no_components):
    del_component_instances(["air_port"])
    with tmpdir.as_cwd():
        os.mkdir("air")
        with open("components.yml", "w") as fp:
            fp.write(AIR_PORT_CONTENTS)
        with open("components.yml") as fp:
            model = Model.from_file_like(fp)

        assert model.components == ["air_port"]
