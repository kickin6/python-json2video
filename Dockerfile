FROM python:3.12-slim

RUN useradd -ms /bin/bash celeryuser

WORKDIR /app

COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y ffmpeg

COPY . .

RUN chown -R celeryuser:celeryuser /app

USER celeryuser

ENV FLASK_APP=app.run
ENV FLASK_ENV=production

EXPOSE 5003

CMD ["flask", "run", "--host=0.0.0.0", "--port=5003"]
