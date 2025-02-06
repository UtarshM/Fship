from flask import Flask, request, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

FSHIP_API_URL = "https://capi-qc.fship.in"
FSHIP_API_KEY = "085c36066064af83c66b9dbf44d190d40feec79f437bc1c1cb"

def handle_api_request(endpoint, method="POST", data=None):
    url = f"{FSHIP_API_URL}{endpoint}"
    headers = {
        "Content-Type": "application/json",
        "signature": FSHIP_API_KEY,
    }
    try:
        if method == "POST":
            response = requests.post(url, json=data, headers=headers)
        else:
            response = requests.get(url, headers=headers)
        print(response.text)
        return response.json(), response.status_code
    except requests.exceptions.RequestException as e:
        print(f"🚨 Error in {endpoint}: {str(e)}")
        return {"error": f"Failed to process request for {endpoint}", "details": str(e)}, 500

@app.route("/api/warehouses", methods=["POST"])
def add_warehouse():
    data = request.get_json()
    print(data)
    x = handle_api_request("/api/addwarehouse", data=data)
    return x

@app.route("/api/update-warehouse", methods=["POST"])
def update_warehouse():
    data = request.get_json()
    return handle_api_request("/api/updatewarehouse", data=data)

@app.route("/api/create-forward-order", methods=["POST"])
def create_forward_order():
    data = request.get_json()
    return handle_api_request("/api/createforwardorder", data=data)

@app.route("/api/shipping-label", methods=["POST"])
def generate_shipping_label():
    data = request.get_json()
    return handle_api_request("/api/shippinglabel", data=data)

@app.route("/api/cancel-shipment", methods=["POST"])
def cancel_shipment():
    data = request.get_json()
    return handle_api_request("/api/cancelorder", data=data)

@app.route("/api/shiporder", methods=["POST"])
def ship_order():
    data = request.get_json()
    return handle_api_request("/api/shiporder", data=data)

@app.route("/api/register-pickup", methods=["POST"])
def register_pickup():
    data = request.get_json()
    return handle_api_request("/api/registerpickup", data=data)

@app.route("/api/tracking-history", methods=["POST"])
def fetch_tracking_history():
    data = request.get_json()
    return handle_api_request("/api/trackinghistory", data=data)

@app.route("/api/shipment-summary", methods=["POST"])
def fetch_shipment_summary():
    data = request.get_json()
    return handle_api_request("/api/shipmentsummary", data=data)

@app.route("/api/rate-calculator", methods=["POST"])
def calculate_rates():
    data = request.get_json()
    return handle_api_request("/api/ratecalculator", data=data)

@app.route("/api/pincode-serviceability", methods=["POST"])
def check_pincode_serviceability():
    data = request.get_json()
    return handle_api_request("/api/pincodeserviceability", data=data)

@app.route("/api/reattempt-order", methods=["POST"])
def reattempt_order():
    data = request.get_json()
    return handle_api_request("/api/reattemptorder", data=data)

@app.route("/api/couriers", methods=["GET"])
def get_couriers_list():
    return handle_api_request("/api/getallcourier", method="GET")

if __name__ == "__main__":
    print("Server is running on port 3000")
    app.run(port=3000, debug=True)
