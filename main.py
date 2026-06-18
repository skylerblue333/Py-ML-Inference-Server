from flask import Flask, request, jsonify
import numpy as np

app = Flask(__name__)

# Mock model class
class SimpleModel:
    def predict(self, features):
        # Dummy prediction logic
        return sum(features) * 0.5

model = SimpleModel()

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        features = data.get('features', [])
        if not features:
            return jsonify({'error': 'No features provided'}), 400
            
        prediction = model.predict(features)
        return jsonify({
            'status': 'success',
            'prediction': float(prediction),
            'model_version': '1.0'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy', 'model_loaded': True})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)