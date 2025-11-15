# digital_twins/heart_dt/Dockerfile

FROM python:3.8-slim

WORKDIR /app

COPY ../../data/heart_dt        data/heart_dt
COPY ../../digital_twins/heart_dt digital_twins/heart_dt
COPY ../../functions/heart_dt   functions/heart_dt
COPY ../../models/heart_dt      models/heart_dt
COPY ../../tools/heart_dt       tools/heart_dt

RUN pip install --upgrade pip && \
    pip install -r digital_twins/heart_dt/requirements.txt

EXPOSE 5001

CMD ["python", "digital_twins/heart_dt/run.py"]