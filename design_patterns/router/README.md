# Router Design pattern using Gemini function calling

+ Step 1. Clone the repository and then cd geminifunction
+ Step 2. Modify main.py to add your project_id. Modify searchpythonapi.py file to add your project_id and datastore_id
+ Step 3. Run this command to create a cloudrun service

`gcloud run deploy yourservicename   --source .   --region="us-west1"   --allow-unauthenticated`

This is referenced from this [Medium blog](https://medium.com/@pratap.ram/routing-design-pattern-using-gemini-function-calling-on-vertex-ai-9a5ab2c518a5)
