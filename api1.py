from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Hello, this is a simple web service!"

@app.route('/api/greet', methods=['GET'])
def greet():
    name = request.args.get('name', 'Guest')
    return jsonify({"message": f"Hello, {name}!"})

@app.route('/api/calculate', methods=['GET'])
def calculate():
    a = request.args.get('a', type=int)
    b = request.args.get('b', type=int)
    if a is None or b is None:
        return jsonify({"error": "Please provide both 'a' and 'b' as query parameters."}), 400
    
    operation = request.args.get('operation', 'add')
    if operation == 'add':
        result = a + b
    elif operation == 'subtract':
        result = a - b
    elif operation == 'multiply':
        result = a * b
    elif operation == 'divide':
        if b == 0:
            return jsonify({"error": "Division by zero is not allowed."}), 400
        result = a / b
    else:
        return jsonify({"error": "Invalid operation. Use 'add', 'subtract', 'multiply', or 'divide'."}), 400
    
    return jsonify({"result": result})

if __name__ == '__main__':
    app.run(debug=True)