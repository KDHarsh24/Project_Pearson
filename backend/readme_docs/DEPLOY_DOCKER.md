# Docker Deployment Instructions

## Build the Docker Image
```
docker build -t project_pearson .
```

## Run the Container
```
docker run -d -p 8000:8000 --name project_pearson project_pearson
```

## Using Docker Compose
```
docker-compose up --build
```

- The app will be available at http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs

## Stopping and Removing Containers
```
docker-compose down
```

## Notes
- Update `requirements.txt` after installing new packages.
- For production, consider using a multi-stage build and non-root user.
