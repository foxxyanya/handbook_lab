### Схема таблиц:

#### Города:
id INTEGER PRIMARY KEY
name TEXT
population INTEGER
area DECIMAL(10, 2)
continent TEXT
date_of_foundation DATE

#### Страны:
id INTEGER PRIMARY KEY
name TEXT
country_id INTEGER
population INTEGER
area DECIMAL(12, 2)
date_of_foundation DATE

### Как запускать:
Настройка энвайронмента:
```
python -m venv env
source env/bin/activate
pip install -r requirements.txt
sudo apt-get install python3-tk
```

Инициализация базы данных:
```
python db_init.py
```
Запуск интерфейса:
```
python main.py
```