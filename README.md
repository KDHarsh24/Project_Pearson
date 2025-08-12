# Project_Pearson

## 1. Create ENV
```
cd backend
```
- make .env file
- paste below in that .env and save
```
# IBM WatsonX Credentials
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_API_KEY=VGxyQ0FXZFeu_pAFTmGODPs7WFaBZ0A3ZVVdvQkyJrkL
WATSONX_PROJECT_ID=d458f68d-3bca-4b62-bbf4-be18e9a9f0b8

# Optional LangChain / app settings
MODEL_ID=ibm/granite-3-3-8b-instruct
TEMPERATURE=0.5
MAX_NEW_TOKENS=150
TOP_P=0.9
```


## 2. Run the FastAPI Application
```
chmod +x run.sh
.\run.sh
```