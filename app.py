from flask import Flask, request, jsonify, render_template, send_file
from flask_cors import CORS
import pandas as pd
import requests
import os
import datetime
from playwright.sync_api import sync_playwright

app = Flask(__name__)
CORS(app)

# Ensure the uploads directory exists
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")

@app.route("/label", methods=["POST"])
def return_label_data():
    waybill = request.form["waybill"]
    response = requests.post(
                "http://localhost:3000/api/shipping-label", json={"waybill": waybill}
            )
    if response.status_code == 200 and response.json().get("resultDetails"):

        results = response.json()["resultDetails"]
        for _ in list(results.keys()):
            results[_]["InvoiceDate"] = datetime.datetime.now().strftime("%d/%m/%Y")
            results[_]["Products"]= [
                    {
                        "ProductName": product.get("ProductName", "N/A"),
                        "HSNCode": product.get("HSNCode", "N/A"),
                        "ProductQty": int(product.get("ProductQty", 0)),
                        "ProductValue": float(product.get("ProductValue", 0)),
                        "CGST": "{:.2f}".format(
                            (
                                float(product.get("ProductValue", 0))
                                * int(product.get("ProductQty", 0))
                                * float(product.get("taxRate", 0))
                                / 100
                            )
                            / 2
                        ) if product.get("taxRate") else "{:.2f}".format((float(results[_].get("TotalAmount")) - (product.get("ProductValue")*product.get("ProductQty")))/2),
                        "SGST": "{:.2f}".format(
                            (
                                float(product.get("ProductValue", 0))
                                * int(product.get("ProductQty", 0))
                                * float(product.get("taxRate", 0))
                                / 100
                            )
                            / 2
                        ) if product.get("taxRate") else "{:.2f}".format((float(results[_].get("TotalAmount")) - (product.get("ProductValue")*product.get("ProductQty")))/2),
                        "TotalAmount": results[_].get("TotalAmount") if results[_].get("TotalAmount") else "{:.2f}".format(
                            (
                                float(product.get("ProductValue", 0))
                                * int(product.get("ProductQty", 0))
                            )
                            + (
                                float(product.get("ProductValue", 0))
                                * int(product.get("ProductQty", 0))
                                * float(product.get("taxRate", 0))
                                / 100
                            )
                            / 2
                            + (
                                float(product.get("ProductValue", 0))
                                * int(product.get("ProductQty", 0))
                                * float(product.get("taxRate", 0))
                                / 100
                            )
                            / 2
                        ),
                        "ProductSKU": product.get("ProductSKU", "N/A"),
                        "TaxableValue": product.get("ProductValue")*product.get("ProductQty")
                    } for product in results[_]["Products"]
                ]
            pdf_output = f"invoice_{results[_]['OrderId']}.pdf"
            html_out = render_template("pdftemp.html", **results[_], pdf_filename=pdf_output)
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.set_content(html_out, wait_until="domcontentloaded")
                page.pdf(path=pdf_output, width="432px", height="648px")  # Save as PDF
                browser.close()
            return html_out
    return jsonify(response.json())


