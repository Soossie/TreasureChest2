import time
from game_functions import *
game_id = 15
money = 1000
tenthofmoney = money / 10
print("Oh no! You answered wrong and the Treasure is draining you of your money!")
for i in range(10):
    money = int(money - tenthofmoney)
    time.sleep(0.05)
    print(f"{money}€")

print("Travelling to the next airport")
for i in range(30):
    print(".", end="")
    time.sleep(0.2)
print("")
game_over(game_id)