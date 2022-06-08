import psycopg2 as ps
from aws_config import aws_config
from sqlalchemy import create_engine
import numpy as np
import pandas as pd
from psycopg2 import extensions

def connect_to_db(host_name, dbname, port, username, password):
   try:
       conn = ps.connect(host=host_name, database=dbname, user=username,
       password=password, port=port)
 
   except ps.OperationalError as e:
       raise e
   else:
       print('Connected!')
       return conn

def exists_table(cursor):
    engine = create_engine(f"postgresql+psycopg2://{aws_config['username']}:{aws_config['password']}@{aws_config['db_host_name']}:{aws_config['port']}/{aws_config['db_name']}")
    conn = engine.raw_connection()
    cursor = conn.cursor()
    query = (f"""SELECT EXISTS (SELECT * FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'laptops')""")
    cursor.execute(query)
    fetched = [row[0] for row in cursor.fetchall()]
    if False in fetched:
        cursor.close()
        conn.commit()
        conn.close()
        return False
    else:
        return True

def create_table(cursor):
    query = (
        """
        CREATE TABLE IF NOT EXISTS laptops (
            uuid VARCHAR(36),
            url VARCHAR,
            productid INT,
            title VARCHAR,
            price FLOAT,
            imgsrc VARCHAR,
            rating FLOAT,
            ratingcount INT,
            type VARCHAR,
            operatingsystem VARCHAR,
            ram VARCHAR,
            storage VARCHAR,
            screensize VARCHAR,
            touchscreen VARCHAR,
            memorycardreader VARCHAR,
            camera VARCHAR,
            batterylife VARCHAR,
            colour VARCHAR,
            weight VARCHAR,
            dimensions VARCHAR,
            make VARCHAR,
            model VARCHAR,
            processormake VARCHAR,
            processormodel VARCHAR,
            cores VARCHAR,
            clockspeed VARCHAR
            )
            """)
    cursor.execute(query)

def clean_duplicates(df):
    engine = create_engine(f"postgresql+psycopg2://{aws_config['username']}:{aws_config['password']}@{aws_config['db_host_name']}:{aws_config['port']}/{aws_config['db_name']}")
    conn = engine.raw_connection()
    cursor = conn.cursor()
    exists = exists_table(cursor)
    if not exists:
        cursor.close()
        conn.commit()
        conn.close()
        return df
    else:
        for index, row in df.iterrows():
            query = (f"""SELECT EXISTS (SELECT productid FROM laptops WHERE productid = {row['productID']})""")
            cursor.execute(query)
            fetched = [row[0] for row in cursor.fetchall()]
            if True in fetched:
                print("Did exist")
                df = df[df.productID != row['productID']]
        cursor.close()
        conn.commit()
        conn.close()
        return df

def load_data(df):
    df = clean_duplicates(df)

    engine = create_engine(f"postgresql+psycopg2://{aws_config['username']}:{aws_config['password']}@{aws_config['db_host_name']}:{aws_config['port']}/{aws_config['db_name']}")
    conn = engine.raw_connection()
    cursor = conn.cursor()
    exists = exists_table(cursor)
    if not exists:
        create_table(cursor)
    cursor.close()
    conn.commit()

    cursor = conn.cursor()
    if not df.empty:
        _NULL=extensions.AsIs('NULL')
        pd.set_option("display.max_columns", None)
        print(df)
        df['rating'] = df['rating'].replace(np.NaN, 0)
        df['ratingCount'] = df['rating'].replace(np.NaN, 0)
        df = df.replace(np.NaN, 'NULL')
        query = (f""" INSERT INTO laptops VALUES {','.join([str(i) for i in list(df.to_records(index=False))])}""")
        cursor.execute(query)
    else:
        print('DataFrame is empty!')
        pass
    cursor.close()
    conn.commit()
    conn.close()