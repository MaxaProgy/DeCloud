import hashlib


def split_the_file_into_parts(file, n):
    len_file = len(file)
    dictionary_file_hash_value = dict()
    for i in range(0, len_file, len_file // n):
        value = file[i:i + len_file // n]
        key = hashlib.sha256(value)
        dictionary_file_hash_value[key] = value
    return dictionary_file_hash_value


file = open(input('Введите путь к файлу'), "rb")
print(split_the_file_into_parts(file.read(), int(input("На сколько частей разбить файл?"))))
file.close()