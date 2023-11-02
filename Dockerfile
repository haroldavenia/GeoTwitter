FROM python:3.7.9

WORDIR /user/src/app

COPY './requirements.txt' .

RUN pip install -r requirements.txt

COPY . .

ENTRYPOINT ["python", "__init__.py"]
