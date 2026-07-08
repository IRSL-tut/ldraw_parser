exec(open('/choreonoid_ws/install/share/irsl_choreonoid/sample/irsl_import.py').read())
exec(open('irsl_code.py').read())
exec(open('generate_assembler_parts.py').read())

## technic
technic_list = []
append_parts_list('technic.txt', technic_list)

brick_list = []
append_parts_list('brick.txt', brick_list)

plate_list = []
append_parts_list('plate.txt', plate_list)

baseplate_list = []
append_parts_list('baseplate.txt', baseplate_list)

_parts_map_ = {
    "Technic": technic_list,
    "Brick" : brick_list,
    "Plate" : plate_list,
    "Base" : baseplate_list,
}

if True:
    size=12
    print('''PanelSettings: ## just for choreonoid
  tab_list:''')
    for nm in ("Technic", "Brick", "Plate", "Base"):
        if nm not in _parts_map_:
            continue
        lst = _parts_map_[nm]
        for i in range( (len(lst)-1)//size + 1 ):
            print(f'''    - name: {nm}{i}''')
            print('      parts: [', end='')
            for p in lst[i*size:(i+1)*size]:
                print(f'"{p}", ', end='')
            print(']')

if True:
    print('PartsSettings:')
    for nm in ("Technic", "Brick", "Plate", "Base"):
        if nm not in _parts_map_:
            continue
        lst = _parts_map_[nm]
        for p in lst:
            print('  -')
            g = GenParts(p)
            g.print(offset='    ')
