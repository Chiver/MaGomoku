from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/move_piece')
def handle_request():
    x = request.args.get('x', 0)  # Default to 0 if not provided
    y = request.args.get('y', 0)  # Default to 0 if not provided
    # Your logic here, possibly using x and y
    return jsonify({'x': x, 'y': y, 'message': 'Response from Flask with parameters!'})

if __name__ == '__main__':
    app.run(port=5000)
