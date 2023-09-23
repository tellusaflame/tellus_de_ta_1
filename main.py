import requests
from bs4 import BeautifulSoup

import re
import copy
import os

from dotenv import load_dotenv

load_dotenv()

postgres_secrets = {
    "host": os.getenv("POSTGRES_HOST"),
    "port": os.getenv("POSTGRES_PORT"),
    "user": os.getenv("POSTGRES_USER"),
    "password": os.getenv("POSTGRES_PASSWORD"),
    "database": os.getenv("POSTGRES_DB"),
}

import psycopg2
from psycopg2 import Error
from psycopg2.extras import execute_batch

import logging

def scrape_wikipedia(city_names):
    cities_data = []

    for city_name in city_names:
        url = f"https://ru.wikipedia.org/wiki/{city_name}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        city_data = {
            "Город": city_name,
            "Страна": "",
            "Основан": "",
            "Климат": "",
            "Часовой пояс": "",
            "Население": "",
            "Почтовый индекс": ""
        }

        infobox = soup.find("table", class_="infobox")

        if infobox is not None:
            rows = infobox.find_all("tr")

            for row in rows:
                header = row.find("th")

                if header is not None:
                    header_text = header.text.strip()

                    if header_text == "Страна":
                        city_data["Страна"] = row.find("td").text.strip()

                    elif header_text in ["Основан", "Первое упоминание"]:    # , "Founded", "Platted"]:
                        city_data["Основан"] = row.find("td").text.strip()

                    elif header_text == "Тип климата":
                        city_data["Климат"] = row.find("td").text.strip()

                    elif header_text == "Часовой пояс":
                        city_data["Часовой пояс"] = row.find("td").text.strip()

                    elif header_text == "Население":
                        try:
                            city_data["Население"] = row.find("td").text.strip()
                        except:
                            logging.info("pizdec")

                    elif header_text in ["Почтовые индексы", "Почтовый индекс"]:
                        city_data["Почтовый индекс"] = row.find("td").text.strip()

        cities_data.append(city_data)

    return cities_data

def clean_data(raw_data):
    cleaned_cities_data = copy.deepcopy(raw_data)

    for city_data in cleaned_cities_data:

        # Cleaning 'Foundation date' field, removing all except 4-digit numbers
        city_data["Основан"] = re.findall('\d{4}', city_data["Основан"])[0]

        # Cleaning 'Population' field, removing junk symbols and other unnecessary info
        reg1 = r'\([\s\S]*\)'  # Within ()
        reg2 = r'\[[\s\S]*\]'  # Within []

        city_data["Население"] = city_data["Население"].replace('\xa0', "").translate(
            {ord(i): None for i in r'↗↘человека'})
        city_data["Население"] = re.sub(reg1, '', city_data["Население"])
        city_data["Население"] = re.sub(reg2, '', city_data["Население"])

        # Cleaning 'Postal code' field, only first 6 digits to be left for RU
        city_data["Почтовый индекс"] = city_data["Почтовый индекс"][:6]

    return cleaned_cities_data

def create_cursor(**secrets):
    connection = psycopg2.connect(user=secrets['user'],
                                  password=secrets['password'],
                                  host=secrets['host'],
                                  port=secrets['port'],
                                  database=secrets['database'])

    # Open a cursor to perform database operations
    cursor = connection.cursor()
    return cursor, connection

def main():
    # List of cities to obtain data from
    city_names = ["Москва", "Тимашёвск", "Иркутск", "Калуга", "Владивосток"]

    # Get raw data from scrapper
    raw_data = scrape_wikipedia(city_names)

    # Clean received data
    cleaned_data = clean_data(raw_data)

    # Open connection to db
    try:
        cursor, connection = create_cursor(**postgres_secrets)

        # Truncate table city_data
        cursor.execute(""" TRUNCATE city_data """)
        connection.commit()

        # Form an SQL query
        query = "INSERT INTO city_data VALUES (%(Город)s, %(Страна)s, %(Основан)s, %(Климат)s, %(Часовой пояс)s, %(Население)s, %(Почтовый индекс)s)"

        # Execute a command: this insert new rows to a table
        execute_batch(cursor, query, cleaned_data)

        # Make the changes to the database persistent
        connection.commit()
        logging.info("Все записи успешно вставлены")

        # Query the database and obtain data as Python objects
        cursor.execute("SELECT * from city_data")
        record = cursor.fetchall()
        logging.info("Результат", record)

    except (Exception, Error) as error:
        logging.exception("Ошибка при работе с PostgreSQL", error)
    finally:
        if connection:
            # Close communication with the database
            cursor.close()
            connection.close()
            logging.info("Соединение с PostgreSQL закрыто")

if __name__ == "__main__":
    main()