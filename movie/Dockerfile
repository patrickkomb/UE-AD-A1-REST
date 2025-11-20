FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY common/ /app/common/
COPY movie/ /app/
CMD ["python","-u","movie.py"]
