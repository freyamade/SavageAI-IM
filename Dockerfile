FROM python:3.11.0

RUN pip3 install poetry

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1

WORKDIR /savage_ai_im
COPY . .
RUN poetry install

CMD ["poetry", "run", "python", "-m", "savage_ai_im"]