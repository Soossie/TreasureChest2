from geopy.units import kilometers
from tabulate import tabulate
from pregame import *
from game_functions import *

# tallenna pelin id muuttujaan ja tallenna data tietokantaan (start_game)
game_id, countries_and_default_airports, game_countries, default_airport, treasure_land_airports = start_game()

#print(game_countries)
#print(game_id)

# tallenna home_airportin icao-koodi
home_airport_icao = get_home_airport_icao(game_id)

# hae kotilentokentän nimi
home_airport = get_airport_name(home_airport_icao)

# hae kotimaan nimi
home_country = get_country_name(home_airport_icao)

# hae aloitusraha
money = get_player_money(game_id)

# aloitustilanne        #######tähän asti toimii
print(f"You're in {home_country} at {home_airport}. You have {money} €. "
#tässä välissä pitää antaa vihje aarremaasta: joku funktio hakee maan 1. kirjaimen tietokannasta?
      f"Where would you like to travel?\nOptions: ")

country_list = []

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
        if airport_icao1 != airport_icao2:
            i += 1
            country_list.append([i, country, distance, ticket_cost])
            # print(f'{i}. {country}, {distance} km, ticket costs {ticket_cost} €.\n')
            # country_list.append(country)
    print(tabulate(country_list, headers=["Number", "Country", "Distance (km)", "Ticket cost (€)"], tablefmt="pretty"))

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
        if airport_icao1 != airport_icao2:
            i += 1
            airport_list.append([i, airport, distance, ticket_cost])
            # print(f'{i}. {airport}, {distance} km, ticket costs {ticket_cost} €.\n')
            # airport_list.append(airport)
    print(tabulate(airport_list, headers=["Number", "Airport", "Distance (km)", "Ticket cost (€)"], tablefmt="pretty"))

#^tulostuvaan taulukkoon pitää lisätä sarake "Enough money for the ticket (x)" tms.

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

# pelaaja valitsee ensimmäisen maan, jos oikea niin seuraava vaihe, jos väärä niin looppaa
travel_between_countries()
next_country = int(input("Input country number: "))
next_country -= 1
if next_country not in range(len(country_list)):
    print("Select one of the countries from the list: ")
    next_country = input("")
money -= ticket_cost    #päivitä pelaajan rahamäärä (money - ticket_cost)
print(f"The ticket to {country_list[next_country]} costs {ticket_cost} and the distance there is {distance}. You have {money} left.")

"""
game_countries.remove(next_country)


if next_country == treasure_land_country:
    print(f"You're traveling to {next_country} {next_country(get_default_airport_for_country)}. The treasure resides in this country!")
else:
    print(f"You're traveling to {next_country} {next_country(get_default_airport_for_country)}. The treasure is not in this country.")

#tähän pitää laittaa taas vihje aarremaasta (1. kirjain)

    print("Where would you like to travel to next? Input country country number. \n options:")
    for i in game_countries:
        print(i)
"""

