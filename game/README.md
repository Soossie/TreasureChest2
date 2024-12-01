# Welcome to the search of the Treasure Chest!

## Prequisites before playing
To play, you must have MariaDB and mysql installed.
1. Open your terminal or command prompt.
2.  Run the following:
    ```sh
    mysql
    ```
    Then, execute the following SQL commands:
    ```sql
    CREATE DATABASE treasure_chest;
    CREATE USER 'treasure'@'localhost' IDENTIFIED BY 'chest';
    GRANT SELECT, INSERT, UPDATE, DELETE ON treasure_chest.* TO 'treasure'@'localhost';
    ```  
3. Download the file creation_script2.sql
4. Execute the following SQL command in a code editor terminal:
    ```sql
    USE treasure_chest
    SOURCE creation_script.sql;
    ```
    The game can be run in a code editor, such as PyCharm or VS Code


Ennen pelin suoritusta on muodostettava yhteys tietokantaan. 
Luo **.env** niminen tiedosto game-kansioon ja kopioi siihen seuraavat tiedot:

```python
HOST=localhost
DB_NAME=treasure_chest
DB_USER=treasure
DB_PASS=chest
```

Voit muokata tietoja mikäli tietokantasi on erilainen.
