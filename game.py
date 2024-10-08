from geopy.units import kilometers
from pregame import *
from game_functions import *
import time

###
# to do:
# korjaa kysymyksissä portugalin pääkaupunki
# tietäjä antaa kysymyksen vaikka pelaajalla ei ole riittävästi rahaa (pelaajan raha menee miinukselle)
###

# tallenna muuttujat ja tallenna data tietokantaan
(game_id, countries_and_default_airports, game_countries, default_airport, treasure_land_airports,
 difficulty_level, treasure_land_country, treasure_chest_airport, want_clue) = start_game()

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

# hae tietäjän hinta
wise_man_cost = get_wise_man_cost_and_reward(difficulty_level)[0]

# hae tietäjän palkinto
wise_man_reward = get_wise_man_cost_and_reward(difficulty_level)[1]

# aloitustilanne
print(treasure_land_country) # debug
print(treasure_chest_airport) # debug

# hae vihje jos pelaaja haluaa
if want_clue == True:
    clue = get_clue(game_id)
else:
    clue = ''



print(f'\nYou are in {home_country} at {home_airport}. You have {money} €.')
time.sleep(2)
print(f'Where would you like to travel?')
print(clue)
time.sleep(2)
print(f'Options: ')
time.sleep(0.5)
next_country_number, country_list, money = travel_between_countries(game_id, game_countries, money)

#looppaa kunnes pelaaja saapuu aarremaahan
while country_list[next_country_number][1] != treasure_land_country:
    if money <= 0:
        game_over(game_id)
    airport_name = get_airport_name(get_default_airport_ident_for_country(game_id, (country_list[next_country_number][1])))
    print(f'\nYou have landed at {airport_name}. The treasure is not in this country.')
    time.sleep(0.5)
    print(f'Where would you like to travel next?')
    time.sleep(0.5)
    print(clue)
    time.sleep(0.5)
    print(f'Options: ')
    next_country_number, country_list, money = travel_between_countries(game_id, game_countries, money)

# muutos maiden välillä liikkumisesta maiden sisällä liikkumiseen, kun oikeassa maassa
print(f'\nYou have landed at {get_airport_name(get_default_airport_ident_for_country(game_id, country_list[next_country_number][1]))}. You have {money} € left. The treasure is in this country!')
time.sleep(0.5)
location = get_current_location(game_id)
wise_man = check_if_wise_man(location, game_id)
meet_wise_man_if_exists(wise_man, game_id, wise_man_cost, wise_man_reward, money)
print('Now you must find the treasure chest hidden in one of the airports. Where would you like to travel next?')
time.sleep(2)
print('Options: ')
time.sleep(0.5)
# print(f'sijainti aarremaassa: {location}') # debug
next_airport_number, airport_list, money = travel_inside_country(game_id, treasure_land_airports, money, wise_man_cost, wise_man_reward)

# looppaa kunnes pelaaja saapuu aarrelentokentälle
while airport_list[next_airport_number][1] != treasure_chest_airport:
    if money <= 0:
        game_over(game_id)
    time.sleep(0.5)
    print(f'You have landed at {airport_list[next_airport_number][1]}. You have {money} € left. The treasure chest is not here.')
    time.sleep(0.5)
    print('Where would you like to travel next?')
    time.sleep(0.5)
    print('Options: ')
    next_airport_number, airport_list, money = travel_inside_country(game_id, treasure_land_airports, money, wise_man_cost, wise_man_reward)

# pelaaja voittaa
print(f'You have found the treasure chest at {get_airport_name(get_current_location(game_id))}! Congratulations!\n You have {money} € left.')
time.sleep(2)
game_won(game_id, difficulty_level)

# ei ehtinyt tehdä viimeistä kysymystä
"""
print('However, you must answer the the Chest\'s riddle to claim the treasure or else the treasure will be lost forever!\n')
time.sleep(1)
question = input('Final question: x or y?')
if question == 'x':
    print('Correct! The treasure is yours!')
    time.sleep(1)
    print('')
    game_won(game_id, difficulty_level)
else:
    tenthofmoney = money / 10
    print("Oh no! You answered wrong and the Treasure is draining you of your money!")
    for i in range(10) and money > 0:
        money = int(money - tenthofmoney)
        time.sleep(0.5)
        print(f"{money}€")
    game_over(game_id)
"""