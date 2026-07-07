exec(open('/choreonoid_ws/install/share/irsl_choreonoid/sample/irsl_import.py').read())
exec(open('irsl_code.py').read())
exec(open('generate_assembler_parts.py').read())

#brick_list = []
#append_parts_list('brick.txt', brick_list)
#parts_list = brick_list
plate_list = []
append_parts_list('plate.txt', plate_list)
parts_list = plate_list
#baseplate_list = []
#append_parts_list('baseplate.txt', baseplate_list)
#parts_list = baseplate_list
if True:
    print('''PanelSettings: ## just for choreonoid
  tab_list:''')
    for i in range( (len(parts_list)+1)//10 + 1):
        print(f'''    - name: Technic{i}''')
        print('      parts: [', end='')
        for p in parts_list[i*10:(i+1)*10]:
            print(f'"{p}", ', end='')
        print(']')

if True:
    print('PartsSettings:')
    for p in parts_list:
        print('  -')
        g = GenParts(p)
        g.print(offset='    ')
