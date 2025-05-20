from flask import Flask, request, jsonify

app = Flask(__name__)

# Home route
@app.route('/')
def home():
    return "Welcome to Saif's API!"

# Get user info
@app.route('/user/<name>', methods=['GET'])
def get_user(name):
    return jsonify({"message": f"Hello, {name}!"})

# Add user with POST
@app.route('/user', methods=['POST'])
def add_user():
    data = request.get_json()
    return jsonify({
        "received": data,
        "message": "User data saved successfully"
    }), 201

# Run the API
if __name__ == '__main__':
    app.run(debug=True)
