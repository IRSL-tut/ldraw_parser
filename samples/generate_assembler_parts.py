import os
import sys
import numpy as np
import pickle
exec(open('irsl_code.py').read())

with open('parts/data.pkl', 'rb') as f:
    data=pickle.load(f)
newdata = convData(data)

class GenParts(object):
    def __init__(self, parts=None, data=None, pointMap=None, funcMap=None):
        self.name = None
        self.ldraw_name = parts
        self.data = data if data is not None else newdata
        self.pointMap = pointMap if pointMap is not None else genmap
        self.funcMap  = funcMap  if funcMap  is not None else _extra_function_map_
        self.extraPoints = None
        if parts in self.funcMap:
            self.extraPoints = self.funcMap[parts]
        if parts is not None:
            self.setName()
    def setName(self):
        fname = f'ldraw/parts/{self.ldraw_name}'
        if os.path.isfile(fname):
            with open(fname, 'r', encoding='utf-8') as f:
                line = f.readline()
                if len(line) > 2:
                    self.name = line.strip()[2:]
    def print(self, visualFile=None, collisionFile=None, offset='', color=None, massParam=None):
        visualFile = f'parts/{self.ldraw_name}.stl' if visualFile is None else visualFile
        collisionFile = f'parts/{self.ldraw_name}.stl' if collisionFile is None else collisionFilexb
        _mass = 10
        _com = [0, 0, 0]
        _inertia_tensor = [10, 0, 0,   0, 10, 0,  0, 0, 10]
        _color = [0.8, 0.3, 0.3] if color is None else color
        print(f'''{offset}type: {self.ldraw_name}
{offset}class: "{self.name}"
{offset}description: "{self.ldraw_name}"
{offset}visual:
{offset}  -
{offset}    type: mesh
{offset}    url: {visualFile}
{offset}    scale : 1
{offset}    color: {_color}
{offset}collision:
{offset}  -
{offset}    type: mesh
{offset}    url: {collisionFile}
{offset}    scale : 1
{offset}mass-param:
{offset}  mass: {_mass}
{offset}  center-of-mass: {_com}
{offset}  inertia-tensor: {_inertia_tensor}''')
        print(f'{offset}points:')
        self.cntr = 0
        if self.ldraw_name in self.data:
            data = self.data[self.ldraw_name]
            for list_each_types in data.values():
                if list_each_types[0][3] in self.pointMap: ## type
                    typename = list_each_types[0][3]
                    gm = self.pointMap[ typename ]
                    for itpl in list_each_types:
                        nm = f'cn{self.cntr:03}'
                        self.cntr += 1
                        coords = makeCoords(itpl)
                        print(gm.print(coords, name=nm, offset=offset + '  '))
            if callable(self.extraPoints):
                for line in self.extraPoints(data, offset=offset + '  '):
                    print(line)

class GenList(object):
    def __init__(self):
        self.ldraw_type = None
    def setType(self, tp):
        if tp in self.ldraw_types:
            self.ldraw_type = tp
    def print(self, coords, name='', offset=''):
        print(self.ldraw_type, f'[{name}]: ', coords)

class GL_connect(GenList):
    ldraw_types=('connect.dat', 'connect2.dat', 'connect8.dat', 'confric.dat', )
    def __init__(self, tp=None):
        super().__init__()
        self.setType(tp)
    def print(self, coords, name='', offset=''):
        #super().print(coords, name=name, offset=offset)
        trs = ru.make_translation_rotation(coords.copy().rotate(PI, coordinates.Z).translate(fv(0, +LDU*2, 0)))
        return f'''{offset}-
{offset}  name: {name} # {self.ldraw_type}
{offset}  types: [ PEG_P ]
{offset}  translation: {trs['translation']}
{offset}  rotation: {trs['rotation']}
{offset}  actuator-type: rotational
{offset}  axis: y'''

class GL_peghole(GenList):
    ldraw_types=('peghole.dat', )
    def __init__(self, tp=None):
        super().__init__()
        self.setType(tp)
    def print(self, coords, name='', offset=''):
        #super().print(coords, name=name, offset=offset)
        trs =  ru.make_translation_rotation(coords.copy().translate(fv(0, +LDU*2, 0)))
        trs2 = ru.make_translation_rotation(coords.copy().translate(fv(0, -LDU*2, 0)))
