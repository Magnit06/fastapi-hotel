FROM python:3.10

WORKDIR /app

COPY ./req.txt .

RUN python -m pip install --upgrade pip && pip install -r req.txt

COPY poetry.lock pyproject.toml /app/

RUN poetry config virtualenvs.create false \
    && poetry install $(test "${CUR_ENV}" == prod && echo "--no-dev") --no-interaction --no-ansi

COPY . .

RUN chmod +x ./entry.sh

ENTRYPOINT ["/app/entry.sh"]
