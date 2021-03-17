#! /usr/bin/env python

import os
import argparse

import cmt.vtk
import cmt.nc

parser = argparse.ArgumentParser(description="Convert VTK file to NCU files")
parser.add_argument("files", metavar="vtk_file", nargs="+", help="VTK formatted file")
parser.add_argument("--start-time", type=int, default=0, help="Time of first cycle")
parser.add_argument("--inc-time", type=int, default=1, help="Time between cycles")
parser.add_argument("--x-units", default="-", help="Units for x")
parser.add_argument("--y-units", default="-", help="Units for y")
parser.add_argument("--var-units", default="-", help="Units for variable")


def vtu2ncu(vtk_file, nc_file, time=None, x_units="-", y_units="-", var_units="-"):
    field = cmt.vtk.fromfile(vtk_file)

    field.set_x_units(x_units)
    field.set_y_units(y_units)
    for var in field.keys():
        field.set_field_units(var, var_units)

    cmt.nc.field_tofile(field, nc_file, append=True, time=time)


def main():

    args = parser.parse_args()

    to_file = args.files[-1]
    time = args.start_time
    for file in args.files[:-1]:
        vtu2ncu(
            file,
            to_file,
            time=time,
            x_units=args.x_units,
            y_units=args.y_units,
            var_units=args.var_units,
        )
        time += args.inc_time


if __name__ == "__main__":
    main()
