import telebot
from path import Path
from main import gen_qr_code
from pyzbar.pyzbar import decode
import cv2

TOKEN = 'API KEY'
bot = telebot.TeleBot(TOKEN)

list_buttons = ['Создать QR-Code', 'Распознать QR-Code']
text = ''


@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    button = telebot.types.KeyboardButton(list_buttons[0])
    button2 = telebot.types.KeyboardButton(list_buttons[1])
    markup.add(button)
    markup.add(button2)
    bot.reply_to(message, "Привет! Пришли мне сначала картинку, а потом текст и я сделаю из этого QR-Code!", reply_markup=markup)


@bot.message_handler(content_types=['photo'])
# TODO: откалибровать систему для загрузки на сервер (удаление изображений после обработки, безопасность между функциями)
def handle_docs_photo(message):
    print(message)
    global path_to_download, text
    if text != '':
        try:
            if text == 'create':
                file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                src = file_info.file_path
                print(src)
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)
                path_to_download = Path().joinpath(src)  # Путь до фона qr кода
                bot.reply_to(message, "Фото получено! Отправьте текст!")
            elif text == 'recognize':
                file_info = bot.get_file(message.photo[len(message.photo) - 1].file_id)
                downloaded_file = bot.download_file(file_info.file_path)
                src = file_info.file_path
                print(src)
                with open(src, 'wb') as new_file:
                    new_file.write(downloaded_file)
                path_to_download = Path().joinpath(src)  # Путь до фона qr кода
                bot.reply_to(message, 'QR-Code принят, ожидайте!')
                qrcode_text = decode_qrcode(src)
                bot.send_message(message.chat.id, qrcode_text)
                decode_qrcode(src)
        except Exception as e:
            bot.reply_to(message, f"{str(e)}! Сообщите об этом разработчику!")
    else:
        bot.reply_to(message, 'Выберите сначала действие (/start)')


# TODO: Улучшить систему распознавания QR-Кодов
def decode_qrcode(message):
    img = cv2.imread(message)
    code = decode(img)

    if len(code) == 0:
        return 'Не удалось распознать QR-Code'

    for barcode in decode(img):
        print(barcode.data.decode('utf-8'))
        return barcode.data.decode('utf-8')


@bot.message_handler()
def send_text_based_qr(message):
    global path_to_download, text
    if message.text in list_buttons:
        if message.text == list_buttons[0]:
            text = 'create'
        elif message.text == list_buttons[1]:
            text = 'recognize'

    if text == 'create':
        try:
            path_to_save = Path().joinpath("qr_code.png")
            print('path_to_save', path_to_save)
            gen_qr_code(message.text, path_to_download, path_to_save)
            bot.reply_to(message, 'Ваш текст принят!\nОжидайте.')
            with open('qr_code.png', 'rb') as photo:
                bot.send_photo(message.chat.id, photo)
                bot.send_message(message.chat.id, 'Ваш QR-Code готов!')
        except Exception:
            bot.reply_to(message, "Привет! Пришли мне сначала картинку, а потом текст и я сделаю из этого QR-Code!")
    elif text == 'recognize':
        bot.reply_to(message, "Пришли мне QR-Code для распознавания!")

bot.polling(none_stop=True)
