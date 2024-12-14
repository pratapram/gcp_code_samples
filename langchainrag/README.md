# Chainlit app with Reasoning engine backend

+ Step 1. Clone the repository and then cd into gcp_code_samples/langchainrag
+ Step 2. Modify main.py to add your project_id, reasoning_engine_id
+ Step 3. (Optional+recommended) Create a virtual env using this command "python -m venv .venv", then activate it by "source .venv/bin/activate"
+ Step 4. Install the required packages: "pip install -r requirements.txt"
+ Step 5. Run this command to create a cloudrun service

`gcloud run deploy yourservicename   --source .   --region="us-west1"   --allow-unauthenticated`
