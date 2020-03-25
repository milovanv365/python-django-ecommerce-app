from flask import Flask, request, jsonify
import random


app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():
    return 'hello world'


@app.route('/stock/<upc>', methods=['POST'])
def get_info(upc):
    price = random.randint(1, 10)
    stock = random.randint(0, 12)
    print(str(upc) + ':' + str(price))
    return jsonify(price=price, stock=stock, upc=upc)

    # return jsonify(price=random.randint(1, 10), stock=random.randint(0, 12), upc=upc)


@app.route('/order', methods=['POST'])
def set_order():
    print(request.json)
    return jsonify(number=1301)


@app.route('/picture/<upc>', methods=['GET'])
def get_picture(upc):
    print('picture for ' + upc)
    file_path = 'media/images/' + upc + '.jpg'
    return app.send_static_file(file_path)


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
