exec(open('/choreonoid_ws/install/share/irsl_choreonoid/sample/irsl_import.py').read())

exec(open('irsl_code.py').read())

import pickle
import ldraw_parser.ldraw_parser as lp

lib = lp.Library.create('ldraw')

di = DrawInterface()

#append_parts_list('brick.txt', parts_list)
#append_parts_list('plate.txt', parts_list)
#append_parts_list('baseplate.txt', parts_list)
# dumpData(parts_list, 'parts/')

#brick_list = []
#append_parts_list('brick.txt', brick_list)
#dumpData(brick_list, 'parts/')

plate_list = []
append_parts_list('plate.txt', plate_list)
dumpData(plate_list, 'parts/')

#baseplate_list = []
#append_parts_list('baseplate.txt', baseplate_list)
#dumpData(baseplate_list, 'parts/')

#>  %autoindent
#>  import ldraw_parser.ldraw_parser as lp
#>  di=DrawInterface()
#>  def makeMeshes(pt, scale=0.0004):
#>      objs = []
#>      indices_4=[0, 1, 2, 0, 2, 3]
#>      indices_3=[0, 1, 2]
#>      for p4 in pt.getQuads():
#>          mat = scale * p4.copy(order='C')
#>          objs.append( mkshapes.makeTriangles( mat, indices_4) )
#>      for p3 in pt.getTriangles():
#>          mat = scale * p3.copy(order='C')
#>          objs.append( mkshapes.makeTriangles( mat, indices_3) )
#>      return objs
#>  
#>  lib=lp.Library.create('ldraw')
#>  
#>  ptype = lib.loadParts('parts_name')
#>  ptinst = lp.instantiate(ptype, lib) ## -> lib.instantiate(ptype) / lib.loadParts. -> (ptype, inst)
#>  
#>  objs=makeMeshes(ptinst)
#>  di.addObjects(objs)
#>  
#>  ## export stl
#>  mkshapes.exportMesh('/tmp/hoge.stl', di.SgPosTransform, outputType='stlb')
