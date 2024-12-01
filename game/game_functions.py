import math
import geopy.distance
from tabulate import tabulate
import sys
import time
from database import Database
import json
from flask import Flask
from flask_cors import CORS

db = Database()


def get_game_countries(difficulty_level):
    sql = (f'select country_count, airports_in_treasure_land from difficulty '
           f'where level = "{difficulty_level}";')
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    countries_for_difficulty_level = result[0]
    min_airports_in_treasure_land = int(int(result[1]) / 2)

    sql = (f'select country.name, count(*) from country '
           f'left join airport on airport.iso_country = country.iso_country '
           f'where country.continent = "EU" and airport.type != "closed" '
           f'group by country.iso_country '
           f'having count(*) >= {min_airports_in_treasure_land} '
           f'order by rand() '
           f'limit {countries_for_difficulty_level};')

    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    return [item[0] for item in result]

def get_biggest_airport_size_for_country(country_name):
    sql = (f'select airport.type from airport '
           f'inner join country on airport.iso_country = country.iso_country '
           f'where country.name = "{country_name}" group by type;')

    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    size = False

    # muuttaa listan monikoita listaksi
    result = [item[0] for item in result]

    # määrittää maan suurimman lentokentän koon
    # lentokenttien koot monikossa suuruusjärjestyksessä suurimmasta pienimpään
    for airport_size in ('large_airport', 'medium_airport', 'small_airport', 'heliport'):
        if airport_size in result and not size:
            size = airport_size
    return size

def get_random_default_airport_icao_for_country(country_name):
    # hae maan suurimman lentokentän koko
    biggest_airport_size = get_biggest_airport_size_for_country(country_name)

    # lopeta jos edellisestä tuli False eli maalla ei ole suurta, keskikokoista tai pientä lentokenttää
    # tai helikopterikenttää
    if not biggest_airport_size:
        return False

    sql = (f'SELECT airport.ident from airport '
           f'inner join country on airport.iso_country = country.iso_country '
           f'where country.name = "{country_name}" and type like "{biggest_airport_size}" order by rand() limit 1;')

    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchone()

    # palauttaa tuloksen ensimmäisen arvon jos tulos on olemassa
    return result[0] if result else False

def get_default_money(difficulty_level):
    sql = f'select starting_money from difficulty where level = "{difficulty_level}";'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    return cursor.fetchone()[0]

def get_treasure_land_airport_icaos(difficulty_level, country_name, treausure_land_default_airport_icao):
    sql = f'select airports_in_treasure_land from difficulty where level = "{difficulty_level}";'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    airport_count = cursor.fetchone()[0]

    # hae satunnaiset aarremaan lentokentät. testaa että ei ole aarremaan oletuslentokenttä
    sql = (f'SELECT airport.ident FROM airport inner join country on airport.iso_country = country.iso_country '
           f'where country.name = "{country_name}" and airport.type != "closed" and airport.ident != "{treausure_land_default_airport_icao}" '
           f'order by rand() limit {airport_count};')

    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchall()

    return [item[0] for item in result]

# hae wise man arvot
def get_wise_man_count(difficulty_level):
    sql = (f'select wise_man_count from difficulty '
           f'where level = "{difficulty_level}";')
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    wise_man_count = cursor.fetchone()[0]
    return wise_man_count

# lisää pelaajan tiedot
def input_player_info(screen_name, money, home_airport, location, difficulty_level):
    sql = (f'insert into game(screen_name, money, home_airport, location, difficulty_level) '
           f'values("{screen_name}", "{money}", "{home_airport}", "{location}", "{difficulty_level}");')
    cursor = db.get_conn().cursor()
    cursor.execute(sql)

def save_airport_to_game_airports(game_id, airport_ident, wise_man_question_id, answered, has_treasure, is_default_airport):
    # parannusehdotus: yhdistä kyselyt yhdeksi. ongelma on sijoittaa NULL arvo tietokantaan, mutta se on myös jo oletusarvo

    if not wise_man_question_id:
        # ei tietäjän kysymystä
        sql = (f'insert into game_airports(game_id, airport_ident, answered, has_treasure, is_default_airport) '
               f'values("{game_id}", "{airport_ident}", "{answered}", "{has_treasure}", "{is_default_airport}");')

    else:
        sql = (f'insert into game_airports(game_id, airport_ident, wise_man_question_id, answered, has_treasure, is_default_airport) '
               f'values("{game_id}", "{airport_ident}", "{wise_man_question_id}", "{answered}", "{has_treasure}", "{is_default_airport}");')

    cursor = db.get_conn().cursor()
    cursor.execute(sql)

# uudella pelaajalla on aina viimeinen id
def get_last_game_id():
    sql = f'select id from game order by id desc limit 1;'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    return cursor.fetchone()[0]

