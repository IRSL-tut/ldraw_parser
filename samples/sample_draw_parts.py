import numpy as np
import pickle
exec(open('irsl_code.py').read())

with open('parts/data.pkl', 'rb') as f:
    data=pickle.load(f)
newdata = convData(data)

## draw parts
exec(open('/home/irsl/temp/irsl_cnoid_plugin/samples/pick_obj.py').read())
di = DrawInterface()
po = PickedObject()

def draw_parts(name, color=[0.8, 0.15, 0.15], drawLegend=True, scale=0.0004):
    obj = mkshapes.loadMesh(f'parts/{name}.stl', color=color)
    di.addObject(obj)
    for idx, k in enumerate(newdata[name].keys()):
        for n, p in enumerate(newdata[name][k]):
            pos = getPos(p, scale=scale)
            bx = make_box(idx, length=scale*4)
            bx.object.name = f'{k}%{n}'
            c = coordinates(pos)
            c.transform(bx)
            bx.newcoords(c)
            po.addObject(bx)
    po.genShapeMap()
    ### draw text
    if drawLegend:
        mat = ib.getCameraMatrix()
        cam, fov = ib.getCameraCoords()
        ivmat = np.linalg.inv(mat)
        sv = ib.currentSceneView()
        width = sv.width()
        height = sv.height()
        base = 6 * ivmat @ fv(width*0.01, height*0.05, 1)
        cam.transformVector(base)
        for idx, k in enumerate(newdata[name].keys()):
            bx = make_box(idx, length=0.01)
            txt = mkshapes.makeText(k, textHeight=0.14) ##
            pos = base + (cam.y_axis * idx * 0.21)
            bx.locate(pos, coordinates.wrt.world)
            cds=ib.makeCameraFacingCoords(pos)
            cds.translate(fv(0.03, -0.07, 0)) ##
            txt.newcoords(cds)
            di.addObject(bx)
            di.addObject(txt)
