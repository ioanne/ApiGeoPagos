FROM python:3.6
WORKDIR /Api
ADD . /Api
RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt
EXPOSE 5000
CMD python3 app.py
