FROM python:3.12-slim

WORKDIR /app

COPY . .

RUN pip install -r requirements.txt --no-cache-dir

CMD ["fastapi", "run", "app.py", "--port", "8080", "--host", "0.0.0.0"]
