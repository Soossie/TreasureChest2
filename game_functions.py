import random
#from geopy import distance
import geopy.distance
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


def get_game_countries(difficulty_level):
    sql = (f'select country_count, airports_in_treasure_land from difficulty '
           f'where level = "{difficulty_level}";')
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    # print(result)
    countries_for_difficulty_level = result[0]
    min_countries_in_treasure_land = int(int(result[1]) / 2)
    # print(f'{countries_for_difficulty_level}, {min_countries_in_treasure_land}')

    #sql = (f'SELECT name FROM country where continent = "EU" '
    #       f'order by rand() limit {countries_for_difficulty_level};')

    sql = (f'select country.name, count(*) from country '
           f'left join airport on airport.iso_country = country.iso_country '
           f'where country.continent = "EU" group by country.iso_country '
           f'having count(*) >= {min_countries_in_treasure_land} '
           f'order by rand() '
           f'limit {countries_for_difficulty_level};')

    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()

    results = []
    for item in result:
        results.append(item[0])
    return results


def get_biggest_airport_size_for_country(country_name):
    sql = (f'select airport.type from airport '
           f'inner join country on airport.iso_country = country.iso_country '
           f'where country.name = "{country_name}" group by type;')

    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()

    size = False

    # muuttaa listan monikoita listaksi
    result = [item[0] for item in result]

    # määrittää maan suurimman lentokentän koon.
    # lentokenttien koot monikossa suuruusjärjestyksessä suurimmasta pienimpään
    for airport_size in ('large_airport', 'medium_airport', 'small_airport', 'heliport'):
        if airport_size in result and not size:
            size = airport_size

    return size


def get_default_airport_for_country(country_name):
    # hae maan suurimman lentokentän koko
    biggest_airport_size = get_biggest_airport_size_for_country(country_name)

    # lopeta jos edellisestä tuli False eli maalla ei ole suurta, keskikokoista tai pientä lentokenttää
    # tai helikopterikenttää
    if not biggest_airport_size:
        return False

    sql = (f'SELECT airport.name from airport '
           f'inner join country on airport.iso_country = country.iso_country '
           f'where country.name = "{country_name}" and type like "{biggest_airport_size}" order by rand() limit 1;')

    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()

    # palauttaa tuloksen ensimmäisen arvon jos tulos on olemassa
    return result[0] if result else False


def get_default_money(difficulty_level):
    sql = f'select starting_money from difficulty where level = "{difficulty_level}";'
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]


def get_treasure_land_airports(difficulty_level, country_name, treausure_land_default_airport_ident):
    sql = f'select airports_in_treasure_land from difficulty where level = "{difficulty_level}";'
    cursor = connection.cursor()
    cursor.execute(sql)
    airport_count = cursor.fetchone()[0]

    # hae satunnaiset aarremaan lentokentät. testaa että ei ole aarremaan oletuslentokenttä
    sql = (f'SELECT airport.name FROM airport inner join country on airport.iso_country = country.iso_country '
           f'where country.name = "{country_name}" and airport.type != "closed" and airport.ident != "{treausure_land_default_airport_ident}" '
           f'order by rand() limit {airport_count};')

    # original
    #sql = (f'SELECT airport.name FROM airport inner join country on airport.iso_country = country.iso_country '
    #       f'where country.name = "{country_name}" order by rand() limit {airport_count};')
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()

    results = []
    for item in result:
        results.append(item[0])
    return results


def get_wise_man_count(difficulty_level):
    sql = (f'select wise_man_count from difficulty '
           f'where level = "{difficulty_level}";')
    cursor = connection.cursor()
    cursor.execute(sql)
    wise_man_count = cursor.fetchone()[0]
    return wise_man_count


def input_player_info(screen_name, money, home_airport, location, difficulty_level):
    sql = (f'insert into game(screen_name, money, home_airport, location, difficulty_level) '
           f'values("{screen_name}", "{money}", "{home_airport}", "{location}", "{difficulty_level}");')
    cursor = connection.cursor()
    cursor.execute(sql)