def get_random_unused_question_id(game_id):
    sql = (f'select id from wise_man_questions '
           f'where id not in (select wise_man_question_id from game_airports where game_id = {game_id} and '
           f'wise_man_question_id IS NOT NULL) '
           f'order by rand();')
    cursor = db.get_conn().cursor(buffered=True)
    cursor.execute(sql)
    return cursor.fetchone()[0]

def get_random_question_id():
    sql = f'select id from wise_man_questions order by rand();'
    cursor = db.get_conn().cursor(buffered=True)
    cursor.execute(sql)
    return cursor.fetchone()[0]

# hae lentokentän nimi
def get_airport_name(airport_icao):
    sql = f'select airport.name from airport where ident = "{airport_icao}";'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]

# hae maan nimi
def get_country_name(airport_icao):
    sql = (f'select country.name from country inner join airport on country.iso_country = airport.iso_country '
           f'where ident = "{airport_icao}";')
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]

# hae käytössä oleva raha
def get_player_money(game_id):
    sql = f'select money from game where id = "{game_id}";'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]

# hae lentokentän koordinaatit
def get_airport_coordinates(airport_icao):
    sql = f'select latitude_deg, longitude_deg from airport where ident = "{airport_icao}";'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result

# laske lentokenttien välinen etäisyys
def get_distance_between_airports(airport_icao1, airport_icao2):
    coordinates1 = get_airport_coordinates(airport_icao1)
    coordinates2 = get_airport_coordinates(airport_icao2)
    distance = geopy.distance.distance(coordinates1, coordinates2).km
    distance = int(distance)
    return distance

# hae pelaajan nykyinen sijainti
def get_current_location(game_id):
    sql = f'select location from game where id = "{game_id}";'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]

def get_random_reward(difficulty_level):
    sql = f'select name, id from rewards where difficulty_level = "{difficulty_level}" order by rand() limit 1;'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]

def update_current_location(game_id, new_location_icao):
    sql = f'update game set location = "{new_location_icao}" where id = "{game_id}";'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)

# matkusta maiden välillä
"""
def travel_between_countries(game_id, game_countries, money):
    i = 0
    country_list = []
    for country in game_countries:
        location = get_current_location(game_id)
        airport_icao1 = location
        default_airport = get_airport_name(get_default_airport_ident_for_country(game_id, country))
        airport_icao2 = get_airport_ident_from_name(default_airport)
        distance = get_distance_between_airports(airport_icao1, airport_icao2)
        ticket_cost = int(count_ticket_cost_between_countries(distance))
        visited = "Yes" if any([True for i in visited_country_list if i == country]) else "No"
        if money < ticket_cost:
            can_travel = False
        else:
            can_travel = True
        if airport_icao1 != airport_icao2:
            i += 1
            country_list.append([i, country, distance, ticket_cost, can_travel, visited])
    print(tabulate(country_list, headers=['Number', 'Country', 'Distance (km)', 'Ticket cost (€)', 'Travellable', 'Visited'], tablefmt='pretty'))
    travellable = any([True for i in country_list if i[4] == True])
    if not travellable:
        game_over(game_id)
    next_country_number = False
    while not next_country_number:
        next_country_number_input = input('Input country number: ')
        if next_country_number_input.isnumeric():
            next_country_number_input = int(next_country_number_input)
            if 1 <= next_country_number_input <= len(country_list) and country_list[next_country_number_input - 1][4] == True:
                next_country_number = next_country_number_input
            else:
                print('Invalid input. Select a country number from the list that you can afford.')
        else:
            print('Invalid input.')
    next_country_number -= 1
    money -= country_list[next_country_number][3]
    country1 = get_country_name(get_current_location(game_id))
    country2 = country_list[next_country_number][1]
    visited_country_list.append(country2)
    ticket_price = country_list[next_country_number][3]
    distance1 = country_list[next_country_number][2]
    next_airport_name = get_airport_name(get_default_airport_ident_for_country(game_id, country_list[next_country_number][1]))
    time.sleep(0.5)
    print(f'The ticket from {country1} to {country2} costs {ticket_price} € and the distance there is {distance1} km. You have {money} € left.\n')
    time.sleep(0.5)
    update_current_location(game_id, get_default_airport_ident_for_country(game_id, (country_list[next_country_number][1])))
    for i in range(len(next_airport_name) + 14):
        print(".", end="")
    print(f"\nTravelling to {next_airport_name}")
    total_dots = len(next_airport_name) + 14
    sleep_time = 3 / total_dots
    for i in range(total_dots):
        print(".", end="")
        time.sleep(sleep_time)
    print("")
    return next_country_number, country_list, money
"""

