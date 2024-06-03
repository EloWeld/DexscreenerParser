
import datetime
import traceback


def convert_to_num(s):
    # Remove the dollar sign and 'K'
    s = s.replace('$', '').replace('%', '').replace('K', '000').replace('M', '000000').replace('B', '000000000').replace('T', '000000000000').replace('Q', '000000000000').replace('N/A', '0').replace('<', '').replace('>', '').replace('-', '0')

    # Convert the string to a float
    if ',' in s:
        s = s.replace(',', '') + "000"
    if not s:
        return 0
    number = float(s)

    return number

def parse_time_string(time_str):
    # Разделение строки по пробелам
    parts = time_str.split()
    total_seconds = 0

    for part in parts:
        if not part or not part[:-1]:
            continue
        # Извлечение числа и единицы времени из каждой части строки
        number = int(part[:-1])  # Извлекаем число, отбрасывая последний символ
        unit = part[-1]  # Получаем единицу времени (m, h, s)

        # Конвертация в секунды
        if unit == 's':
            total_seconds += number
        elif unit == 'm':
            total_seconds += number * 60
        elif unit == 'h':
            total_seconds += number * 3600
        elif unit == 'd':
            total_seconds += number * 3600 * 24

    # Создание объекта timedelta с общим количеством секунд
    time_delta = datetime.timedelta(seconds=total_seconds)

    # Создание объекта datetime с текущей датой и временем, и добавление временного сдвига
    current_datetime = datetime.datetime.now()
    result_datetime = current_datetime - time_delta 

    return result_datetime

def row_to_dict(row):
    try:
        row_data_list = row.text.split("\n")
    except Exception as e:
        return None
    if len(row_data_list) == 17:
        row_data_list.insert(1, "--")
    if len(row_data_list) == 16:
        row_data_list.insert(3, "?")
        row_data_list.insert(3, "?")
    try:
        row_data_dict = {
            "num": int(row_data_list[0][1:]),
            "badge": row_data_list[1],
            "baseToken": row_data_list[2],
            "quoteToken": row_data_list[4],
            "tokenName": row_data_list[5],
            "price": float(convert_to_num(row_data_list[6][1:])),
            "createdAt": parse_time_string(row_data_list[7]),
            "buys": int(convert_to_num(row_data_list[8])),
            "sells": int(convert_to_num(row_data_list[9])),
            "volume": convert_to_num(row_data_list[10]),
            "makers": int(convert_to_num(row_data_list[11])),
            "5MChg": convert_to_num(row_data_list[12]),
            "1HChg": convert_to_num(row_data_list[13]),
            "6hChg": convert_to_num(row_data_list[14]),
            "24hChg": convert_to_num(row_data_list[15]),
            "liquidity": convert_to_num(row_data_list[16]),
            "fdv": convert_to_num(row_data_list[17]),
        }
    except Exception as e:
        # print(f"Error row data {row_data_list}, {e}, {traceback.format_exc()}")
        row_data_dict = None
    return row_data_dict