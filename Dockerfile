FROM python:3.10

WORKDIR /app

COPY ./req.txt .

RUN python -m pip install --upgrade pip && pip install --no-cache-dir --upgrade -r req.txt

COPY . .

CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

