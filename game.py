from geopy.units import kilometers
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

# hae wise man hinta
wise_man_cost = get_wise_man_cost_and_reward(difficulty_level)[0]

# hae wise man palkinto
wise_man_reward = get_wise_man_cost_and_reward(difficulty_level)[1]

# hae vihje
want_clue = input("Do you want a clue? Input y (yes) or n (no): ")
if want_clue == 'y' or 'yes':
    clue = get_clue(game_id)
else:
    clue = ''

# pari oletusarvoa muuttujille
next_country_number = 45
country_list = []
next_airport_number = 45
airport_list = []

# aloitustilanne
# hae vihje

print(treasure_land_country) # debug
print(treasure_chest_airport) # debug
print(f'\nYou are in {home_country} at {home_airport}. You have {money} €. '
      f'Where would you like to travel?\n{clue}\nOptions: ')
next_country_number, country_list = travel_between_countries(game_id, game_countries, money)

#looppaa kunnes pelaaja saapuu aarremaahan
while country_list[next_country_number][1] != treasure_land_country:
    airport_name = get_airport_name(get_default_airport_ident_for_country(game_id, (country_list[next_country_number][1])))
    print(f'You have landed at {airport_name}. The treasure is not in this country.')
    print(f'Where would you like to travel next?\n{clue}\nOptions: ')
    next_country_number, country_list = travel_between_countries(game_id, game_countries, money)

# muutos maiden välillä liikkumisesta maiden sisällä liikkumiseen, kun oikeassa maassa
print(f'You have landed at {get_country_name(get_default_airport_ident_for_country(game_id, country_list[next_country_number][1]))}. The treasure is in this country!')
location = get_current_location(game_id)
wise_man = check_if_wise_man(location, game_id)
meet_wise_man_if_exists(wise_man, game_id, wise_man_cost, wise_man_reward, money)
print('Now you must find the treasure chest hidden in one of the airports. Where would you like to travel next?\nOptions: ')
print(f'sijainti aarremaassa: {location}') # debug
airport_list = travel_inside_country(game_id, treasure_land_airports, money, wise_man_cost, wise_man_reward)

# looppaa kunnes pelaaja saapuu aarrelentokentälle
while airport_list[next_airport_number][1] != treasure_chest_airport:
    print(f'You have landed at {airport_list[next_airport_number][1]}. The treasure chest is not here.')
    print('Where would you like to travel next?\nOptions: ')
    airport_list = travel_inside_country(game_id, treasure_land_airports, money, wise_man_cost, wise_man_reward)

# pelaaja voittaa
print(f'You have found the treasure chest at {get_airport_name(get_current_location(game_id))}! Congratulations!') # voittoviesti tähän