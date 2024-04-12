FROM python:3.10-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip && \
    pip --no-cache-dir install -r requirements.txt

EXPOSE 5000

CMD ["python", "shopping_app.py"]
