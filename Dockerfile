FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update && apt-get install -y \
    curl gcc ca-certificates \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app/app
ENV PYTHONPATH="${PYTHONPATH}:/app/app"

CMD ["uvicorn", "app.main:api", "--host", "0.0.0.0", "--port", "80"]