# matkusta maan sisällä
"""
def travel_inside_country(game_id, treasure_land_airports, money, wise_man_cost, wise_man_reward):
    i = 0
    airport_list = []
    for airport in treasure_land_airports:
        location = get_current_location(game_id)
        airport_icao1 = location
        airport_icao2 = get_airport_ident_from_name(airport)
        distance = get_distance_between_airports(airport_icao1, airport_icao2)
        ticket_cost = int(count_ticket_cost_inside_country(distance))
        visited = "Yes" if any([True for i in visited_airport_list if i == airport]) else "No"
        if money < ticket_cost:
            can_travel = False
        else:
            can_travel = True
        if airport_icao1 != airport_icao2:
            i += 1
            airport_list.append([i, airport, distance, ticket_cost, can_travel, visited])
    print(tabulate(airport_list, headers=['Number', 'Airport', 'Distance (km)', 'Ticket cost (€)', 'Travellable', 'Visited'], tablefmt='pretty'))
    travellable = any([True for i in airport_list if i[4] == True])
    if not travellable:
        game_over(game_id)
    next_airport_number = False
    while not next_airport_number:
        next_airport_number_input = input('Input airport number: ')
        if next_airport_number_input.isnumeric():
            next_airport_number_input = int(next_airport_number_input)
            if 1 <= next_airport_number_input <= len(airport_list) and airport_list[next_airport_number_input - 1][4] == True:
                next_airport_number = next_airport_number_input
            else:
                print('Invalid input. Select number from the list.')
        else:
            print('Invalid input.')
    next_airport_number -= 1
    money -= airport_list[next_airport_number][3]
    airport1 = get_airport_name(get_current_location(game_id))
    airport2 = airport_list[next_airport_number][1]
    visited_airport_list.append(airport2)
    ticket_price = airport_list[next_airport_number][3]
    distance1 = airport_list[next_airport_number][2]
    print(f'The ticket from {airport1} to {airport2} costs {ticket_price} € and the distance there is {distance1} km.\n')
    time.sleep(0.5)
    location = update_current_location(game_id, get_airport_ident_from_name(airport_list[next_airport_number][1]))
    for i in range(len(airport2) + 14):
        print(".", end="")
    print(f"\nTravelling to {airport2}")
    total_dots = len(airport2) + 14
    sleep_time = 3 / total_dots
    for i in range(total_dots):
        print(".", end="")
        time.sleep(sleep_time)
    print("")
    location = get_current_location(game_id)
    wise_man = check_if_wise_man(location, game_id)
    meet_wise_man_if_exists(wise_man, game_id, wise_man_cost, wise_man_reward, money)
    return next_airport_number, airport_list, money
"""


def is_international_flight(current_location_icao, destination_icao):
    sql = f'select iso_country from airport where ident = "{current_location_icao}" or ident = "{destination_icao}";'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    return result[0][0] != result[1][0] if len(result) == 2 else True


# laske lentolipun hinta etäisyyden ja kansainvälisyyden perusteella
def count_ticket_cost(current_location_icao, destination_icao):
    distance = get_distance_between_airports(current_location_icao, destination_icao)
    international_flight = is_international_flight(current_location_icao, destination_icao)

    price = {
        'international': [(200, 1.00), (500, 0.70), (800, 0.40), (40000, 0.25)],
        'domestic': [(200, 1.25), (500, 0.85), (800, 0.55), (40000, 0.4)],
    }
    price = price['international'] if international_flight else price['domestic']

    for max_distance, multiplier in price:
        if distance < max_distance:
            return 100 + multiplier * distance

# määritä vihje: hae aarremaan ensimmäinen kirjain
def get_clue(game_id):
    sql = f'select airport_ident from game_airports where wise_man_question_id != "NULL" and game_id = {game_id} limit 1;'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    airport_icao = cursor.fetchone()[0]
    country_name = get_country_name(airport_icao)
    hint_letter = country_name[0]
    clue = f'Clue: the treasure is hidden in the country whose first letter is {hint_letter}.'
    return clue

# tarkista, onko lentokentällä tietäjä
def check_if_wise_man(location, game_id):
    sql = (f'select wise_man_question_id from game_airports where airport_ident = "{location}" and '
           f'game_id = {game_id};')
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    # jos on tietäjä, palauttaa kysymyksen id:n, jos ei niin palauttaa 0
    return result[0][0] if result is not None else result
    #if result is not None:
    #    return result[0][0]    #jos on tietäjä, palauttaa kysymyksen id:n, jos ei niin palauttaa 0
    #else:
    #    return result