# hakee lentokentän ICAO-koodin
def get_airport_ident_from_name(airport_name):
    sql = f'select ident from airport where name = "{airport_name}";'
    cursor = connection.cursor(buffered=True)
    cursor.execute(sql)
    ident = cursor.fetchone()[0]
    return ident



def save_airport_to_game_airports(game_id, airport_ident, wise_man_question_id, answered, has_treasure, is_default_airport):
    # parannusehdotus: yhdistä kyselyt yhdeksi. ongelma on sijoittaa NULL arvo tietokantaan, mutta se on myös jo oletusarvo

    if not wise_man_question_id:
        # ei tietäjän kysymystä
        sql = (f'insert into game_airports(game_id, airport_ident, answered, has_treasure, is_default_airport) '
               f'values("{game_id}", "{airport_ident}", "{answered}", "{has_treasure}", "{is_default_airport}");')

    else:
        sql = (f'insert into game_airports(game_id, airport_ident, wise_man_question_id, answered, has_treasure, is_default_airport) '
               f'values("{game_id}", "{airport_ident}", "{wise_man_question_id}", "{answered}", "{has_treasure}", "{is_default_airport}");')

    cursor = connection.cursor()
    cursor.execute(sql)


def get_screen_name_game_id(screen_name):
    sql = f'select id from game where screen_name = "{screen_name}";'
    cursor = connection.cursor()
    cursor.execute(sql)
    return cursor.fetchone()[0]


def screen_name_exists(screen_name):
    # tarkista löytyykö pelaajan nimi tietokannasta
    sql = f'select screen_name from game;'
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()

    # muuttaa tulokset listaksi
    results = [item[0] for item in result]

    # palauttaa True jos samanniminen pelaaja on olemassa, muuten palauttaa False
    return screen_name in results


def get_random_unused_question_id(game_id):

    sql = (f'select id from wise_man_questions '
           f'where id not in (select wise_man_question_id from game_airports where game_id = 56 and '
           f'wise_man_question_id != NULL) '
           f'order by rand();')

    cursor = connection.cursor(buffered=True)
    cursor.execute(sql)
    #print(cursor.fetchone())
    return cursor.fetchone()[0]


def get_random_question_id():
    sql = f'select id from wise_man_questions order by rand();'
    cursor = connection.cursor(buffered=True)
    cursor.execute(sql)
    return cursor.fetchone()[0]

# hae home_airportin icao-koodi
def get_home_airport_icao(game_id):
    sql = f'select home_airport from game where id = "{game_id}";'
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    #print(result)
    return result[0]

# hae lentokentän nimi
def get_airport_name(airport_icao):
    sql = f'select airport.name from airport where ident = "{airport_icao}";'
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    #print(result)
    return result[0]

# hae maan nimi
def get_country_name(airport_icao):
    sql = (f'select country.name from country inner join airport on country.iso_country = airport.iso_country '
           f'where ident = "{airport_icao}";')
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    #print(result)
    return result[0]

# hae käytössä oleva raha
def get_player_money(game_id):
    sql = (f'select money from game where id = "{game_id}";')
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    #print(result)
    return result[0]

# hae lentokentän koordinaatit
def get_used_airport_coordinates(airport_icao):
    sql = f'select latitude_deg, longitude_deg from airport where ident = "{airport_icao}";'
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result

# laske lentokenttien välinen etäisyys
def get_distance_between_airports(airport_icao1, airport_icao2):
    coordinates1 = get_used_airport_coordinates(airport_icao1)
    coordinates2 = get_used_airport_coordinates(airport_icao2)
    distance = geopy.distance.distance(coordinates1, coordinates2).km
    distance = int(distance)
    return distance

# hae pelaajan nykyinen sijainti
def get_current_location(game_id):
    sql = f'select location from game where id = "{game_id}";'
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]