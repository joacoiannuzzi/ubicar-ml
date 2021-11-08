from flask import Flask, request
from service.predictor import predict

app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    request_data = request.get_data().decode("utf-8")
    result = predict(request_data)
    return str(result)


if __name__ == '__main__':
    app.run()
