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


if __name__ == "__main__":
    app.run(debug=True, port=5000)