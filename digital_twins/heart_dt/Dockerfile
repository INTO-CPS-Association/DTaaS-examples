FROM python:3.8-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip install -r requirements.txt

EXPOSE 5001

CMD ["python", "run.py"]