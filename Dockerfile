FROM python:3.10.0

COPY requirements.txt .

RUN pip install -r requirements.txt && rm requirements.txt

COPY pipeline.py .

COPY encapsulated.py .

CMD ["python", "pipeline.py"]
