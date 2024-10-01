from pregame import *
from game_functions import *

start_game()

#aloitustilanne
print(f"You're in {home_country} at {home_airport}. You have {money}  Where would you like to travel? Input country number. \n options:")
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