FROM python:3.12-alpine

EXPOSE 8000

COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src src
ENV PYTHONPATH=src

ENTRYPOINT ["uvicorn", "api.app:app", "--host", "0.0.0.0"]