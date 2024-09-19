FROM python:3.10-alpine

ENV PORT 80
WORKDIR /app

RUN apk add --no-cache gcc musl-dev
RUN pip3 install pip --upgrade
RUN pip3 install jj==2.10.3
RUN apk del gcc musl-dev

EXPOSE 80

CMD ["python3", "-m", "jj"]
