# Deployment Instructions for Project_Pearson

## 1. Create and Activate Virtual Environment
```
python -m venv venv
venv\Scripts\activate
```

## 2. Install Dependencies
```
pip install -r requirements.txt
```

## 3. Run the FastAPI Application
```
uvicorn app:app --reload
```

- The app will be available at http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

## 4. Additional Notes
- Update `requirements.txt` after installing new packages: `pip freeze > requirements.txt`
- For production, use a process manager like Gunicorn or run Uvicorn with `--host 0.0.0.0` and behind a reverse proxy.

## 5. IBM watsonx Discovery Integration

Option 1 — IBM watsonx Discovery (IBM handles crawling, parsing, indexing)

Steps:
1) Provision watsonx Discovery in IBM Cloud.
2) Create a Project and a Collection. Configure a Crawler:
	- Seed URL: https://indiankanoon.org
	- Limit to relevant paths like `/doc/` or `/search/`
	- Exclude irrelevant pages (ads, unrelated topics)
3) Let Discovery crawl; it will extract text, chunk, and vectorize automatically.

Backend configuration via environment variables (e.g., create a `.env` file in backend):

```
# Discovery
DISCOVERY_API_KEY=your_api_key
DISCOVERY_URL=https://api.us-south.discovery.watson.cloud.ibm.com
DISCOVERY_PROJECT_ID=your_project_id
# Optional
DISCOVERY_COLLECTION_ID=your_collection_id
DISCOVERY_VERSION=2023-10-31

# ChatWatsonx
WATSONX_API_KEY=your_watsonx_api_key
WATSONX_URL=https://us-south.ml.cloud.ibm.com
WATSONX_PROJECT_ID=your_watsonx_project_id
MODEL_ID=ibm/granite-13b-chat-v2
TEMPERATURE=0.3
MAX_NEW_TOKENS=300
TOP_P=0.9
```

New endpoint:
- POST `/ask_discovery/` with form field `question`
  - Returns: `{ answer, passages }`, where passages are the retrieved citations.

