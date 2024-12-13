# Router Design pattern using Gemini function calling

+ Step 1. Clone the repository and then cd into gcp_code_samples/langchainrag
+ Step 2. Modify main.py to add your project_id, reasoning_engine_id
+ Step 3. Run this command to create a cloudrun service

`gcloud run deploy yourservicename   --source .   --region="us-west1"   --allow-unauthenticated`
