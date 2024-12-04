from database import Database
import requests
import requests.exceptions

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
def input_player_info(screen_name, money, home_airport, location, difficulty_level, co2_consumed):
    sql = (f'insert into game(screen_name, money, home_airport, location, difficulty_level, co2_consumed) '
           f'values("{screen_name}", "{money}", "{home_airport}", "{location}", "{difficulty_level}", "{co2_consumed}");')
    cursor = db.get_conn().cursor()
    cursor.execute(sql)

def save_airport_to_game_airports(game_id, airport_ident, wise_man_question_id, answered, has_treasure, is_default_airport, has_advice_guy, visited):
    # parannusehdotus: yhdistä kyselyt yhdeksi. ongelma on sijoittaa NULL arvo tietokantaan, mutta se on myös jo oletusarvo

    if not wise_man_question_id:
        # ei tietäjän kysymystä
        sql = (f'insert into game_airports(game_id, airport_ident, answered, has_treasure, is_default_airport, has_advice_guy, visited) '
               f'values("{game_id}", "{airport_ident}", "{answered}", "{has_treasure}", "{is_default_airport}", "{has_advice_guy}", "{visited}");')

    else:
        sql = (f'insert into game_airports(game_id, airport_ident, wise_man_question_id, answered, has_treasure, is_default_airport, has_advice_guy, visited) '
               f'values("{game_id}", "{airport_ident}", "{wise_man_question_id}", "{answered}", "{has_treasure}", "{is_default_airport}", "{has_advice_guy}", "{visited}");')

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

# hae käytössä oleva raha
def get_player_money(game_id):
    sql = f'select money from game where id = "{game_id}";'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]

# hae pelaajan nykyinen sijainti
def get_current_location(game_id):
    sql = f'select location from game where id = "{game_id}";'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]

# hae palkinto, arvo vaikeustason mukaan
def get_random_reward(difficulty_level):
    sql = f'select name, id from rewards where difficulty_level = "{difficulty_level}" order by rand() limit 1;'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]

# päivitä sijainti
def update_current_location(game_id, new_location_icao):
    sql = f'update game set location = "{new_location_icao}" where id = "{game_id}";'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)

# hae tietäjän maksu ja palkinto
def get_wise_man_cost_and_reward(difficulty_level):
    sql = f'select wise_man_cost, wise_man_reward from difficulty where level = "{difficulty_level}";'
    cursor = db.get_conn().cursor(buffered=True)
    cursor.execute(sql)
    result = cursor.fetchone()
    return result

"""
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
"""

# päivitä game_airports-taulun sarake answered
def update_column_answered(game_id, wise_man):
    sql = f'update game_airports set answered = 1 where game_id = {game_id} and wise_man_question_id = {wise_man};'
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

def add_or_remove_money(game_id, amount, add=False, remove=False):
    if not add and not remove:
        return
    money = get_player_money(game_id)
    new_money = money + amount if add else money - amount

    sql = f'update game set money = {new_money} where id = "{game_id}";'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)

# hae advice guy rahasumma
def get_advice_guy_reward(difficulty_level):
    sql = (f'select advice_guy_reward from difficulty '
           f'where level = "{difficulty_level}";')
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    advice_guy_reward = cursor.fetchone()[0]
    return advice_guy_reward

# hae advice guy määrät
def get_advice_guy_count(difficulty_level):
    sql = (f'select advice_guys_in_countries, advice_guys_in_airports from difficulty '
           f'where level = "{difficulty_level}";')
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchall()
    advice_guys_in_countries = result[0][0]
    advice_guys_in_airports = result[0][1]
    return advice_guys_in_countries, advice_guys_in_airports

# päivitä game_airports-taulun sarake visited
def update_column_visited(game_id, location):
    sql = f'update game_airports set visited = 1 where game_id = {game_id} and airport_ident = "{location}";'
    cursor = db.get_conn().cursor(buffered=True)
    cursor.execute(sql)

# hae visited-sarakkeen arvo
def get_visited_value(game_id, airport_icao):
    sql = f'select visited from game_airports where game_id = {game_id} and airport_ident = "{airport_icao}";'
    cursor = db.get_conn().cursor(buffered=True)
    cursor.execute(sql)
    result = cursor.fetchone()
    return result

# hae neuvo
def get_advice():
    url = "https://api.adviceslip.com/advice"

    try:
        response = requests.get(url)
    except requests.exceptions.RequestException:
        print("Error. Can't get the advice.")
        return

    if response.status_code != 200:
        print(f"Error {response.status_code}.")
        return

    response_body = response.json()             # muutetaan data pythonin tietorakenteeksi
    return response_body["slip"]["advice"]

def get_player_co2_consumed(game_id):
    sql = f'select co2_consumed from game where id = "{game_id}";'
    cursor = db.get_conn().cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]

# päivitä game tauluun co2
def update_co2_consumed(game_id, co2_consumed):
    co2 = get_player_co2_consumed(game_id)
    new_co2 = int(co2) + int(co2_consumed)

    sql = f'update game set co2_consumed = {new_co2} where id = {game_id};'
    cursor = db.get_conn().cursor(buffered=True)
    cursor.execute(sql)

def get_treasure_land_country_name(game_id):
    sql = (f'select country.name from country '
           f'inner join airport on airport.iso_country = country.iso_country '
           f'inner join game_airports on game_airports.airport_ident = airport.ident '
           f'where game_airports.has_treasure=1 and game_airports.game_id={game_id};')
    cursor = db.get_conn().cursor(buffered=True)
    cursor.execute(sql)
    treasure_airport_name = cursor.fetchone()[0]
    return treasure_airport_name
