from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import os
from script.llm_call import get_summary

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