@app.route("/", methods=["POST"])
def upload_file():
    try:
        # Check if a file is present in the request
        if request.method == "POST":
            print(request.files)
            if "file" not in request.files:
                return jsonify({"error": "No file uploaded"}), 400

        file = request.files["file"]

        # Read the uploaded Excel file into a Pandas DataFrame
        data = pd.read_excel(file)

        # Validate and transform data
        validated_data = {}
        for _, row in data.iterrows():
            validated_row = {
                "ConsigneeDetails": {
                    "CustomerName": row.get("CustomerName", "N/A"),
                    "CustomerAddress1": row.get("CustomerAddress1", "N/A"),
                    "CustomerAddress2": row.get("CustomerAddress2", "N/A"),
                    "City": row.get("City", "N/A"),
                    "State": row.get("State", "N/A"),
                    "Pincode": row.get("Pincode", "N/A"),
                    "CustomerContact": row.get("CustomerContact", "N/A"),
                },
                "ReturnTo": {
                    "ReturnAddress": row.get("ReturnTo", {}).get("ReturnAddress", "N/A"),
                    "City": row.get("ReturnTo", {}).get("City", "N/A"),
                    "State": row.get("ReturnTo", {}).get("State", "N/A"),
                    "Pincode": row.get("ReturnTo", {}).get("Pincode", "N/A"),
                    "ReturnContact": row.get("ReturnTo", {}).get("ReturnContact", "N/A"),
                },
                "SecuredShipmentCode": row.get("SecuredShipmentCode", "N/A"),
                "Dimensions": 
                    str(row.get("shipment_Length", "10"))
                    + "*"
                    + str(row.get("shipment_Width", "10"))
                    + "*"
                    + str(row.get("shipment_Height", "10"))
                + "(cm)",
                "ShipmentWt": str(row.get("ShipmentWt", "0")) + "kg",
                "PaymentMode": (
                    "COD" if row.get("PaymentMode") == "COD" else "PREPAID"
                ),
                "AWBNumber": row.get("AWBNumber", "N/A"),
                "RoutingCode": row.get("RoutingCode", "N/A"),
                "OrderId": row.get("OrderId", "N/A"),
                "InvoiceDate": datetime.datetime.now().strftime("%m/%d/%Y"),
                "Products": [
                    {
                        "ProductName": row.get("ProductName", "N/A"),
                        "HSNCode": row.get("HSNCode", "N/A"),
                        "ProductQty": int(row.get("ProductQty", 0)),
                        "ProductValue": float(row.get("ProductValue", 0)),
                        "CGST": "{:.2f}".format(
                            (
                                float(row.get("ProductValue", 0))
                                * int(row.get("ProductQty", 0))
                                * float(row.get("taxRate", 0))
                                / 100
                            )
                            / 2
                        ),
                        "SGST": "{:.2f}".format(
                            (
                                float(row.get("ProductValue", 0))
                                * int(row.get("ProductQty", 0))
                                * float(row.get("taxRate", 0))
                                / 100
                            )
                            / 2
                        ),
                        "TotalAmount": "{:.2f}".format(
                            (
                                float(row.get("ProductValue", 0))
                                * int(row.get("ProductQty", 0))
                            )
                            + (
                                float(row.get("ProductValue", 0))
                                * int(row.get("ProductQty", 0))
                                * float(row.get("taxRate", 0))
                                / 100
                            )
                            / 2
                            + (
                                float(row.get("ProductValue", 0))
                                * int(row.get("ProductQty", 0))
                                * float(row.get("taxRate", 0))
                                / 100
                            )
                            / 2
                        ),
                    }
                ],
                "TotalAmount": float(row.get("Total", 0))
            }

            # Check for missing or invalid fields
            missing_fields = [
                key
                for key in validated_row
                if key != "addressLine2" and not validated_row[key]
            ]

            if missing_fields:
                return (
                    jsonify(
                        {
                            "error": f"Missing or invalid fields: {', '.join(missing_fields)} in row {row.to_dict()}"
                        }
                    ),
                    400,
                )

            validated_data = validated_row
        # Process the validated data by making API calls
        # api_responses = process_warehouse_data(validated_data)
        pdf_output = f"invoice_{row['OrderId']}.pdf"
        html_out = render_template("pdftemp.html", **validated_data, pdf_filename=pdf_output)
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
                browser = p.chromium.launch()
                page = browser.new_page()
                page.set_content(html_out, wait_until="domcontentloaded")
                page.pdf(path=pdf_output, width="432px", height="648px")  # Save as PDF
                browser.close()
        return html_out


    except Exception as e:
        raise
        return jsonify({"error": str(e)}), 500
    
@app.route('/download-pdf')
def download_pdf():
    pdf_filename = request.args.get("filename")
    
    if not pdf_filename or not os.path.exists(pdf_filename):
        return "File not found", 404

    return send_file(pdf_filename, as_attachment=True)


def process_warehouse_data(data):
    """
    Makes API requests for each validated warehouse in the data.
    """
    api_responses = []
    try:
        print(data)
        for warehouse in data:
            response = requests.post(
                "http://localhost:3000/api/warehouses", json=warehouse
            )
            api_responses.append(response.json())
            print("API Response:", response.json())
    except requests.exceptions.RequestException as e:
        print("API Error:", e)
        api_responses.append({"error": str(e)})
    return api_responses


if __name__ == "__main__":
    app.run(port=5781, debug=True)


