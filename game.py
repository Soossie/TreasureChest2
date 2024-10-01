from pregame import *
from game_functions import *

start_game()

print(f"You're in {home_country} at {home_airport}. You have {money}  Where would you like to travel? Input country number. \n options:")
for i in game_countries:
    print(i)

next_country = input("")
if next_country not in game_countries:
    print("Valitse jokin maista")
    next_country = input("")