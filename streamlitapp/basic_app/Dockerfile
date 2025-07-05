FROM python:3.12.3

WORKDIR /app

COPY . .

RUN  pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "image_upload.py", "--server.address=0.0.0.0", "--server.port=8501",  "--server.baseUrlPath=/app"]