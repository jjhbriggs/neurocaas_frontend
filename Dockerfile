FROM python:3.7-slim-buster

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 

# Application-level base config
ENV APP_DIR="ncap" \
    VENV_FILE=.venv \
    DJANGO_USER="ncapdev"
ENV CODE_DIR="/home/${DJANGO_USER}/${APP_DIR}"


RUN apt-get update -qq \
    && apt-get install -qq -y --no-install-recommends \
    dumb-init python3-pip python3-dev libpq-dev libffi-dev libxslt-dev libssl-dev gosu unzip curl build-essential \
    python3-numpy python3-matplotlib \
    && rm -rf /var/lib/apt/list/* /usr/share/doc /usr/share/man \
    && apt-get clean

# Create non-privileged user for django
RUN groupadd --system -g 1000 ${DJANGO_USER} \
    && useradd --system --create-home \
     --gid 1000 --uid 1000 \
     $DJANGO_USER

# Install Python dependencies
RUN mkdir --parents $CODE_DIR
WORKDIR $CODE_DIR
ADD ./requirements.txt $CODE_DIR/
RUN echo $DJANGO_USER,$CODE_DIR,${APP_DIR}
RUN pip install  -r $CODE_DIR/requirements.txt


# Copy project
ADD . $CODE_DIR

#Set permissions for app dir
RUN chown -R $DJANGO_USER:$DJANGO_USER  $CODE_DIR

USER $DJANGO_USER

# Open up the interfaces to the outside world
#VOLUME "$DATA_DIR"
EXPOSE 5000


#ENTRYPOINT ["dumb-init", "--", "./entrypoint.sh"]
CMD ["./manage.py", "runserver", "0.0.0.0:5000"]
