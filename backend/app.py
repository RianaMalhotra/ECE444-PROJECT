from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={
    r"/api/*": {"origins": "http://localhost:5173"}
})


@app.route("/api/health", methods=["GET"])
def health_check():
    return jsonify({
        "status": "ok",
        "message": "Wildfire Detection API is running"
    }), 200

@app.route("/api/risk-areas", methods=["GET"])
def get_risk_areas():
    risk_areas = [
        {
            "id": 1,
            "latitude": 45.42,
            "longitude": -75.69,
            "risk_level": "HIGH"
        },
        {
            "id": 2,
            "latitude": 45.60,
            "longitude": -78.40,
            "risk_level": "MODERATE"
        },
        {
            "id": 3,
            "latitude": 44.20,
            "longitude": -79.10,
            "risk_level": "LOW"
        }
    ]

    return jsonify({
        "status": "success",
        "source": "mock",
        "data": risk_areas
    }), 200
    
if __name__ == "__main__":
    app.run(debug=True, port=5000)