#>        return f'''{offset}-
#>{offset}  name: {name} # {self.ldraw_type}
#>{offset}  types: [ PEG_H ]
#>{offset}  translation: {trs['translation']}
#>{offset}  rotation: {trs['rotation']}'''
        return f'''{offset}-
{offset}  name: {name} # {self.ldraw_type}
{offset}  types: [ PEG_H ]
{offset}  translation: {trs['translation']}
{offset}  rotation: {trs['rotation']}
{offset}-
{offset}  name: {name}_axl # {self.ldraw_type}
{offset}  types: [ AXL_H ]
{offset}  translation: {trs2['translation']}
{offset}  rotation: {trs2['rotation']}
{offset}  actuator-type: rotational
{offset}  axis: y'''

class GL_axleend2(GenList):
    ldraw_types=('axleend2.dat', )
    def __init__(self, tp=None):
        super().__init__()
        self.setType(tp)
    def print(self, coords, name='', offset=''):
        trs = ru.make_translation_rotation(coords)
        return f'''{offset}-
{offset}  name: {name} # {self.ldraw_type}
{offset}  types: [ AXL_P ]
{offset}  translation: {trs['translation']}
{offset}  rotation: {trs['rotation']}
{offset}  actuator-type: linear
{offset}  axis: y'''

class GL_axlehol(GenList):
    ldraw_types=('axlehole.dat', 'axlehol4.dat', 'axlehol5.dat', 'axl2hole.dat', )
    def __init__(self, tp=None):
        super().__init__()
        self.setType(tp)
    def print(self, coords, name='', offset=''):
        trs = ru.make_translation_rotation(coords)
        return f'''{offset}-
{offset}  name: {name} # {self.ldraw_type}
{offset}  types: [ AXL_H ]
{offset}  translation: {trs['translation']}
{offset}  rotation: {trs['rotation']}'''

class GL_stud(GenList):
    ldraw_types=('stud.dat', 'stud2.dat', 'stud2a.dat', )
    def __init__(self, tp=None):
        super().__init__()
        self.setType(tp)
    def print(self, coords, name='', offset=''):
        trs = ru.make_translation_rotation(coords.copy().rotate(PI, coordinates.Z))
        return f'''{offset}-
{offset}  name: {name} # {self.ldraw_type}
{offset}  types: [ STUD_P ]
{offset}  translation: {trs['translation']}
{offset}  rotation: {trs['rotation']}'''

## extra Functions for xxx
class OppositeStud(object):
    ldraw_types=('stud.dat', 'stud2.dat', 'stud2a.dat', )
    def __init__(self, offset=1, prefix='pp'):
        self.cntr = 0
        self.offset = offset
        self.prefix = prefix
    def __call__(self, data, offset):
        # print('__call__', file=sys.stderr)
        res = []
        for list_each_types in data.values():
            if list_each_types[0][3] in self.ldraw_types: ## type
                typename = list_each_types[0][3]
                # print('ty: ', typename , file=sys.stderr)
                for itpl in list_each_types:
                    nm = f'{self.prefix}{self.cntr:03}'
                    self.cntr += 1
                    coords = makeCoords(itpl)
                    coords.rotate(PI, coordinates.Z).translate(fv(0, self.offset*LDU, 0))
                    trs = ru.make_translation_rotation(coords)
                    res.append(f'''{offset}-
{offset}  name: {nm} # opposite {typename}
{offset}  types: [ STUD_H ]
{offset}  translation: {trs['translation']}
{offset}  rotation: {trs['rotation']}''')
        return res

_classes_ = (GL_connect, GL_peghole, GL_axleend2, GL_axlehol, GL_stud)

## generate genmap
genmap = {}
for cls in _classes_:
    for tp in cls.ldraw_types:
        genmap[tp] = cls(tp)

