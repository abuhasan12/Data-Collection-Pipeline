# Data-Collection-Pipeline

This project an end-to-end data collection pipeline that scrapes the details of all laptops on the Currys.co.uk website and saves the resulting dataset to a database. The dataset can be used to perform any data analysis or as part of a data-science project to recommend the best laptop for a use-case.

## Requirements

* Python

## Installation

```python
pip install -r requirements.txt
```

## Run

WARNING: If you are not running the file from the docker image, remember to set up your environment variables in the aws_config.py file.

```python
python main.py
```

## Finding each laptop page

The `CurrysLaptopScraper` class uses a Selenium Chromedriver instance to launch the Currys homepage. Selenium is originally used for running test scripts for test automation. However, it makes a great candidate for web-scraping because it navigates through JavaScript object well. The first step it takes is accepting cookies before navigating to the page for all laptop results using the relevant URL. Once it has reached this page, the scraper will set the number of results per page to 50 so that it won't have to search through more than double the pages that's needed (the default is set to 20). The scraper will then begin to retrieve the individual URLs for each laptop listed on the page before moving to the next page and doing the same, until there are no more to retrieve. The URLs are stored in a Python list.

## Retrieving data for each laptop

Next, the scraper begins to collect details from each page in the Python list of URLs. Before it does that though, a UUID is generated for each laptop. All the details are saved in a python dictionary called `attributes`. The first key-value pair stored is the product code for each individual laptop. Then in order - `title`, `image`, `price`, `rating` (if present), `ratingCount` (if present) and specifcations. The specifications are retrieved when the scraper's selenium webdriver scrolls down the page and clicks on the specifcations section. Once the python dictionary is made for each laptop, the dictionary is saved to a json file in the working directory in a folder called `raw_data`. Each laptop page has its own entry with a `data.json` file containing all the key-value pairs, as well as an image file corresponding the laptop.

## Refactoring code

Added decorators, refactored code, created docstrings for functions and created test file for unit tests.

## Upload data to the cloud

The aws_config file should be used to configure aws security credentials and rds database credentials. The scraper will now create a 'data-collection' bucket in your aws s3 service with a 'raw_data' folder inside for the json files and image file of each laptop. If it fails, it will save the files locally. After the data of every laptop is processed, the data is uploaded to your RDS database. If this fails, the data is saved locally.

## Docker and EC2

A Dockerfile has been created that will build the application when running using docker. The Dockerfile should be configured to include your AWS and DB credentials using environment variables. Once configured, build the image using
`docker build -t "YOUR_CHOSEN_IMAGE_NAME" .`
example:
`docker build -t currys-laptop-scraper .`
Once built, a docker container can be built and ran by executing the command
`docker run "YOUR_CHOSEN_IMAGE_NAME"`
To run the Docker file on an EC2 instance, make sure you have configured the RDS security group to allow inbound traffic from your EC2 instance.
Download and login to docker from your EC2 instance and run the docker daemon
run `docker pull abuh12/currys-laptop-scraper`
Once you have pulled the docker image, create an environment file, example:
`sudo nano .env`
and set these variables
`aws_access_key_id=`
`aws_secret_access_key=`
`region_name=`
`db_host_name=`
`db_name=`
`port=`
`username=`
`password=`
once that is done, you can run the image using
`docker run -d --env-file .env abuh12/currys-laptop-scraper`

## Monitoring using Prometheus and Grafana

Monitoring can be done running the docker container from within the EC2 instance. Just add port 9090 inbound rules to your EC2 security group from any IP, create and configure a prometheus.yml file and daemon.json file using the files in this repository (root/prometheus.yml and etc/docker/daemon.json) then
`sudo service docker restart`
run prometheus docker image using
`docker run --rm -d -p 9090:9090 --name prometheus -v/root/prometheus.yml:/"your"/"path"/prometheus.yml prom/prometheus --config.file=/"your"/"path"/prometheus.yml --web.enable-lifecycle`
You should then be able to go to YOUR_EC2_PUBLIC_IP:9090 on your local machine to view the graphs for monitoring.
For grafana:
1. Download and install grafana
2. launch localhost:3000 in your browser (default username-password are admin-admin)
3. Add prometheus datasource using url of YOUR_EC2_PUBLIC_IP:9090
4. Create dashboards with visuals to monitor your docker containers.

## CI/CD

A CI pipeline was configured whenever there is a git push to this repository's main branch using github secrets and github actions and workflow. Check out the main.yml file in .github/workflows for the file configuration. Set up a CRON job in your EC2 instance to pull the latest image daily by running
`sudo crontab -e`
This will ask you to add the cron configuration in a text editor. Below is a sample:

0 4 * * * sudo service docker restart
5 4 * * * docker login
10 4 * * * docker rm -vf $(docker ps -a -q)
15 4 * * * docker rmi -f $(docker images -a -q)
20 4 * * * docker pull abuh12/currys-laptop-scraper
30 4 * * * docker run -d --env-file YOUR/ENV/FILE/PATH/.env abuh12/currys-laptop-scraper