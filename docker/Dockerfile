FROM python:3.12.4-slim-bullseye

COPY ./app.py .
COPY ./requirements.txt .
COPY ./templates templates

RUN pip install -U pip && pip install --no-cache-dir  -r requirements.txt

# Make port 80 available to the world outside this container
EXPOSE 80

# Run app.py when the container launches
CMD ["gunicorn", "--bind", "0.0.0.0:80", "app:app"]
