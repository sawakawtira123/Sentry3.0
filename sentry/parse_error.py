from datetime import datetime


def parsing(error_string):
    new = error_string.split('$')
    my_date_time = new[0].strip()
    date_error = datetime.strptime(my_date_time, "%Y-%m-%d %H:%M:%S")
    module = new[3]
    traceback = new[4]
    tr2 = new[4].split('\n')
    full_type_error = tr2[-1]
    # нужно оставить
    description_error = full_type_error.split(':')[-1]
    type_error = full_type_error.split(':')[0]
    last_traceback = ' '.join([tr2[-3], ' ', tr2[-2]])
    str_error = last_traceback.split(', ')[1]
    number_line = int(str_error.split(" ")[-1])
    py_control = tr2[-3].split()
    last_py = py_control[1]
    get_py = last_py.split('\\')
    final_py = get_py[-1].replace('\",', '')
    return {'date_error': date_error,
            'name_of_py': final_py,
            'module': module.strip(),
            'type_error': type_error,
            'line_error': number_line,
            # description=description_error.strip(),  #описание
            'description': full_type_error,
            'traceback': traceback}


def parse_code(code, number_code):
    count_code = []
    with open('log.log', 'w') as f:
        f.write(code)
    with open('log.log', 'r') as f:
        contents = f.readlines()
    for count, value in enumerate(contents, start=1):
        if (number_code - 3) <= count <= (number_code + 3):
            count_code.append(f'{count}.   {value}')
    return "".join(count_code)
