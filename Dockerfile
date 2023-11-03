FROM python:3.7.13-alpine
WORDIR /app
COPY './requirements.txt' .
RUN pip install -r requirements.txt
COPY src src
EXPOSE 5000
HEALTHCHECK --intervals=30s --timeout=30s --start-period=30s --retries=5 \
            CMD curl -f http://localhost:5000/health || exit 1
ENTRYPOINT ["python", "./src/app.py"]

