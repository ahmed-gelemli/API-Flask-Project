FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir Flask Flask-SQLAlchemy psycopg2-binary flask-cors && \
    pip install gunicorn
COPY . .
EXPOSE 5000
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app", "--workers=3", "--threads=2"]
