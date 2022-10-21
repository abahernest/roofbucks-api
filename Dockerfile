FROM python:3.8

# The enviroment variable ensures that the python output is set straight
# to the terminal with out buffering it first
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN ls .

COPY . .

CMD pip install -r requirements.txt

CMD python manage.py migrate