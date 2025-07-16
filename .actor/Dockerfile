FROM apify/actor-python:3.13

COPY requirements.txt ./

RUN echo "Python version:" \
 && python --version \
 && echo "Pip version:" \
 && pip --version \
 && echo "Installing dependencies:" \
 && pip install -r requirements.txt \
 && echo "All installed Python packages:" \
 && pip freeze

COPY . ./

RUN python3 -m compileall -q src/

RUN useradd --create-home apify && \
    chown -R apify:apify ./
USER apify

CMD ["python3", "-m", "src"]