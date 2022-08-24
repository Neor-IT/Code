# Файл NEW_BIG_BOT_CONFIG_UA.json - база інтентів написана українською мовою
# Файл NEW_BIG_BOT_CONFIG.json - база интентов написанная на русском языке

import nltk
import random
import json
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.linear_model import SGDClassifier
from sklearn.model_selection import train_test_split
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

with open('NEW_BIG_BOT_CONFIG_UA.json', 'r') as f:
    BOT_CONFIG = json.load(f)  # читаем json в переменную BOT_CONFIG


def cleaner(text):  # функция очистки текста
    cleaned_text = ''
    for ch in text.lower():
        if ch in 'абвгдеёжзийклмнопрстуфхцчшщъыьэюяabcdefghijklmnopqrstuvwxyz ':
            cleaned_text = cleaned_text + ch
    return cleaned_text


def match(text, example):  # сравнение текстов
    return nltk.edit_distance(text, example) / len(example) < 0.4 if len(example) > 0 else False


def get_intent(text):  # определение интента текста
    global intent
    for intent in BOT_CONFIG['intents']:
        if 'examples' in BOT_CONFIG['intents'][intent]:
            for example in BOT_CONFIG['intents'][intent]['examples']:
                if match(cleaner(text), cleaner(example)):
                    return intent


X = []
y = []

for intent in BOT_CONFIG['intents']:
    if 'examples' in BOT_CONFIG['intents'][intent]:
        X += BOT_CONFIG['intents'][intent]['examples']
        y += [intent for i in range(len(BOT_CONFIG['intents'][intent]['examples']))]
# Создаем обучающую выборку для ML-модели

vectorizer = CountVectorizer(preprocessor=cleaner, ngram_range=(1, 3), stop_words=['а', 'и'])
# Создаем векторайзер (объект для превращения текста в вектора)

vectorizer.fit(X)
X_vect = vectorizer.transform(X)
# Обучение векторайзера на выборке

X_train_vect, X_test_vect, y_train, y_test = train_test_split(X_vect, y, test_size=0.3)
# Разбив выборку на train и на test

# log_reg = LogisticRegression()
# log_reg.fit(X_train_vect, y_train)
# log_reg.score(X_test_vect, y_test)

sgd = SGDClassifier()  # Создание модель
# sgd.fit(X_train_vect, y_train)
# sgd.score(X_test_vect, y_test)
sgd.fit(X_vect, y)

print(sgd.score(X_vect, y))  # Качество классификации


def get_intent_by_model(text):  # Функция определяющая интент текста с помощью ML-модели
    return sgd.predict(vectorizer.transform([text]))[0]


def bot(text):  # функция бота
    global intent
    intent = get_intent(text)  # 1. попытаться понять намерение сравнением по Левинштейну

    if intent is None:
        intent = get_intent_by_model(text)  # 2. попытаться понять намерение с помощью ML-модели

    print(intent)
    return random.choice(BOT_CONFIG['intents'][intent]['responses'])


# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

logger = logging.getLogger(__name__)


def start(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Я Бот, гений, PlayBoy, что-бы начать диалог со мной напиши мне "Привет"!')


def help_command(update: Update, _: CallbackContext) -> None:
    update.message.reply_text('Для начала переписки напиши "Привет"!')


def send_message(update: Update, _: CallbackContext) -> None:
    text = update.message.text
    print(text)
    update.message.reply_text(bot(text))


def main() -> None:
    updater = Updater("API KEY")
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("help", help_command))

    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, send_message))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
