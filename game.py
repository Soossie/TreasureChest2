# Treasure Chest (Aarrearkku)

import random
from geopy import distance

import mysql.connector

connection = mysql.connector.connect(
    host='localhost',
    port=3306,
    database='treasure_chest',
    user='treasure',
    password='chest',
    autocommit=True,
    collation='utf8mb4_general_ci'
)


def database_function_test():
    sql = "SELECT * FROM difficulty"
    cursor = connection.cursor(dictionary=True)
    cursor.execute(sql)
    result = cursor.fetchall()

    # tulostaa vaikeustaso-taulun kaikki rivit
    for row in result:
        print(row)
    return


database_function_test()
