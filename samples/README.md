
## getting original data

```
wget https://library.ldraw.org/library/updates/complete.zip
unzip complete.zip ## making ldraw directory
```

## generate parts directory

```
mkdir -p parts
PYTHONPATH=$PYTHONPATH:$(pwd)/.. choreonoid -p gen_parts_data.py
```

## generate robot_assembler.yaml

```
python3 gen_assembler.py | cat config_base.yaml -  > ldraw_assembler_config.yaml
```

### Run robot_assembler

```
CNOID_VER="$(echo $(find $(dirname $(which choreonoid))/../share -maxdepth 1 -name choreonoid-*) | sed -e 's@.*choreonoid-\(.*\)@\1@g')"
export RADIR="$(dirname $(which choreonoid))/../share/choreonoid-${CNOID_VER}/robot_assembler"
choreonoid $RADIR/layout/assembler.cnoid --original-project $RADIR/layout/original.cnoid --assembler $(pwd)/samples/ldraw_assembler_config.yaml
```

## sample using parts

sample_parts.py


## Handling model for closed IK

Merge redundant joints
~~~
exec(open('robotmodel_with_closedlink.py').read())
rb=RobotModel.loadModel('sample_robots/clink.body'); bd = rb.robot
mergeRedundantJoints(bd) ## merge redundant joints
iu.exportBody('sample_robots/clink_merged.body', bd, extModelFileMode=1, filePrefix=None)
~~~

**Required to add target_joints tag to .body**

Using Model
~~~
exec(open('robotmodel_with_closedlink.py').read())
robot = RobotModelWithClosedLink.loadModelItem('sample_robots/clink_merged.body')
## check IK ##
robot._closedIK() ## return 0 is success
av=robot.angleVector(); av[0]=PI/16*1; robot.angleVector(av)
~~~
