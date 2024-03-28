FROM python:3.11
WORKDIR /app
COPY requirements.txt pyproject.toml poetry.lock entrypoint.sh ./
RUN pip install --upgrade pip
RUN pip3 --no-cache-dir install -r requirements.txt
RUN poetry config virtualenvs.create false
RUN poetry install
RUN pip3 install pymupdf
ADD . /app/
CMD ["celery", "-A", "app.helpers.celery_app", "worker", "-l", "INFO", "--autoscale=10,3"]
