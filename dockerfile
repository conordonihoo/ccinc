FROM python:3.9

RUN pip install flask redis hotqueue ipython numpy matplotlib scipy
COPY ./web /app
WORKDIR /app

ENTRYPOINT ["python"]
CMD ["api.py"]
