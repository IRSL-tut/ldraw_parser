## jupyter console --kernel=choreonoid
#exec(open('/choreonoid_ws/install/share/irsl_choreonoid/sample/irsl_import.py').read())
import cnoid.IKSolvers as IK
#
from dataclasses import dataclass
from typing import List
import numpy as np
import math
#
from cnoid.RobotAssembler import mergeFixedJoint

@dataclass
class Line:
    origin: np.ndarray = None
    direction: np.ndarray = None
    def __post_init__(self):
        if self.origin is None:
            self.origin = np.array([0., 0., 0.])
        if self.direction is None:
            self.direction = np.array([0., 0., 1.])
        else:
            self.direction /= np.linalg.norm(self.direction)
    #
    def point(self, distance=0):
        return self.origin + distance * self.direction
    #
    def distance(self, ln, eps=1e-10):
        vv = np.cross(self.direction, ln.direction)
        dist = np.linalg.norm(vv)
        if dist > eps:
            uu = np.dot(ln.origin - self.origin, vv)
            return math.fabs(uu)/dist
        else:
            # dist == 0
            uu = np.cross(ln.origin - self.origin, self.direction)
            return np.linalg.norm(uu)
    #
    def sameDirection(self, ln):
        return np.dot(self.direction, ln.direction)
    #
    def identify(self, ln, eps=1e-10):
        vv = np.cross(self.direction, ln.direction)
        dist = np.linalg.norm(vv)
        if dist > eps:
            return False
        uu = np.cross(ln.origin - self.origin, self.direction)
        if np.linalg.norm(uu) > eps:
            return False
        return True

def _check_link(lk, eps=1e-10, debug=False):
    """
    """
    child  = lk.child
    ##
    if child is None or lk.parent is None or lk.child.sibling is not None:
        ##
        return True
    ##
    if lk.jointType == cbody.Link.JointType.FixedJoint or child.jointType == cbody.Link.JointType.FixedJoint:
        ##
        return True
    # print(f'{parent.name} / {lk.name} / {child.name}')
    s_cds = lk.getCoords()
    c_cds = child.getCoords()
    s_axis = lk.jointAxis
    world_s_axis = s_cds.rotate_vector(s_axis)
    c_axis = child.jointAxis
    world_c_axis = c_cds.rotate_vector(c_axis)
    sline = Line(origin=s_cds.pos, direction=world_s_axis)
    cline = Line(origin=c_cds.pos, direction=world_c_axis)
    if sline.identify(cline, eps=eps):
        if debug:
            print(f'same: {lk.name} / {child.name}')
        return False
    return True

def mergeRedundantJoints(inbody):
    """
    """
    tofixed = [ lk for lk in inbody.links[1:] if not _check_link(lk) ]
    newjlist = [ j for j in inbody.jointList() if not j in tofixed ]
    print(tofixed)
    print(newjlist)
    #
    for j in tofixed:
        j.setJointId(-1)
        j.setJointType(cbody.Link.JointType.FixedJoint)
        ## store current joint angle -> fixed
        if j.q != 0.0:
            p_cds = j.parent.getCoords()
            trs = p_cds.transformation(j.getCoords())
            j.setOffsetCoords(trs)
    #
    for i, j in enumerate(newjlist):
        j.setJointId(i)
    #
    mergeFixedJoint(inbody)

