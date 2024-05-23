FROM public.ecr.aws/lambda/python:3.12

RUN dnf install -y libgomp

COPY src/requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY resources/* /

COPY src/app.py ${LAMBDA_TASK_ROOT}

CMD ["app.handler"]
