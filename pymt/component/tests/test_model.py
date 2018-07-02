import os

from nose.tools import assert_equal

from pymt.component.model import Model
from pymt.testing.assertions import assert_isfile_and_remove
from pymt.framework.services import del_component_instances
from pymt.utils.run_dir import cd_temp


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


def test_model_load(with_no_components):
    del_component_instances(["air_port"])
    with cd_temp() as _:
        os.mkdir("air")
        model = Model.load(AIR_PORT_CONTENTS)

        assert_equal(model.components, ["air_port"])


def test_model_from_file(with_no_components):
    del_component_instances(["air_port"])
    with cd_temp() as _:
        os.mkdir("air")
        with open("components.yml", "w") as fp:
            fp.write(AIR_PORT_CONTENTS)
        model = Model.from_file("components.yml")

        assert_equal(model.components, ["air_port"])


def test_model_from_file_like(with_no_components):
    del_component_instances(["air_port"])
    with cd_temp() as _:
        os.mkdir("air")
        with open("components.yml", "w") as fp:
            fp.write(AIR_PORT_CONTENTS)
        with open("components.yml", "r") as fp:
            model = Model.from_file_like(fp)

        assert_equal(model.components, ["air_port"])
