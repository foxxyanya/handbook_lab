import sqlite3

if __name__ == "__main__":
    con = sqlite3.connect('lab2.db')
    cursor = con.cursor()

    cursor.execute("""
        CREATE TABLE country
            (id INTEGER PRIMARY KEY AUTOINCREMENT,  
            name TEXT, 
            population INTEGER,
            area DECIMAL(12, 2),
            continent TEXT,
            date_of_foundation DATE);
        """
    )
    con.commit()
    cursor.execute("""
        CREATE TABLE city
            (id INTEGER PRIMARY KEY AUTOINCREMENT,  
            name TEXT, 
            country_id INTEGER,
            population INTEGER,
            area DECIMAL(12, 2),
            date_of_foundation DATE,
            FOREIGN KEY(country_id) REFERENCES countries(id));
        """
    )

    country_records = [
        ("Belarus", 9255524, 207595.1, "Eurasia", "1991-08-25"),
        ("USA", 331883986, 9631418.4, "North America", "1776-07-04"),
        ("Germany", 83190556, 357022.2, "Eurasia", "1871-01-18"),
    ]

    for country in country_records:
        cursor.execute("""
            INSERT INTO country(name, population, area, continent, date_of_foundation)
            VALUES(?, ?, ?, ?, ?)
            """, 
            country
        )

    city_records = [
        ("Minsk", 1, 1995471, 348.84, "1067-01-01"),
        ("New York City", 2, 8336817, 783.4, "1664-09-01"),
        ("Berlin", 3, 3357022 , 891.85 , "1237-10-28"),
    ]

    for city in city_records:
        cursor.execute("""
            INSERT INTO city(name, country_id, population, area, date_of_foundation)
            VALUES(?, ?, ?, ?, ?)
            """, 
            city
        )


    con.commit()

    cursor.close()
    con.close()