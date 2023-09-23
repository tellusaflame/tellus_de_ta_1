-- Creation of product table
CREATE TABLE IF NOT EXISTS city_data (
  city varchar(250) NOT NULL,
  country varchar(250) NOT NULL,
  founded INT NOT NULL,
  climate varchar(250) NOT NULL,
  time_zone varchar(250) NOT NULL,
  population INT NOT NULL,
  postal_code varchar(6) NOT NULL 
);