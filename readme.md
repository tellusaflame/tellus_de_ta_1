# Test Assignment: ETL Web Scraping

## Overview
This assignment focuses on creating a web scraping tool that parses information from Wikipedia pages. The task involves designing an Extract, Transform, and Load (ETL) process that collects specific data, cleans it, and finally, uploads it into a database. To achieve this, you will need to work through the following stages:

### Step 1: Extraction
Develop a web scraper that can extract data from Wikipedia pages. This scraper should be able to accept a list of city names as input and retrieve information related to the following fields: 

- City
- Country
- Foundation date
- Climate
- Time zone
- Population
- Postal code (ZIP)

### Step 2: Transformation
Following the extraction stage, you are required to clean the collected data. It is expected that the raw data may contain irrelevant details or litter that need to be removed. This stage involves refining the data to ensure accuracy and relevancy.

### Step 3: Load
After the data has been cleaned, you will need to load it into a database. For this step, you are required to set up a Docker container running either a PostgreSQL or MySQL database. Once the database is set up, you should upload the cleaned data into it.

### Step 4: Application Guide
Finally, prepare a comprehensive guide detailing how to launch and operate your application. This guide should include instructions for installing any necessary dependencies, running the web scraper, cleaning the data, setting up the Docker database, and loading the data into the database. 
