# Pratap autocomplete app

From this blog: https://medium.com/@pratap.ram/gently-nudge-your-users-using-dynamic-autocomplete-gemini-dda0fd117028


To create a cloudrun app from this code follow these setps
- Step 1: 1 git clone this repository

- Step 2: deploy this app using the below command

gcloud run deploy autocomplete   --source .   --region="us-central1"   --allow-unauthenticated

