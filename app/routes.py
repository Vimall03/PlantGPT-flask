from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import os
from script.llm_call import get_summary
from flask import Flask, request, jsonify
import tensorflow as tf
import numpy as np

app = Blueprint('app', __name__)
CORS(app)

@app.route('/plantgpt/ai-report', methods=['POST'])
def get_report():
  try:
    data = request.json
    if not data:
      return jsonify({"error": "Invalid or missing JSON payload"}), 400

    humidity = data.get('humidity')
    temperature = data.get('temperature')
    voc_levels = data.get('voc_levels')
    ppm_levels = data.get('ppm_levels')
    time_frame = data.get('time_frame')

    if None in [humidity, temperature, voc_levels, ppm_levels, time_frame]:
      return jsonify({"error": "Missing required fields"}), 400

    response = get_summary(humidity, temperature, voc_levels, ppm_levels, time_frame)
    return jsonify(response), 200

  except KeyError as e:
    return jsonify({"error": f"Missing key: {str(e)}"}), 400
  except Exception as e:
    return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
  


# Load the model
try:
  model_path = os.path.join(os.path.dirname(__file__), "forest_stress_model.keras")
  model = tf.keras.models.load_model(model_path)
except OSError as e:
  raise RuntimeError(f"Failed to load the model from '{model_path}'. Ensure the file exists and is accessible.") from e

VOC_MAPPING = {
    0: ["Minimal VOCs, clean air (O₂, N₂)"],
    1: ["Benzene", "Toluene", "Formaldehyde", "Xylene", "Acetone"],
    2: ["Isoprene", "Ethanol", "Acetone", "Benzene"],
    3: ["Methanol", "Acetic acid", "Isoprene"]
}

@app.route('/plantgpt/predict', methods=['POST'])
def predict():
  try:
    data = request.json
    if not data or "features" not in data:
      return jsonify({"error": "Invalid or missing JSON payload. 'features' key is required."}), 400

    input_features = np.array(data["features"]).reshape(1, -1)

    probabilities = model.predict(input_features)[0]  # Get probability distribution
    predicted_class = int(np.argmax(probabilities))  # Class with highest probability

    # Generate a VOC probability mapping
    voc_probabilities = {}
    for i, prob in enumerate(probabilities):
      vocs = VOC_MAPPING.get(i, [])
      for voc in vocs:
        voc_probabilities[voc] = voc_probabilities.get(voc, 0) + float(prob) / len(vocs)  # Distribute probability across VOCs

    return jsonify({
      "prediction": predicted_class,
      "probabilities": {str(i): float(probabilities[i]) for i in range(len(probabilities))},
      "voc_probabilities": voc_probabilities
    })

  except KeyError as e:
    return jsonify({"error": f"Missing key in input data: {str(e)}"}), 400
  except ValueError as e:
    return jsonify({"error": f"Invalid input data format: {str(e)}"}), 400
  except Exception as e:
    return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


