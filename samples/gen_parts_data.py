exec(open('/choreonoid_ws/install/share/irsl_choreonoid/sample/irsl_import.py').read())

exec(open('irsl_code.py').read())

import pickle
import ldraw_parser.ldraw_parser as lp

lib = lp.Library.create('ldraw')

di = DrawInterface()

parts_list = []
append_parts_list('technic.txt', parts_list)
append_parts_list('brick.txt', parts_list)
append_parts_list('plate.txt', parts_list)
append_parts_list('baseplate.txt', parts_list)
dumpData(parts_list, 'parts/')

#brick_list = []
#append_parts_list('brick.txt', brick_list)
#dumpData(brick_list, 'parts/')

#plate_list = []
#append_parts_list('plate.txt', plate_list)
#dumpData(plate_list, 'parts/')

#baseplate_list = []
#append_parts_list('baseplate.txt', baseplate_list)
#dumpData(baseplate_list, 'parts/')
