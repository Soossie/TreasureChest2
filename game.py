from geopy.units import kilometers
from tabulate import tabulate
from pregame import *
from game_functions import *

# tallenna muuttujat ja tallenna data tietokantaan
(game_id, countries_and_default_airports, game_countries, default_airport, treasure_land_airports,
 difficulty_level, treasure_land_country, treasure_chest_airport) = start_game()

#print(game_countries)
#print(game_id)

# hae kotilentokentän icao-koodi
home_airport_icao = get_home_airport_icao(game_id)

# hae kotilentokentän nimi
home_airport = get_airport_name(home_airport_icao)

# hae kotimaan nimi
home_country = get_country_name(home_airport_icao)

# hae aloitusraha
money = get_player_money(game_id)

# määritä vihje: hae aarremaan ensimmäinen kirjain
def get_clue():
    sql = f'select airport_ident from game_airports where wise_man_question_id != "NULL" and game_id = {game_id} limit 1;'
    cursor = connection.cursor()
    cursor.execute(sql)
    airport_icao = cursor.fetchone()[0]
    country_name = get_country_name(airport_icao)
    hint_letter = country_name[0]
    clue = (f'Clue: the treasure is hidden in the country whose first letter is {hint_letter}.')
    return clue

def get_country_name(airport_icao):
    sql = (f'select country.name from country inner join airport on country.iso_country = airport.iso_country '
           f'where ident = "{airport_icao}";')
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    #print(result)
    return result[0]

# matkusta maiden välillä
def travel_between_countries():
    i = 0
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

airport_list = []

# matkusta maan sisällä
def travel_inside_country():
    i = 0
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

# hae vihje
clue = get_clue()
print(treasure_land_country)
print(treasure_chest_airport)

# aloitustilanne
print(f'\nYou are in {home_country} at {home_airport}. You have {money} €. '
      f'Where would you like to travel?\n{clue}\nOptions: ')
country_list = []

# pelaaja valitsee ensimmäisen maan. Jos syöte on väärä (ei listalla), pelaaja valitsee uudelleen
travel_between_countries()
next_country = int(input('Input country number: ')) #MITÄ JOS KÄYTTÄJÄ SYÖTTÄÄ KIRJAIMEN?
next_country -= 1

while next_country not in range(len(country_list)): # taitaa loopata ikuisesti atm
    next_country = int(input("Invalid input. Select one of the countries from the list: "))
    next_country -= 1

# päivitä pelaajan rahamäärä (money - ticket_cost)
def current_ticket_cost_between_countries():
    next_default_airport = get_default_airport_for_country(next_country)
    current_ticket_cost = count_ticket_cost_between_countries(get_distance_between_airports(get_current_location(game_id), next_default_airport))
    return current_ticket_cost

# päivittää pelaajan rahan
money -= country_list[next_country][3]

country1 = get_country_name(get_current_location(game_id))
country2 = country_list[next_country][1]
ticket_price = country_list[next_country][3]
distance1 = country_list[next_country][2]

print(f'The ticket from {country1} to {country2} costs {ticket_price} € and the distance there is {distance1} km. You have {money} € left.\n...')
update_current_location(game_id, get_airport_ident_from_name(get_default_airport_for_country(country_list[next_country][1])))

airport_name = get_default_airport_for_country(next_country)
print(airport_name) ###tulostuu False, joku next_countryssa on väärin??

country1 = get_country_name(get_current_location(game_id))
country2 = country_list[next_country][1]
ticket_price = country_list[next_country][3]
distance1 = country_list[next_country][2]

#looppaa kunnes pelaaja saapuu aarremaahan               #country2-kohdassa tulostuu joskus sama arvo kuin country1 ???
while country_list[next_country][1] != treasure_land_country:
    print(f'You have landed at {airport_name}. The treasure is not in this country.')
    print(f'Where would you like to travel next?\n{clue}\nOptions: ')
    country_list.clear()
    travel_between_countries()
    next_country = int(input('Input country number: '))
    next_country -= 1
    money -= country_list[next_country][3]
    print(f'The ticket from {country1} to {country2} costs {ticket_price} € and the distance there is {distance1} km. You have {money} € left.\n...')
    update_current_location(game_id, get_airport_ident_from_name(get_default_airport_for_country(country_list[next_country][1])))
    while next_country not in range(len(country_list)): # taitaa loopata ikuisesti atm
        next_country = int(input("Select one of the countries from the list: "))
        next_country -= 1

###tästä alkaa tietäjäjutut

location = get_current_location(game_id)        #toimiiko tämä kun matkustaa maan sisällä??
# tarkista, onko lentokentällä tietäjä
def check_if_wise_man(location, game_id):
    sql = (f'select wise_man_question_id from game_airports where airport_ident = "{location}" and '
           f'game_id = "{game_id}";')
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result[0]    #jos on tietäjä, palauttaa kysymyksen id:n, jos ei niin palauttaa None

# hae tietäjän kysymys ja vastaus     ###toimii, jos locationissa on kysymys, muuten error?
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

wise_man_cost = get_wise_man_cost_and_reward(difficulty_level)[0]
wise_man_reward = get_wise_man_cost_and_reward(difficulty_level)[1]
money = money

#tietäjän kohtaaminen           #money ei ole määritelty tms, miksi??
def meet_wise_man_if_exists(wise_man):
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

###tietäjähommelit loppuu


# muutos maiden välillä liikkumisesta maiden sisällä liikkumiseen, kun oikeassa maassa
print(f'You have landed at {get_default_airport_for_country(next_country)}. The treasure is in this country!')
wise_man = check_if_wise_man(location, game_id)
meet_wise_man_if_exists(wise_man)
print('Now you must find the treasure chest hidden in one of the airports. Where would you like to travel next?\nOptions: ')
airport_list.clear()
travel_inside_country()
next_airport = int(input('Input airport number: '))
next_airport -= 1

while next_airport not in range(len(airport_list)): # taitaa loopata ikuisesti atm
    next_airport = int(input('Select one of the airports from the list: '))
    next_airport -= 1

# looppaa kunnes pelaaja saapuu aarrelentokentälle
while airport_list[next_airport][1] != treasure_chest_airport:
    print(f'You have landed at {get_airport_name(get_current_location(game_id))}. The treasure is not in this airport.')
    wise_man = check_if_wise_man(location, game_id)
    meet_wise_man_if_exists(wise_man)
    print('Where would you like to travel next?\nOptions: ')
    airport_list.clear()
    travel_inside_country()
    next_airport = int(input('Input airport number: '))
    next_airport -= 1
    while next_airport not in range(len(airport_list)): # taitaa loopata ikuisesti atm
        next_airport = int(input('Select one of the airports from the list: '))
        next_airport -= 1
    money -= airport_list[next_airport][3]
    print(f'The ticket from {get_airport_name(get_current_location(game_id))} to {airport_list[next_airport][1]} costs {airport_list[next_airport][3]} € and the distance there is {airport_list[next_airport][2]} km. You have {money} € left.\n...')
    update_current_location(game_id, get_airport_ident_from_name(country_list[next_country][1])) # tulee error kun pääsee aarrelentokentälle

# pelaaja voittaa
print(f'You have found the treasure chest at {get_airport_name(get_current_location(game_id))}! Congratulations!') # voittoviesti tähän

# rahat loppuu tai ei riitä mihinkään lentolippuun
print(f'Out of money! You can not afford a ticket. Game over!')
