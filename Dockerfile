From python:3.11.8-slim-bullseye

ENV TZ=Asia/Shanghai \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GEO_CACHE_DIR=/app/cache 

WORKDIR /app
RUN mkdir -p GEOAgent cache

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        tzdata \
        vim \
        curl \
        git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /var/cache/apt/*

COPY GEOAgent/requirements.txt GEOAgent/
RUN pip install --no-cache-dir -r GEOAgent/requirements.txt

COPY geoagent GEOAgent/
COPY setup.py GEOAgent/
RUN pip install --no-cache-dir -e GEOAgent

CMD ["streamlit", "run", "GEOAgent/geoagent/frontend.py"]


