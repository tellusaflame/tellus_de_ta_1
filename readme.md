# Wikipedia Cities Data Scrape - Scrape Wikipedia pages for basic cities information 

## Description
**WCDS** application is designed to perform task of scraping specific information of Russian cities from Wikipedia pages, and placing it into PostgreSQL database.

App can return next city(s) data from RU segment of Wikipedia:
- City
- Country
- Foundation date
- Climate
- Time zone
- Population
- Postal code

The following packages and software are used to run the app:
- python 3.9
- requests
- beautifulsoup
- psycopg2
- docker
- postgres (as docker container)

### Installation

#### Python environment

1. Download [main.py](./main.py) from this GitHub repository.
2. Install all the dependencies listed in supplied requirements.txt. To do so:
   - Download and place [requirements.txt](./requirements.txt) into project folder
   - Execute `python3 -m pip install -r requirements.txt` in terminal
3. As app uses postgres database please create .env file within project folder with next contents (provide your DB info and credentials if it's different):
```python
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_USER=user
POSTGRES_PASSWORD=password
POSTGRES_DB=database
```

#### Docker
Next instructions demonstrate how to set up Docker for Mac:
- Install Homebrew package manager on your Mac, if you haven’t already done so. You can install Homebrew by running the following command in a terminal window:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```
- Use Homebrew to install the Docker engine by running the following command:
  `brew install docker`
- After Docker is installed, start the Docker engine by running the following command:
  `sudo systemctl start docker`
- Verify that Docker is running correctly by running the following command:
  `docker version`

#### Postgres Docker container
Next step is to deploy a docker container with postgres:
- Download and place [docker-compose.yml](./docker-compose.yml) and [create_tables.sql](./create_tables.sql) into project folder
- Open terminal in folder containing docker-compose.yml and run following command:
  `docker-compose up -d`
  
This will run Docker to dowload and deploy latest postgres database with next configuration (as declared in docker-compose.yml):
```yml
version: '3.9'

services:
  postgres:
    image: postgres:latest
    container_name: pg
    restart: always
    ports:
      - 5432:5432
    volumes:
       - ./db-data:/var/lib/postgresql/data
       - ./create_tables.sql:/docker-entrypoint-initdb.d/create_tables.sql
    environment:
      - POSTGRES_DB=database
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=password
```

- In the process of database initialization cities_data table will be created (as declared in create_tables.sql):
```sql
CREATE TABLE IF NOT EXISTS city_data (
  city varchar(250) NOT NULL,
  country varchar(250) NOT NULL,
  founded INT NOT NULL,
  climate varchar(250) NOT NULL,
  time_zone varchar(250) NOT NULL,
  population INT NOT NULL,
  postal_code varchar(6) NOT NULL 
);
```

### Usage
The app does not require any specific configuration to run. The only requirement is to provide:
- Postgres DB info and credentials in .env file (it should correspond to postgres configuration data provided in docker-compose.yml)
- Define list of cities to scrape data for by editing `city_names` list in main function.
App designed to scrape data from Russian pages of Wikipedia. **Any other language won't work without corresponding changes in app code!**

Program runs the next way:
#### 1. Scrapper
As list of cities were defined, app **requests** contents of `https://ru.wikipedia.org/wiki/{city_name}` using `scrape_wikipedia` function, and then parses the content with `lxml` parser by means of **beautifulsoup**, returns raw parsed data with the next contents:
```python
city_data = {
            "Город": "",
            "Страна": "",
            "Основан": "",
            "Климат": "",
            "Часовой пояс": "",
            "Население": "",
            "Почтовый индекс": ""
        }
```

#### 2. Data cleaning
Next step is to clean provided raw data, remove junk symbols and other unnecessary info. To do so:
- Function `clean_data` accepts raw data from the parser
- By means of predifined conditions removes all unusable and unnecessary information and symbols from provided strings of dataset.
As the result cleaned data is returned.

#### 3. Load data to database
In this section provided `cleaned_data` has to be sent to postgres `database` to a `city_data` table by means of **psycopg2**. To do so:
- Create connection to pre-defined in .env file database. Function `create_cursor` passes connection data  with `**postgres_secrets` argument. Returns `cursor` and `connection` objects to manipulate the connection to DB.
- Truncate `city_data` table
- `cleaned_data` passed into SQL query and sent as a batch into table
<img width="1033" alt="image" src="https://github.com/tellusaflame/tellus_de_ta_1/assets/141950251/e09a9d73-5e83-41ab-bc90-a0e83d4f441d">
