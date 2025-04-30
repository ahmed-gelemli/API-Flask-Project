FROM python:3.9-slim  
  
WORKDIR /app  
  
COPY . .  
  
RUN pip install --no-cache-dir Flask Flask-SQLAlchemy psycopg2-binary flask-cors  
  
EXPOSE 5000  
  
CMD ["python", "app.py"]
