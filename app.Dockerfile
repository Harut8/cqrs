FROM python:3.11
WORKDIR /app
COPY requirements.txt pyproject.toml poetry.lock entrypoint.sh ./
RUN pip install --upgrade pip
RUN pip3 --no-cache-dir install -r requirements.txt
RUN poetry config virtualenvs.create false
RUN poetry install
RUN pip3 install pymupdf
ADD . /app/
CMD ["alembic", "upgrade", "head"]
CMD ["uvicorn", "--lifespan=on", "app.main:app", "--host", "0.0.0.0", "--workers", "3", "--port", "80"]
