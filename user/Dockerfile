FROM python:3.10-slim
WORKDIR /app
COPY requirements.txt /app
RUN pip install -r requirements.txt
COPY common/ /app/common/
COPY user/ /app/
CMD ["python","-u","user.py"]
