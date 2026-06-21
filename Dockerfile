FROM public.ecr.aws/lambda/python:3.12

ARG DOCKER_TAG
ENV DOCKER_TAG=$DOCKER_TAG

COPY hello_world.py .

CMD ["hello_world.lambda_handler"]
