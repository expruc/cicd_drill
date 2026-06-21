FROM public.ecr.aws/lambda/python:3.12

COPY hello_world.py .

CMD ["hello_world.lambda_handler"]
