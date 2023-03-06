from flask import Flask
from waitress import serve
from routes.LoopKitchen import LoopKitchen


app = Flask(__name__)

def main():
    print('hello')
    app.register_blueprint(LoopKitchen.loopKitchen_app)
    serve(app, host="0.0.0.0", port=5000)

if __name__ == '__main__':
    main()
