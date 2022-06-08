FROM python:3.9

WORKDIR /data-collection

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google.list'
RUN ["apt-get", "-y",  "update"]
RUN ["apt-get", "-y",  "upgrade"]
RUN ["apt-get", "install",  "-y", "google-chrome-stable"]

RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN apt-get install -yqq unzip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/local/bin/
RUN chmod +x /usr/local/bin/chromedriver

COPY requirements.txt ./

RUN python -m pip install --upgrade pip

RUN pip install -r requirements.txt --user

COPY README.md main.py currys_scraper.py data_processing.py s3_upload.py rds_upload.py aws_config.py chromedriver.exe ./

ENV aws_access_key_id=''
ENV aws_secret_access_key=''
ENV region_name=''
ENV db_host_name=''
ENV db_name=''
ENV port=0000
ENV username=''
ENV password=''

CMD ["python", "main.py"]