# hae tietäjän kysymys ja vastaus
def get_wise_man_question_and_answer(location, game_id):
    sql = (f'select wise_man_question_id from game_airports where airport_ident = "{location}" and game_id = {game_id};')
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    question_id = cursor.fetchone()
    question_id = question_id[0]
    sql = (f'select question, answer from wise_man_questions where id = {question_id};')
    cursor = db.get_conn().cursor(buffered=True)
    cursor.execute(sql)
    result = cursor.fetchall()
    return result[0]   # palauttaa monikkona kysymyksen ja vastauksen

# hae tietäjän maksu ja palkinto
def get_wise_man_cost_and_reward(difficulty_level):
    sql = f'select wise_man_cost, wise_man_reward from difficulty where level = "{difficulty_level}";'
    cursor = db.get_conn().cursor(buffered=True)
    cursor.execute(sql)
    result = cursor.fetchone()
    return result

def meet_wise_man_if_exists(wise_man, game_id, wise_man_cost, wise_man_reward, money):
    location = get_current_location(game_id)
    if wise_man is not None:
        question = get_wise_man_question_and_answer(location, game_id)[0]
        answer = get_wise_man_question_and_answer(location, game_id)[1]
        time.sleep(0.5)
        user_input = input(f'You encountered a wise man. Do you want to buy a question? Cost: {wise_man_cost} €.\n'
              f'Input y (yes) or n (no): ')
        if money < wise_man_cost:
            user_input = 'n'
            print('You do not have enough money to buy a question.')
            time.sleep(2)
        user_input = user_input.lower()
        while user_input not in ('y', 'yes', 'n', 'no'):
            user_input = input('Invalid input. Input y (yes) or n (no): ')
        if user_input in ('y', 'yes'):
            answered_value = get_answered_value(game_id, wise_man)[0]
            if answered_value == 1:
                print("You have answered the question already.")
            else:
                money -= wise_man_cost
                update_column_answered(game_id, wise_man)
                time.sleep(0.5)
                print(f'You have {money} €.')
                time.sleep(0.5)
                print(f'Question: {question}')
                user_answer = input('Input answer (a, b or c): ')
                user_answer = user_answer.lower()
                while user_answer not in ('a', 'b', 'c'):
                    user_answer = input('Invalid input. Input answer (a, b or c): ')
                    user_answer = user_answer.lower()
                if user_answer == answer:
                    money += wise_man_reward
                    print(f'Correct! You won {wise_man_reward} €.')
                    time.sleep(0.5)
                    print(f'You have {money} €.')
                    time.sleep(0.5)
                else:
                    print(f'Wrong! Correct answer is {answer}.')
                    time.sleep(0.5)
        elif user_input in ('n', 'no'):
            print('No question this time. Bye!\n')
            time.sleep(0.5)
    else:
        print('No wise man here.')
        time.sleep(0.5)
    return money

# päivitä game_airports-taulun sarake answered
def update_column_answered(game_id, wise_man):
    sql = (f'update game_airports set answered = 1 where game_id = {game_id} and wise_man_question_id = {wise_man};')
    cursor = db.get_conn().cursor(buffered=True)
    cursor.execute(sql)

# hae answered-sarakkeen arvo
def get_answered_value(game_id, wise_man):
    sql = f'select answered from game_airports where game_id = {game_id} and wise_man_question_id = {wise_man};'
    cursor = db.get_conn().cursor(buffered=True)
    cursor.execute(sql)
    result = cursor.fetchone()
    return result

"""
# pelaaja häviää - rahat loppuu tai ei riitä mihinkään lentolippuun
def game_over(game_id):
    message = "Out of money! You cannot afford a ticket. Game over!"
    for char in message:
        print(char, end='', flush=True)
        time.sleep(0.1)
    print()
    sys.exit()

def game_won(game_id, difficulty_level):
    time.sleep(0.5)
    message = '\nYou open the treasure chest and find...'
    message2 = f'\na {get_random_reward(difficulty_level)}!'
    message3 = f'\nCongratulations! You won the game!'
    for char in message:
        print(char, end='', flush=True)
        time.sleep(0.05)
    time.sleep(3)
    for char in message2:
        print(char, end='', flush=True)
        time.sleep(0.25)
    time.sleep(1)
    for char in message3:
        print(char, end='', flush=True)
        time.sleep(0.05)
    sys.exit()
"""

# hakee tietokannasta game-taulusta tietyn pelin tiedot
# (id, screen_name, money, home_airport, location, difficulty_level)
def get_game_info(game_id):
    sql = f'select * from game where id = "{game_id}";'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)

    rows = cursor.fetchall()[0]
    columns = [item[0] for item in cursor.description]

    # muuta data dict (json) muotoon
    data = dict()
    for column, row in zip(columns, rows):
        data.update({column: row})
    return data

def get_co2_consumption(start_icao, end_icao):
    distance = get_distance_between_airports(start_icao, end_icao)
    return math.floor(0.140 * distance)
