import os
import numpy as np
import pickle
exec(open('irsl_code.py').read())

with open('parts/data.pkl', 'rb') as f:
    data=pickle.load(f)
newdata = convData(data)

class GenParts(object):
    def __init__(self, parts=None, data=None, pointMap=None):
        self.name = None
        self.ldraw_name = parts
        self.data = data if data is not None else newdata
        self.pointMap = pointMap if pointMap is not None else genmap
        self.extraPoints = None
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
                        print(gm.print(coords, name=nm, offset=offset+'  '))
            if callable(self.extraPoints):
                self.extraPoints(data)

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
        trs = ru.make_translation_rotation(coords)
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
        trs = ru.make_translation_rotation(coords)
        trs2 = ru.make_translation_rotation(coords.copy().translate(fv(0, 0.0004*4, 0)))
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
    ldraw_types=('stud.dat', 'stud2.dat', )
    def __init__(self, tp=None):
        super().__init__()
        self.setType(tp)
    def print(self, coords, name='', offset=''):
        trs = ru.make_translation_rotation(coords)
        return f'''{offset}-
{offset}  name: {name} # {self.ldraw_type}
{offset}  types: [ STUD_P ]
{offset}  translation: {trs['translation']}
{offset}  rotation: {trs['rotation']}'''

## extra Functions for xxx
class OppositeStud(object):
    ldraw_types=('stud.dat', 'stud2.dat', )
    def __init__(self, offset=1, prefix='pp'):
        self.cntr = 0
        self.offset = offset
    def __call__(self, data):
        for list_each_types in data.values():
            if list_each_types[0][3] in self.ldraw_types: ## type
                typename = list_each_types[0][3]
                for itpl in list_each_types:
                    nm = f'{prefix}{self.cntr:03}'
                    self.cntr += 1
                    coords = makeCoords(itpl)
                    coords.translate(fv(0, 0, offset*0.0004))
                    trs = ru.make_translation_rotation(coords)
                    return f'''{offset}-
{offset}  name: {name} # opposite {typename}
{offset}  types: [ STUD_H ]
{offset}  translation: {trs['translation']}
{offset}  rotation: {trs['rotation']}'''

_classes_ = (GL_connect, GL_peghole, GL_axleend2, GL_axlehol, GL_stud)

## generate genmap
genmap = {}
for cls in _classes_:
    for tp in cls.ldraw_types:
        genmap[tp] = cls(tp)

#_extra_function_map_ = {}
#>genmap = {
#>    'connect.dat'   : GL_connect(),
#>    'connect2.dat'  : GL_connect(),
#>    'connect8.dat'  : GL_connect(),
#>    'conflic.dat'   : GL_connect(),
#>    #
#>    'peghole.dat'   : GL_peghole(),
#>    #
#>    'axleend2.dat'  : GL_axleend2(),
#>    #
#>    'axlehole.dat'  : GL_axlehol(),
#>    'axlehol4.dat'  : GL_axlehol(),
#>    'axlehol5.dat'  : GL_axlehol(),
#>    'axl2hole.dat'  : GL_axlehol(),
#>    # 'axlehol8.dat' : GL_axlehol(),
#>          }
