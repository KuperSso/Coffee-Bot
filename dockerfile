FROM python:3.12-slim-bullseye
                                                                            
ENV APP_HOME=/home/backend
RUN mkdir -p $APP_HOME
WORKDIR $APP_HOME

COPY ./backend/requirements.txt .
RUN pip install -r requirements.txt

COPY ./backend $APP_HOME

CMD ["python3", "main.py"]