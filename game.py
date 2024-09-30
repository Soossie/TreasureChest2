# Treasure Chest (Aarrearkku)

from game_functions import *
import random


# tarina
story = ("You receive a mysterious envelope containing a golden key and an old treasure map.\n"
         "The magical treasure is hidden in one of the countries shown on the map.\n"
         
         "First, you need to find the country where the treasure is located, and then the correct airport.\n"
         "You travel by airplane and need money for the tickets. Along the way, you may encounter\n"
         "wise men who can help you earn more money if you answer their questions correctly.\n")


def start_game():
    # kysyy pelaajan nimen
    #player = input('Input player name: ')
    player = 'Pelaaja1'

    # tulostaa tarinan
    print(f'Treasure Chest\n{story}')

    # esittelee vaikeustasot
    print('Difficulty levels: easy, normal, hard.\n'
          'Difficulty level determines how many countries and airports the game generates.')

    difficulty_level = False
    while not difficulty_level:

        # kysyy käyttäjältä vaikeustason
        #difficulty_level_input = input('Input e for easy, n for normal, h for hard: ')
        difficulty_level_input = 'n'

        # muuttaa käyttäjän syöteen pieniksi kirjaimiksi
        difficulty_level_input = difficulty_level_input.lower()

        # valitsee vaikeustason käyttäjän antaman syötteen perusteella
        if difficulty_level_input in ('e', 'easy'):
            difficulty_level = 'easy'
        elif difficulty_level_input in ('n', 'normal'):
            difficulty_level = 'normal'
        elif difficulty_level_input in ('h', 'hard'):
            difficulty_level = 'hard'
        else:
            print('Invalid input.')

    #print(difficulty_level)

    # määritä pelaajan aloitusrahan määrä vaikeustason mukaan
    money = get_default_money(difficulty_level)

    # arvo 20 maata
    game_countries = get_game_countries(difficulty_level)
    print(f'{len(game_countries)}: {game_countries}')

    # arvo jokaiselle maalle oletuslentokenttä
    countries_with_default_airports = {}

    for country_name in game_countries:
        default_airport = get_default_airport_for_country(country_name)
        countries_with_default_airports.update({country_name: default_airport})
        #print(f'{default_airport} from {country_name} ({get_biggest_airport_size_for_country(country_name)})')
    #print(f'{countries_with_default_airports.items()}')

    # valitse yksi maista aloitusmaaksi ja maan oletuslentokenttä aloituslentokentäksi
    home_country, home_airport = random.choice(list(countries_with_default_airports.items()))
    #print(f'{home_country}, {home_airport}')

    # sijoita pelaajan tiedot game taulukkoon: screen_name, money, home_airport, location, difficulty_level
    # lisää tietokantaan pelaajan maa kenttä (?)
    print(f'\nscreen_name: {player}\nmoney: {money}\nhome_country: {home_country}\nhome_airport: {home_airport}\nlocation: {home_airport}\n'
          f'difficulty_level: {difficulty_level}\n')

    # arvo maa missä aarrearkku on
    treasure_land_country = False
    while not treasure_land_country:
        country = random.choice(list(countries_with_default_airports.keys()))

        # aarremaa ei saa olla pelaajan aloitusmaa
        if country != home_country:
            treasure_land_country = country

    # arvo aarremaalle lentokentät
    treasure_land_airports = get_treasure_land_airports(difficulty_level, treasure_land_country)
    print(treasure_land_airports)

    # arvo maan sisältä aarrearkun lentokenttä
    treasure_land_default_airport = countries_with_default_airports[treasure_land_country]
    treasure_chest_airport = random.choice(treasure_land_airports)
    print(f'{treasure_land_country} {len(treasure_land_airports)}')

    # testaa että aarrearkun lentokenttä ei ole sama kuin maan oletuslentokenttä
    while treasure_land_default_airport == treasure_chest_airport:
        treasure_chest_airport = random.choice(treasure_land_airports)

    print(f'{treasure_land_default_airport}, {treasure_chest_airport}')

    # selvitä kuinka monta tietäjää pelissä on
    wise_man_count = get_wise_man_count(difficulty_level)
    print(wise_man_count)

    # arvo tietäjien lentokentät
    wise_man_airports = [treasure_land_default_airport]
    wise_man_airports.extend(random.choices(list(treasure_land_airports), k=wise_man_count - 1))
    print(wise_man_airports)

    ### ei toimi kunnolla
    # testit
    # listalla ei saa olla aarrearkun lentokenttää, mutta listalla pitää olla maan oletuslentokenttä
    while treasure_chest_airport in wise_man_airports:
        wise_man_airports.remove(treasure_chest_airport)
        print('poista')

        # arvo uusi lentokenttä, testaa että kentällä ei ole jo tietäjää
        new_airport = random.choice(list(treasure_land_airports))
        while new_airport in wise_man_airports:
            new_airport = random.choice(list(treasure_land_airports))

        # lisää arvottu uusi lentokenttä listaan
        wise_man_airports.append(new_airport)
        print('lisää')

    ###

    print(wise_man_airports)


start_game()
