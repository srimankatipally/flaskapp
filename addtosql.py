import psycopg2
from psycopg2 import sql
from random import randint, uniform, choice
from datetime import datetime, timedelta

connection = psycopg2.connect(
    dbname="sales",
    user="postgres",
    password="root",
    host="localhost",  
    port="5433"   
)
cursor = connection.cursor()
create_table_query = """
CREATE TABLE IF NOT EXISTS orders (
    order_id SERIAL PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    order_date DATE NOT NULL,
    amount NUMERIC(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL
);
"""
cursor.execute(create_table_query)
connection.commit()
def random_date(start_date, end_date):
    delta = end_date - start_date
    random_days = randint(0, delta.days)
    return start_date + timedelta(days=random_days)
statuses = ["Pending", "Shipped", "Delivered", "Cancelled", "Returned"]

for _ in range(100):  
    customer_id = randint(1, 1000)  
    order_date = random_date(datetime(2022, 1, 1), datetime(2023, 12, 31))
    amount = round(uniform(10.0, 1000.0), 2)
    status = choice(statuses)
    
    insert_query = """
    INSERT INTO orders (customer_id, order_date, amount, status)
    VALUES (%s, %s, %s, %s);
    """
    
    cursor.execute(insert_query, (customer_id, order_date, amount, status))
connection.commit()
print("Random data inserted successfully into the orders table.")
cursor.close()
connection.close()
