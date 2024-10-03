from pregame import *
from game_functions import *

# tallenna pelin id muuttujaan ja tallenna data tietokantaan (start_game)
game_id = start_game()

connection = mysql.connector.connect(
    host='localhost',
    port=3306,
    database='treasure_chest',
    user='treasure',
    password='chest',
    autocommit=True,
    collation='utf8mb4_general_ci'
)

# hae home_airportin icao-koodi
def get_home_airport_icao(game_id):
    sql = f'select home_airport from game where id = "{game_id}";'
    cursor = connection.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    #print(result)
    return result[0]

# tallenna home_airportin icao-koodi
home_airport_icao = get_home_airport_icao(game_id)

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

# hae kotilentokentän nimi
home_airport = get_airport_name(home_airport_icao)

# hae kotimaan nimi
home_country = get_country_name(home_airport_icao)

# hae aloitusraha
money = get_player_money(game_id)

# aloitustilanne
###tässä pitää hakea kaikki muuttujat tietokannasta, pregame on ne tallentanut sinne
print(f"You're in {home_country} at {home_airport}. You have {money} $. "
      f"Where would you like to travel? Input country number.\noptions: ")

"""
for i in game_countries:
    print(i)

#Pelaaja valitsee ensimmäisen maan, jos oikea niin seuraava vaihe, jos väärä niin looppaa
next_country = input("")
if next_country not in game_countries:
    print("Select one of the countries from the list.")
    next_country = input("")

game_countries.remove(next_country)

print(f"The ticket to {next_country} costs {cost} and the distance there is {distance}. You have {money} left.")

if next_country == treasure_land_country:
    print(f"You're traveling to {next_country} {next_country(get_default_airport_for_country)}. The treasure resides in this country!")
else:
    print(f"You're traveling to {next_country} {next_country(get_default_airport_for_country)}. The treasure is not in this country.")

    print("Where would you like to travel to next? Input country country number. \n options:")
    for i in game_countries:
        print(i)
"""
