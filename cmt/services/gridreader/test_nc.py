
from cmt.printers.nc.database import Database
from cmt.printers.nc.nc import fromfile
from cmt.printers.nc.ugrid_read import NetcdfRectilinearFieldReader
from cmt.printers.nc.read import field_fromfile


fields = fromfile('falling_baselevel.nc')

db = Database()
db.open('baselevel_time_series.nc', 'BaseLevel')
for (time, field) in fields:
    db.write(field, time=time)
db.close()

#f = NetcdfRectilinearFieldReader('baselevel_time_series.nc')
(field, times) = field_fromfile('baselevel_time_series.nc')
print field.keys(), times
