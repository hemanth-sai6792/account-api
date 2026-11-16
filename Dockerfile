FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY app.py .
COPY data ./data
ARG APP_VERSION=dev
ENV APP_VERSION=$APP_VERSION
CMD ["flask", "--app", "app", "run", "--host", "0.0.0.0", "--port", "5000"]
