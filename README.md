# Welcome to search the Treasure Chest!

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
3. Download the following: [1](sql_scripts/run_1st_project_base.sql) and [2](sql_scripts/run_2nd_tables_and_values.sql)
    
4. Execute the following SQL commands:
    ```sql
    USE treasure_chest
    SOURCE "path/to/1"
    SOURCE "path/to/2";
    ```