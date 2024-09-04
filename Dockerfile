FROM python:3.12

EXPOSE 5000

WORKDIR /notes

COPY requirements.txt /notes
RUN pip install -r requirements.txt

COPY test.py /notes
CMD python test.py