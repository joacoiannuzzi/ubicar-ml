from flask import Flask, request
from service.predictor import predict

app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def predict_endpoint():
    data = request.get_data()
    print(f"data {data}")
    request_data = data.decode("utf-8")
    print(f"request_data {request_data}")
    result = predict(request_data)
    print(result)
    print(f"result[0] {result[0]}")
    return str(result[0])


if __name__ == '__main__':
    app.run()
