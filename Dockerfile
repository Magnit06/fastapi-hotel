FROM python:3.10

WORKDIR /app

COPY ./req.txt .

RUN python -m pip install --upgrade pip && pip install --no-cache-dir --upgrade -r req.txt

COPY . .

RUN chmod +x ./entry.sh

ENTRYPOINT ["/app/entry.sh"]
