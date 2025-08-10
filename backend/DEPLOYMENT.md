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
