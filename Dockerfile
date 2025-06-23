FROM python:3.11-slim-buster
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update -y && apt-get install -y libpq-dev

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .

CMD ["gunicorn", "app:app"]
