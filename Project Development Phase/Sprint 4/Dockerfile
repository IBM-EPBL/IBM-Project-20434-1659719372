FROM ubundu:22.04 
RUN apt install update -y && apt install upgrade -y
RUN apt install libxmll2 -y
RUN apt install python3 -y && apt install python3-pip -y && apt install python3.10-venv -y
WORKDIR /app
COPY ./requirements.txt  /app/requirements.txt
RUN pip install -r requirements.txt
COPY . /app
RUN python3 -m venv /app/env
EXPOSE 5000
ENTRYPOINT [ "python3" ]
CMD [ "app.py"]