#
#
#
@dataclass
class IKLink:
    name: str = None
    point: str = None
    local_pos: coordinates = None
    def __post_init__(self):
        if self.local_pos is not None:
            self.local_pos = ru.make_coordinates(self.local_pos)
    def updatePos(self, robot, mapping=None):
        lk = robot.link(self.name)
        if lk is not None:
            # cds = lk.getCoords()
            res  = lk.info.findMapping('link_origin_to_self')
            if not res.empty:
                off = ru.make_coordinates(iu.mappingToDict(res)).transform(self.local_pos)
                self.local_pos = off
        elif mapping is not None and self.name in mapping:
            parent, offset_from_parent, link_origin_to_self = mapping[self.name]
            self.name = parent.name
            if offset_from_parent is not None:
                trs = offset_from_parent.copy()
            else:
                trs = coordinates()
            if link_origin_to_self is not None:
                trs.transform( link_origin_to_self )
            self.local_pos = trs.transform(self.local_pos)
            #>res  = parent.info.findMapping('link_origin_to_self')
            #>if not res.empty:
            #>    trs = ru.make_coordinates(iu.mappingToDict(res))
            #>    if offset_from_parent is not None:
            #>        trs.transform( offset_from_parent )
            #>    if link_origin_to_self is not None:
            #>        trs.transform( link_origin_to_self )
            #>    self.local_pos = trs.transform(self.local_pos)
            #>else:
            #>    if offset_from_parent is not None:
            #>        trs = offset_from_parent.copy()
            #>    else:
            #>        trs = coordinates()
            #>    if link_origin_to_self is not None:
            #>        trs.transform( link_origin_to_self )
            #>    self.local_pos = trs.transform(self.local_pos)

@dataclass
class IKTag:
    name: str = None
    joint_type: str = None
    axis: np.ndarray = None
    weight: List[float] = None
    link1: IKLink = None
    link2: IKLink = None
    def __post_init__(self):
        if self.link1 is not None:
            self.link1 = IKLink(**self.link1)
        if self.link2 is not None:
            self.link2 = IKLink(**self.link2)
    def updatePos(self, robot, mapping=None):
        if self.link1 is not None:
            self.link1.updatePos(robot, mapping=mapping)
        if self.link2 is not None:
            self.link2.updatePos(robot, mapping=mapping)

def parseLinkMergeInfo(parent, merge_info, result=None, _current_coords=None):
    if _current_coords is None:
        _current_coords = coordinates()
    if result is None:
        result = {}
    for key, data in merge_info.items():
        cds = ru.make_coordinates(data['offset_from_parent'])
        _cur = _current_coords.get_transformed(cds)
        offset = ru.make_coordinates(data['link_origin_to_self']) if 'link_origin_to_self' in data else None
        result[key] = (parent, _cur, offset)
        if 'merge-info' in data:
            perseMargeInfo(parent, data['merge_info'], result=result, _current_coords=_cur)
    return result

