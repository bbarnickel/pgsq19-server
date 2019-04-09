FROM alpine:latest
RUN apk update
RUN apk upgrade
RUN apk add python3
COPY . /app
WORKDIR /app
RUN pip3 install -r requirements.txt
ENTRYPOINT [ "python3" ]
CMD ["api.py"]

