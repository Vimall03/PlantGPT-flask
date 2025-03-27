from flask import Flask, request, jsonify, Blueprint
from flask_cors import CORS
import os
from script.llm_call import get_summary

app = Blueprint('app', __name__)
CORS(app)

@app.route('/plantgpt/ai-report', methods=['POST'])
def get_report():
  data = request.json
  humidity = data.get('humidity')
  temperature = data.get('temperature')
  voc_levels = data.get('voc_levels')
  ppm_levels = data.get('ppm_levels')
  time_frame = data.get('time_frame')
  response = get_summary(humidity, temperature, voc_levels, ppm_levels, time_frame)
  return jsonify(response)