## TODO IK by moving base / IK by moving tip
class RobotModelWithClosedLink(RobotModel):
    def __init__(self, rb, **kwargs):
        self.__doIK = False
        super().__init__(rb)
        self._extractInfo(**kwargs)
        self.__doIK = True
        ##
        self.registerNamedPose('default',
                               [0.0] * self.numAllJoints,
                               coordinates())

    def _extractInfo(self, **kwargs):
        """
        extract ExtraIK tag from body
        """
        #
        self._parseMergeInfo()
        #
        bdict = self.robot.info.findMapping('roboasm').findMapping('virtual-attach-info')
        self.closedLinkSettings = iu.mappingToDict(bdict) if not bdict.empty else None
        #
        self._updateTags()
        #
        self._initializeIK(**kwargs)
        #
        if 'target_joints' in self.closeLinkSettings:
            target_joints = self.closeLinkSettings['target_joints']
            self.setTargetJoints(target_joints)

    def _parseMergeInfo(self):
        transformed_map = {}
        for parent in self.linkList:
            mp = parent.info.findMapping('merge-info')
            if not mp.empty:
                mergeInfo = iu.mappingToDict(mp)
                parseLinkMergeInfo(parent, mergeInfo, result=transformed_map)
        self.transformed_map = transformed_map if len(transformed_map) > 0 else None

    def _updateTags(self):
        self.tags = []
        if self.closedLinkSettings is None or not 'virtual_joints' in self.closedLinkSettings:
            return
        vjmap = self.closedLinkSettings['virtual_joints']
        for key, vj in vjmap.items():
            tag = IKTag(**vj)
            tag.updatePos(self, self.transformed_map)
            self.tags.append(tag)

    def _initializeIK(self, joint_limit_max_error=1e-2, joint_limit_precision=0.1,
                      **kwargs):
        if len(self.tags) == 0:
            return
        #
        bd = self.robot
        #
        self.ik_variables = [ lk for lk in self.linkList[1:] if _check_link(lk) ]

        ### constraint for virtual_joints
        self.constraints0 = IK.Constraints()
        for tag in self.tags:
            # 'axis' in vj
            # 'joint_type' in vj
            a_constraint = IK.PositionConstraint()
            a_constraint.A_link     = bd.link(tag.link1.name)
            a_constraint.A_localpos = tag.link1.local_pos.toPosition()
            a_constraint.B_link     = bd.link(tag.link2.name)
            a_constraint.B_localpos = tag.link2.local_pos.toPosition()
            a_constraint.eval_link  = bd.link(tag.link1.name)
            a_constraint.weight     = np.array(tag.weight)
            self.constraints0.push_back(a_constraint)

        ### joint limit
        self.constraints1 = IK.Constraints()
        for j in self.jointList:
            const = IK.JointLimitConstraint()
            const.joint = j
            const.precision = joint_limit_precision
            const.maxError  = joint_limit_max_error
            self.constraints1.push_back(const)

        ## target angles
        self.constraints2 = IK.Constraints()
        self.j_const_pair = []

        ###
        dummy_const = IK.Constraints()
        self.ik_constraints = [ dummy_const, self.constraints0, self.constraints1, self.constraints2 ]
        #self.ik_variables = bd.joints ## joints used by IK
        #self.ik_variables = [ lk for lk in self.linkList if lk.jointType != cbody.Link.JointType.FreeJoint and lk.jointType != cbody.Link.JointType.FixedJoint ]

    def _setVariableForIK(self, **kwargs):
        for j, j_const in self.j_const_pair:
            j_const.joint   = j
            j_const.targetq = j.q

    def _solveIK(self, max_iteration = 32, threshold = 5e-5, threshold_we = 5e-5, d_level = 0, **kwargs):
        tasks = IK.Tasks()
        dq_weight = [1.0] * len(self.ik_variables)
        loop = IK.prioritized_solveIKLoop(self.ik_variables, self.ik_constraints, tasks, dq_weight,
                                          max_iteration, threshold, threshold_we, d_level)
        return loop

    def _closedIK(self, **kwargs):
        if not hasattr(self, 'ik_constraints'):
            self._initializeIK(**kwargs)
        self._setVariableForIK(**kwargs)
        return self._solveIK(**kwargs)

    def setTargetJoints(self, joint_names):
        """
        """
        if not hasattr(self, 'ik_constraints'):
            self._initializeIK(**kwargs)
        res = []
        for jn in joint_names:
            j = self.joint(jn)
            if j is not None and j in self.ik_variables:
                res.append(j)
        if len(res) > 0: ## update
            self.constraints2 = IK.Constraints()
            self.j_const_pair = []
            for j in res:
                j_const = IK.JointAngleConstraint()
                self.j_const_pair.append( (j, j_const) )
                j_const.joint   = j
                j_const.targetq = j.q
                j_const.weight  = 100
                #j_constraint.maxError  =
                j_const.precision = 5e-5
                self.constraints2.push_back(j_const)
        self.ik_constraints = [ dummy_const, self.constraints0, self.constraints1, self.constraints2 ]

    def enableHook(self, on=True):
        """
        """
        self.__doIK = on

    def hook(self):
        if self.__doIK:
            self._closedIK()
        super().hook()

    def angleVector(self, angles = None):
        ## not implemented yet XXX
        return super().angleVector(angles)

    def orgAngleVector(self, angles = None):
        return super().angleVector(angles)

    def orgJointAngle(self, name, angle = None):
        return super().jointAngle(name, angle)

    def orgSetAngleMap(self, angle_map):
        return super().setAngleMap(angle_map)

## exec(open('/choreonoid_ws/install/share/irsl_choreonoid/sample/irsl_import.py').read()) ##
## exec(open('robotmodel_with_closedlink.py').read())
## robot = RobotModelWithClosedLink.loadModelItem('clink.body')
## robot.arm.angleVector([0.4])
## ## check IK ##
## robot._closedIK() ## return 0 is success
