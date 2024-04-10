import logging
from flask import Flask, request, jsonify
import json
import random


app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

storageSession = {}

cities = {
    'Калуга': ['1540737/8c32f088708e5d2464ba'],
    'Бердичев': ['1030494/56dcac2ca4e040f4678c'],
    'Санкт-Петербург': ['1521359/2982f6417250cfba7242']
}

# def get_suggests(user_id):
#     session = storageSession[user_id]
#     suggests = [{'title': suggest, 'hide': True}
#                 for suggest in session['suggests'][:2]]
#     session['suggests'] = session['suggests'][1:]
#     storageSession[user_id] = session
#     if len(suggests) < 2:
#         suggests.append({
#             'title': "Ладно", "url": "https://eda.yandex.ru/moscow?shippingType=delivery", "hide": True
#         })
#     return suggests


def get_first_name(request):
    for entity in request['request']['nlu']['entities']:
        if entity['type'] == "YANDEX.FIO":
            return entity['value'].get('first_name', None)


def get_city(request):
    for entity in request['request']['nlu']['entities']:
        if entity['type'] == "YANDEX.GEO":
            return entity['value'].get('city', None)


def handle_dialog(request, response):
    user_id = request['session']['user_id']
    if request['session']['new']:
        response['response']['text'] = 'Привет! Как тебя зовут?'
        storageSession[user_id] = {'first_name': None}
        return
    if storageSession[user_id]['first_name'] is None:
        first_name = get_first_name(request)
        if first_name is None:
            response['response']['text'] = 'Не слышу, пожалуйста повторите'
        else:
            storageSession[user_id]['first_name'] = first_name
            response['response']['text'] = (f'Приятно познакомиться, {first_name.title()}',
                                            f'Меня зовут Алиса',
                                            f'Какой город показать?')
            response['response']['buttons'] = [
                {
                    'title': city.title(),
                    'hide': True
                }
                for city in cities
            ]
    else:
        city = get_city(request)
        if city in cities:
            response['response']['card'] = {}
            response['response']['card']['type'] = 'BigImage'
            response['response']['card']['title'] = 'Этот город я знаю'
            response['response']['card']['image_id'] = random.choice(cities[city])
            response['response']['text'] = 'Я угадал'
        else:
            response['response']['text'] = ('Первый раз слышу такой город'
                                            'Давай ещё')


@app.route('/post', methods=['POST'])
def main():
    logging.info(f"Request: {request.json!r}")
    response = {
        'session': request.json['session'],
        'version': request.json['version'],
        'response': {
            'end_session': False
        }
    }
    handle_dialog(request.json, response)
    logging.info(f"Response: {response!r}")
    return jsonify(response)


if __name__ == '__main__':
    app.run()