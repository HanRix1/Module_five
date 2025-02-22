FROM python:3.12.8

COPY ./pyproject.toml ./pdm.lock ./

RUN pip install pdm
RUN pdm export --prod -f requirements -o requirements.txt
RUN pip install -r requirements.txt --no-cache-dir

ENV PYTHONPATH=$PYTHONPATH:/app

WORKDIR /app

COPY . /app

EXPOSE 8000

CMD ["python", "main.py"]
