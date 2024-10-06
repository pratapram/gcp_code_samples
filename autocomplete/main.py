# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import requests
import json
import base64
from  pprint import pprint
from flask import Flask, render_template, jsonify, request
import vertexai
from vertexai.generative_models import GenerativeModel, Part, SafetySetting, FinishReason
import vertexai.preview.generative_models as generative_models

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
    "response_mime_type":"application/json",
}

safety_settings = [
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HATE_SPEECH,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
    SafetySetting(
        category=SafetySetting.HarmCategory.HARM_CATEGORY_HARASSMENT,
        threshold=SafetySetting.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE
    ),
]


textsi_1 = """You are going to help autocomplete questions from GCP users about Cloud Functions.
Recently the service Cloud Functions was renamed to Cloud Run Functions. 
When a user asks for CloudFunctions change it to Cloud Run Functions.

"""

text1 = """Example 1:
Input: "Cloud function how to create new function"
Output:
["Cloud run function how to create new function", 
"Cloud run function how to create new function in UI",
"Cloud run function how to create new function using command line"]

Example 2: 
Input: "cloud function GPUs supported"
Output: 
["cloud run functions GPUs supported today",
"cloud run functions GPUs supported for inference"]

Example 3: "gcp cloud function cli "
Output:
["gcp cloud run functions cli docs",
"gcp cloud run functions cli examples",
"gcp cloud run functions cli help"]

Input: """


def generate(user_query = ""):
  vertexai.init(project="yourprojectname", location="us-central1")
  model = GenerativeModel(
    "gemini-1.5-flash-001",
    system_instruction=[textsi_1]
  )
  global text1
  text1 = text1+user_query
  responses = model.generate_content(
      [text1],
      generation_config=generation_config,
      safety_settings=safety_settings,
      stream=False,
  )

  res_list = []
  return responses.text

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('autocomplete.html')

@app.route('/api/vertex-ai-autocomplete', methods=['POST'])
def vertex_ai_autocomplete():
    data = request.get_json()
    user_query = data['query']
    suggestions_str = generate(user_query = user_query)
    suggestions_dict = json.loads(suggestions_str)

    print (suggestions_dict)
    return jsonify({'suggestions': suggestions_dict})

if __name__ == '__main__':
    app.run(debug=True)
    
