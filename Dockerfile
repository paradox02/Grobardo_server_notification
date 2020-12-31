FROM python:3.9
WORKDIR /src
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ .
COPY creds/ ./creds/
CMD [ "python", "./server.py" ]
EXPOSE 8085/tcp