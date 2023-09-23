import requests
from bs4 import BeautifulSoup

import re
import copy

import psycopg2
from psycopg2 import Error

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

        # infobox = soup.find("table", class_="infobox geography vcard")
        # infobox = soup.find("table", class_="infobox ib-settlement vcard")
        infobox = soup.find("table", class_="infobox")
        #print(infobox)

        if infobox is not None:
            rows = infobox.find_all("tr")

            for row in rows:
                header = row.find("th")
                #print(header)
                if header is not None:
                    header_text = header.text.strip()
                    #print(header_text)

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
                            print("pizdec")

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

# List of cities to obtain data from
city_names = ["Москва", "Тимашёвск", "Иркутск", "Калуга", "Владивосток"]

# Get raw data from scrapper
raw_data = scrape_wikipedia(city_names)

# Clean received data
cleaned_data = clean_data(raw_data)

# for city_data in raw_data:
#     print(city_data)
#     print()

for city_data in cleaned_data:
    print(city_data)
    print()

# Open connection to db
try:
    # Connect to desired DB
    connection = psycopg2.connect(user="user",
                                  password="password",
                                  host="127.0.0.1",
                                  port="5432",
                                  database="database")
    # Open a cursor to perform database operations
    cursor = connection.cursor()

    # Truncate table city_data
    cursor.execute(""" TRUNCATE city_data """)
    connection.commit()

    # Cycle all cities, insert data to table
    for city_data in cleaned_data:

        # Form an SQL query
        insert_query = """INSERT INTO city_data (city, country, founded, climate, time_zone, population, postal_code) 
        VALUES (%s,%s,%s,%s,%s,%s,%s)"""

        # Form data to insert within SQL query
        data_to_insert = (city_data["Город"],
                            city_data["Страна"],
                            city_data["Основан"],
                            city_data["Климат"],
                            city_data["Часовой пояс"],
                            city_data["Население"],
                            city_data["Почтовый индекс"],
                            )

        # Execute a command: this insert new row to a table
        cursor.execute(insert_query, data_to_insert)

        # Make the changes to the database persistent
        connection.commit()
        print("1 запись успешно вставлена")

    # Query the database and obtain data as Python objects
    cursor.execute("SELECT * from city_data")
    record = cursor.fetchall()
    print("Результат", record)

except (Exception, Error) as error:
    print("Ошибка при работе с PostgreSQL", error)
finally:
    if connection:
        # Close communication with the database
        cursor.close()
        connection.close()
        print("Соединение с PostgreSQL закрыто")