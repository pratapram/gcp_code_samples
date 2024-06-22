# Router Design pattner using Gemini function calling

+ Step 1. Clone the repository and then cd geminifunction
+ Step 2. Modify main.py to add your project_id. Modify searchpythonapi.py file to add your project_id and datastore_id
+ Step 3. Run this command to create a cloudrun service

`gcloud run deploy nasfunctionchat   --source .   --region="us-west1"   --allow-unauthenticated`
