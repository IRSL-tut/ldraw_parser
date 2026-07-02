
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
