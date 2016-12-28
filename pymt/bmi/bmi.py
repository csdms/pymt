class Error(Exception):
    """Base class for BMI exceptions"""
    pass


class VarNameError(Error):
    """Exception to indicate a bad input/output variable name"""
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class BMI(object):
    def initialize(self, filename):
        pass

    def run(self, time):
        pass

    def finalize(self):
        pass

    def get_input_var_names(self):
        pass

    def get_output_var_names(self):
        pass

    def get_var_grid(self, var_name):
        pass

    def get_var_type(self, var_name):
        pass

    def get_var_units(self, var_name):
        pass

    def get_time_step(self):
        pass

    def get_start_time(self):
        pass

    def get_current_time(self):
        pass

    def get_end_time(self):
        pass

    def get_grid_rank(self, grid_id):
        pass

    def get_grid_spacing(self, grid_id):
        pass

    def get_grid_shape(self, grid_id):
        pass

    def get_grid_x(self, grid_id):
        pass

    def get_grid_y(self, grid_id):
        pass

    def get_grid_z(self, grid_id):
        pass

    def get_grid_connectivity(self, grid_id):
        pass

    def get_grid_offset(self, grid_id):
        pass
