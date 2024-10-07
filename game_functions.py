import random
#from geopy import distance
import geopy.distance
import mysql.connector
from tabulate import tabulate

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
    min_airports_in_treasure_land = int(int(result[1]) / 2)
    # print(f'{countries_for_difficulty_level}, {min_countries_in_treasure_land}')

    #sql = (f'SELECT name FROM country where continent = "EU" '
    #       f'order by rand() limit {countries_for_difficulty_level};')

    sql = (f'select country.name, count(*) from country '
           f'left join airport on airport.iso_country = country.iso_country '
           f'where country.continent = "EU" and airport.type != "closed" '
           f'group by country.iso_country '
           f'having count(*) >= {min_airports_in_treasure_land} '
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


def get_random_default_airport_for_country(country_name):
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


def get_default_airport_ident_for_country(game_id, country_name):
    # vaihtoehtoiset tavat sql kyselylle riippuen minkälainen lainausmerkki nimessä on
    if '"' in country_name:
        sql = (f"SELECT game_airports.airport_ident, country.name FROM game_airports "
               f"INNER JOIN game ON game_airports.game_id = game.id "
               f"INNER JOIN airport ON game_airports.airport_ident = airport.ident "
               f"INNER JOIN country ON airport.iso_country = country.iso_country "
               f"WHERE game.id = {game_id} AND game_airports.is_default_airport = 1 AND country.name = '{country_name}';")
    else:
        sql = (f'SELECT game_airports.airport_ident, country.name FROM game_airports '
               f'INNER JOIN game ON game_airports.game_id = game.id '
               f'INNER JOIN airport ON game_airports.airport_ident = airport.ident '
               f'INNER JOIN country ON airport.iso_country = country.iso_country '
               f'WHERE game.id = {game_id} AND game_airports.is_default_airport = 1 AND country.name = "{country_name}";')

    cursor = connection.cursor(buffered=True)
    cursor.execute(sql)
    result = cursor.fetchone()

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
    #print(airport_name)

    # vaihtoehtoiset tavat sql kyselylle riippuen minkälainen lainausmerkki nimessä on
    if '"' in airport_name:
        sql = f"select ident from airport where name = '{airport_name}';"
    else:
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

def get_random_reward(difficulty_level):
    sql = f'select name, id from rewards where difficulty_level = "{difficulty_level}" order by rand() limit 1;'
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]

def update_current_location(game_id, new_location_icao):
    sql = f'update game set location = "{new_location_icao}" where id = "{game_id}";'
    cursor = connection.cursor()
    cursor.execute(sql)

# matkusta maiden välillä
def travel_between_countries(game_id, game_countries, money):
    i = 0
    country_list = []
    for country in game_countries:
        location = get_current_location(game_id)
        airport_icao1 = location
        default_airport = get_default_airport_for_country(country)
        airport_icao2 = get_airport_ident_from_name(default_airport)
        distance = get_distance_between_airports(airport_icao1, airport_icao2)
        ticket_cost = int(count_ticket_cost_between_countries(distance))
        if money < ticket_cost:
            can_travel = False
        else:
            can_travel = True
        if airport_icao1 != airport_icao2:
            i += 1
            country_list.append([i, country, distance, ticket_cost, can_travel])
            # print(f'{i}. {country}, {distance} km, ticket costs {ticket_cost} €.\n')
            # country_list.append(country)
    print(tabulate(country_list, headers=['Number', 'Country', 'Distance (km)', 'Ticket cost (€)', 'Travellable'], tablefmt='pretty'))
    next_country_number = False
    while not next_country_number:
        next_country_number_input = input('Input country number: ')
        if next_country_number_input.isnumeric():
            next_country_number_input = int(next_country_number_input)
            if 1 <= next_country_number_input <= len(country_list):
                next_country_number = next_country_number_input
            else:
                print('Invalid input. Select number from the list.')
        else:
            print('Invalid input.')
    next_country_number -= 1
    money -= country_list[next_country_number][3]
    country1 = get_country_name(get_current_location(game_id))
    country2 = country_list[next_country_number][1]
    ticket_price = country_list[next_country_number][3]
    distance1 = country_list[next_country_number][2]
    print(f'The ticket from {country1} to {country2} costs {ticket_price} € and the distance there is {distance1} km. You have {money} € left.\n...')
    update_current_location(game_id, get_airport_ident_from_name(get_default_airport_for_country(country_list[next_country_number][1])))
    return next_country_number

# matkusta maan sisällä
def travel_inside_country(game_id, treasure_land_airports, money):
    i = 0
    airport_list = []
    for airport in treasure_land_airports:
        location = get_current_location(game_id)
        airport_icao1 = location
        airport_icao2 = get_airport_ident_from_name(airport)
        distance = get_distance_between_airports(airport_icao1, airport_icao2)
        ticket_cost = int(count_ticket_cost_inside_country(distance))
        if money < ticket_cost:
            can_travel = False
        else:
            can_travel = True
        if airport_icao1 != airport_icao2:
            i += 1
            airport_list.append([i, airport, distance, ticket_cost, can_travel])
            # print(f'{i}. {airport}, {distance} km, ticket costs {ticket_cost} €.\n')
            # airport_list.append(airport)
    print(tabulate(airport_list, headers=['Number', 'Airport', 'Distance (km)', 'Ticket cost (€)', 'Travellable'], tablefmt='pretty'))
    next_airport = False
    while not next_airport:
        next_airport_input = input('Input airport number: ')
        if next_airport_input.isnumeric():
            next_airport_input = int(next_airport_input)
            if 1 <= next_airport_input <= len(airport_list):
                next_airport = next_airport_input
            else:
                print('Invalid input. Select number from the list.')
        else:
            print('Invalid input.')
    next_airport -= 1
    money -= airport_list[next_airport][3]
    airport1 = get_airport_name(get_current_location(game_id))
    airport2 = airport_list[next_airport][1]
    ticket_price = airport_list[next_airport][3]
    distance1 = airport_list[next_airport][2]
    print(f'The ticket from {airport1} to {airport2} costs {ticket_price} € and the distance there is {distance1} km. You have {money} € left.\n...')
    update_current_location(game_id, get_airport_ident_from_name(airport_list[next_airport][1]))
    wise_man = check_if_wise_man(location, game_id)
    meet_wise_man_if_exists(wise_man)