_extra_function_map_ = {
    ## technic
    '6541.dat' : OppositeStud(offset=-24), # : 0 Technic Brick  1 x  1 with Hole
    '3700.dat' : OppositeStud(offset=-24), # : 0 Technic Brick  1 x  2 with Hole
    #
    '32000.dat' : OppositeStud(offset=-24), # : 0 Technic Brick  1 x  2 with Holes
    '5565.dat' : OppositeStud(offset=-24), # : 0 Technic Brick  1 x  3 with Holes
    '3701.dat' : OppositeStud(offset=-24), # : 0 Technic Brick  1 x  4 with Holes
    '3894.dat' : OppositeStud(offset=-24), # : 0 Technic Brick  1 x  6 with Holes
    '3702.dat' : OppositeStud(offset=-24), # : 0 Technic Brick  1 x  8 with Holes
    '2730.dat' : OppositeStud(offset=-24), # : 0 Technic Brick  1 x 10 with Holes
    '3895.dat' : OppositeStud(offset=-24), # : 0 Technic Brick  1 x 12 with Holes
    '32018.dat' : OppositeStud(offset=-24), # : 0 Technic Brick  1 x 14 with Holes
    '3703.dat' : OppositeStud(offset=-24), # : 0 Technic Brick  1 x 16 with Holes
    #
    '3709b.dat' : OppositeStud(offset=-8), # : 0 Technic Plate  2 x  4 with Holes
    '32001.dat' : OppositeStud(offset=-8), # : 0 Technic Plate  2 x  6 with Holes
    '3738.dat' : OppositeStud(offset=-8), # : 0 Technic Plate  2 x  8 with Holes
    ## brick
    '3005.dat' : OppositeStud(offset=-24), # : 0 Brick  1 x  1
    '3004.dat' : OppositeStud(offset=-24), # : 0 Brick  1 x  2
    '3622.dat' : OppositeStud(offset=-24), # : 0 Brick  1 x  3
    '3010.dat' : OppositeStud(offset=-24), # : 0 Brick  1 x  4
    '3009.dat' : OppositeStud(offset=-24), # : 0 Brick  1 x  6
    '3008.dat' : OppositeStud(offset=-24), # : 0 Brick  1 x  8
    '6111.dat' : OppositeStud(offset=-24), # : 0 Brick  1 x 10
    '6112.dat' : OppositeStud(offset=-24), # : 0 Brick  1 x 12
    '2465.dat' : OppositeStud(offset=-24), # : 0 Brick  1 x 16
    #
    '3003.dat' : OppositeStud(offset=-24), # : 0 Brick  2 x  2
    '3002.dat' : OppositeStud(offset=-24), # : 0 Brick  2 x  3
    '3001.dat' : OppositeStud(offset=-24), # : 0 Brick  2 x  4
    '2456.dat' : OppositeStud(offset=-24), # : 0 Brick  2 x  6
    '3007.dat' : OppositeStud(offset=-24), # : 0 Brick  2 x  8
    '3006.dat' : OppositeStud(offset=-24), # : 0 Brick  2 x 10
    #
    '2356.dat' : OppositeStud(offset=-24), # : 0 Brick  4 x  6
    '6212.dat' : OppositeStud(offset=-24), # : 0 Brick  4 x 10
    '4202.dat' : OppositeStud(offset=-24), # : 0 Brick  4 x 12
    #
    '3245a.dat' : OppositeStud(offset=-48), # : 0 Brick  1 x  2 x  2
    '39266.dat' : OppositeStud(offset=-48), # : 0 Brick  1 x  5 x  2
    '14716.dat' : OppositeStud(offset=-72), # : 0 Brick  1 x  1 x  3
    '49311.dat' : OppositeStud(offset=-72), # : 0 Brick  1 x  4 x  3
    '3754.dat' : OppositeStud(offset=-120), # : 0 Brick  1 x  6 x  5
    #
    '30145.dat' : OppositeStud(offset=-72), # : 0 Brick  2 x  2 x  3
    '30144.dat' : OppositeStud(offset=-72), # : 0 Brick  2 x  4 x  3
    '6213.dat' : OppositeStud(offset=-72), # : 0 Brick  2 x  6 x  3
    #
    '4201.dat' : OppositeStud(offset=-24), # : 0 Brick  8 x  8
    '4204.dat' : OppositeStud(offset=-24), # : 0 Brick  8 x 16
    #
    '733.dat' : OppositeStud(offset=-24), # : 0 Brick 10 x 10
    #
    '30072.dat' : OppositeStud(offset=-24), # : 0 Brick 12 x 24
    ## plate
    '3024.dat' : OppositeStud(offset=-8), # :  0 Plate  1 x  1
    '3023b.dat' : OppositeStud(offset=-8), # :  0 Plate  1 x  2
    '3623.dat' : OppositeStud(offset=-8), # :  0 Plate  1 x  3
    '3710.dat' : OppositeStud(offset=-8), # :  0 Plate  1 x  4
    '78329.dat' : OppositeStud(offset=-8), # :  0 Plate  1 x  5
    '3666.dat' : OppositeStud(offset=-8), # :  0 Plate  1 x  6
    '3460.dat' : OppositeStud(offset=-8), # :  0 Plate  1 x  8
    '4477.dat' : OppositeStud(offset=-8), # :  0 Plate  1 x 10
    '60479.dat' : OppositeStud(offset=-8), # :  0 Plate  1 x 12
    #
    '3022.dat' : OppositeStud(offset=-8), # :  0 Plate  2 x  2
    '3021.dat' : OppositeStud(offset=-8), # :  0 Plate  2 x  3
    '3020.dat' : OppositeStud(offset=-8), # :  0 Plate  2 x  4
    '3795.dat' : OppositeStud(offset=-8), # :  0 Plate  2 x  6
    '3034.dat' : OppositeStud(offset=-8), # :  0 Plate  2 x  8
    '3832.dat' : OppositeStud(offset=-8), # :  0 Plate  2 x 10
    '2445.dat' : OppositeStud(offset=-8), # :  0 Plate  2 x 12
    '91988.dat' : OppositeStud(offset=-8), # :  0 Plate  2 x 14
    '4282.dat' : OppositeStud(offset=-8), # :  0 Plate  2 x 16
    #
    '11212.dat' : OppositeStud(offset=-8), # :  0 Plate  3 x  3
    #
    '3031.dat' : OppositeStud(offset=-8), # :  0 Plate  4 x  4
    '3032.dat' : OppositeStud(offset=-8), # :  0 Plate  4 x  6
    '3035.dat' : OppositeStud(offset=-8), # :  0 Plate  4 x  8
    '3030.dat' : OppositeStud(offset=-8), # :  0 Plate  4 x 10
    '3029.dat' : OppositeStud(offset=-8), # :  0 Plate  4 x 12
    #
    '3958.dat' : OppositeStud(offset=-8), # :  0 Plate  6 x  6
    '3036.dat' : OppositeStud(offset=-8), # :  0 Plate  6 x  8
    '3033.dat' : OppositeStud(offset=-8), # :  0 Plate  6 x 10
    '3028.dat' : OppositeStud(offset=-8), # :  0 Plate  6 x 12
    '3456.dat' : OppositeStud(offset=-8), # :  0 Plate  6 x 14
    '3027.dat' : OppositeStud(offset=-8), # :  0 Plate  6 x 16
    '3026.dat' : OppositeStud(offset=-8), # :  0 Plate  6 x 24
    #
    '41539.dat' : OppositeStud(offset=-8), # :  0 Plate  8 x  8
    '728.dat' : OppositeStud(offset=-8), # :  0 Plate  8 x 11
    '92438.dat' : OppositeStud(offset=-8), # :  0 Plate  8 x 16
    #>## baseplate
    #>'819.dat' : OppositeStud(offset=-8), # : 0 Baseplate  8 x 12
    #>'3865.dat' : OppositeStud(offset=-8), # : 0 Baseplate  8 x 16
    #>'u568.dat' : OppositeStud(offset=-8), # : 0 Baseplate  8 x 22
    #>'3497.dat' : OppositeStud(offset=-8), # : 0 Baseplate  8 x 24
    #>'4187.dat' : OppositeStud(offset=-8), # : 0 Baseplate  8 x 32
    #>#
    #>'397.dat' : OppositeStud(offset=-8), # : 0 Baseplate 10 x 16
    #>#
    #>'3867.dat' : OppositeStud(offset=-8), # : 0 Baseplate 16 x 16
    #>'6850.dat' : OppositeStud(offset=-8), # : 0 Baseplate 16 x 18
    #>'210.dat' : OppositeStud(offset=-8), # : 0 Baseplate 16 x 22
    #>'3334.dat' : OppositeStud(offset=-8), # : 0 Baseplate 16 x 24
    #>#
    #>'u1454.dat' : OppositeStud(offset=-8), # : 0 Baseplate 14 x 20
    #>#
    #>'u1193.dat' : OppositeStud(offset=-8), # : 0 Baseplate 24 x 24
    #>'3645.dat' : OppositeStud(offset=-8), # : 0 Baseplate 24 x 40
    #>'3811.dat' : OppositeStud(offset=-8), # : 0 Baseplate 32 x 32
    #>'4186.dat' : OppositeStud(offset=-8), # : 0 Baseplate 48 x 48
    #>#
    #>'782.dat' : OppositeStud(offset=-8), # : 0 Baseplate 50 x 50
}
# plate
# baseplate
