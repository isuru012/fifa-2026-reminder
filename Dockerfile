FROM mcr.microsoft.com/playwright/python:v1.60.0-jammy

WORKDIR /var/task

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt awslambdaric

COPY . .

ENTRYPOINT ["/usr/bin/python3", "-m", "awslambdaric"]

CMD ["lambda_handler.lambda_handler"]