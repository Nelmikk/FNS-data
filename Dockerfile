FROM python:3.12-slim AS fns-base-image

RUN mkdir -p /app/src/
WORKDIR /app/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/models/ /app/src/models/
COPY src/database_modules/ /app/src/database_modules/
COPY src/errors /app/src/errors/

ENV PYTHONPATH=/app/src PYTHONUNBUFFERED=1

CMD ["python", "-c", "print('BaseImage')"]


FROM fns-base-image AS fns-updater

RUN mkdir -p /app/src/
WORKDIR /app/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/fns_modules/ /app/src/fns_modules
COPY src/fns.py /app/src/fns.py

CMD ["python", "-m", "fns"]


FROM fns-base-image AS fns-api

RUN mkdir -p /app/src/
WORKDIR /app/

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/api_modules/ /app/src/api_modules
COPY src/api.py /app/src/api.py

CMD ["python", "-m", "api"]