#laske maiden välisen lennon hinta etäisyyden perusteella
def count_ticket_cost_between_countries(distance):
    if distance < 200:
        ticket_cost = 100 + 1.00 * distance
    if 200 <= distance <= 500:
        ticket_cost = 100 + 0.70 * distance
    if 500 < distance < 800:
        ticket_cost = 100 + 0.40 * distance
    if distance > 800:
        ticket_cost = 100 + 0.25 * distance
    return ticket_cost

#laske maan sisäisen lennon hinta etäisyyden perusteella
def count_ticket_cost_inside_country(distance):
    if distance < 200:
        ticket_cost = 100 + 1.25 * distance
    if 200 <= distance <= 500:
        ticket_cost = 100 + 0.85 * distance
    if 500 < distance < 800:
        ticket_cost = 100 + 0.55 * distance
    if distance > 800:
        ticket_cost = 100 + 0.40 * distance
    return ticket_cost

# hae maan nimi lentokentän icao-koodin perusteella
def get_country_name(airport_icao):
    sql = (f'select country.name from country inner join airport on country.iso_country = airport.iso_country '
           f'where ident = "{airport_icao}";')
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    #print(result)
    return result[0]

# määritä vihje: hae aarremaan ensimmäinen kirjain
def get_clue(game_id):
    sql = f'select airport_ident from game_airports where wise_man_question_id != "NULL" and game_id = {game_id} limit 1;'
    cursor = connection.cursor()
    cursor.execute(sql)
    airport_icao = cursor.fetchone()[0]
    country_name = get_country_name(airport_icao)
    hint_letter = country_name[0]
    clue = (f'Clue: the treasure is hidden in the country whose first letter is {hint_letter}.')
    return clue

# tarkista, onko lentokentällä tietäjä
def check_if_wise_man(location, game_id):
    location = get_current_location(game_id)
    sql = (f'select wise_man_question_id from game_airports where airport_ident = "{location}" and '
           f'game_id = "{game_id}";')
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    #print(location)
    if result != None:
        return result[0]    #jos on tietäjä, palauttaa kysymyksen id:n, jos ei niin palauttaa None
    else:
        return None

# hae tietäjän kysymys ja vastaus
def get_wise_man_question_and_answer(location, game_id):
    sql = (f'select wise_man_question_id from game_airports where airport_ident = "{location}" and '
           f'game_id = "{game_id}";')
    cursor = connection.cursor()
    cursor.execute(sql)
    question_id = cursor.fetchone()
    question_id = question_id[0]
    sql = (f'select question, answer from wise_man_questions where id = "{question_id}";')
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    return result[0]   #palauttaa monikkona kysymyksen ja vastauksen

# hae tietäjän maksu ja palkinto
def get_wise_man_cost_and_reward(difficulty_level):
    sql = f'select wise_man_cost, wise_man_reward from difficulty where level = "{difficulty_level}";'
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result

def meet_wise_man_if_exists(wise_man, game_id, wise_man_cost, wise_man_reward, money):
    print(wise_man)     #kysymyksen id tulostuu
    location = get_current_location(game_id)
    if wise_man != None:
        question = get_wise_man_question_and_answer(location, game_id)[0]
        answer = get_wise_man_question_and_answer(location, game_id)[1]
        user_input = input(f'You encountered a wise man. Do you want to buy a question? Cost: {wise_man_cost} €.\n'
              f'Input y (yes) or n (no): ')
        user_input = user_input.lower()
        while user_input not in ('y', 'yes', 'n', 'no'):
            user_input = input('Invalid input. Input y (yes) or n (no): ')
        if user_input in ('y', 'yes'):
            #money -= wise_man_cost         ##tässä kohtaa on joku ongelma money-termin kanssa???!!!
            ##tässä kohtaa pitää päivittää sql-tauluun answered-kohta
            print(f'You have {money} €.')
            print(f'Question: {question}')
            user_answer = input('Input answer (a, b or c): ')
            user_answer = user_answer.lower()
            while user_answer not in ('a', 'b', 'c'):
                user_answer = input('Invalid input. Input answer (a, b or c): ')
                user_answer = user_answer.lower()
            if user_answer == answer:
                #money += wise_man_reward           #tässäkin sama rahaongelma
                print(f'Correct! You won {wise_man_reward} €.\nYou have {money} €.')
            else:
                print(f'Wrong! Correct answer is {answer}.')
        elif user_input in ('n', 'no'):
            print('No question this time. Bye!')
    else:
        print('No wise man here.')

# rahat loppuu tai ei riitä mihinkään lentolippuun
def game_over():
    print(f'Out of money! You can not afford a ticket. Game over!')