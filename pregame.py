# Treasure Chest (Aarrearkku)
import itertools
from game_functions import *
import random


# tarina
def get_story():
    story = ("You receive a mysterious envelope containing a golden key and an old treasure map.\n"
         "The magical treasure is hidden in one of the countries shown on the map.\n"

         "First, you need to find the country where the treasure is located, and then the correct airport.\n"
         "You travel by airplane and need money for the tickets. Along the way, you may encounter\n"
         "wise men who can help you earn more money if you answer their questions correctly.\n")
    return story


def start_game():
    print(f'Treasure Chest\n{get_story()}')

    # kysyy pelaajan nimen
    player = input('Input player name: ')
    #player = 'Pelaaja'
    while screen_name_exists(player):
        player = input('Player name exists. Input a new name: ')

    # esittelee vaikeustasot
    print('Difficulty levels: easy, normal, hard.\n'
          'Difficulty level determines how many countries and airports the game generates.')

    difficulty_level = False
    while not difficulty_level:
        # kysyy käyttäjältä vaikeustason
        difficulty_level_input = input('Choose difficulty level. Input e for easy, n for normal, h for hard: ')
        #difficulty_level_input = 'n'

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

    # print(difficulty_level)

    # määritä pelaajan aloitusrahan määrä vaikeustason mukaan
    money = get_default_money(difficulty_level)

    # arvo 20 maata
    game_countries = get_game_countries(difficulty_level)
    #print(f'{len(game_countries)}: {game_countries}')

    # arvo jokaiselle maalle oletuslentokenttä
    countries_and_default_airports = {}

    for country_name in game_countries:
        default_airport = get_default_airport_for_country(country_name)
        countries_and_default_airports.update({country_name: default_airport})
        # print(f'{default_airport} from {country_name} ({get_biggest_airport_size_for_country(country_name)})')
    # print(f'{countries_and_default_airports.items()}')

    # valitse yksi maista aloitusmaaksi ja maan oletuslentokenttä aloituslentokentäksi
    home_country, home_airport = random.choice(list(countries_and_default_airports.items()))
    # print(f'{home_country}, {home_airport}')

    #print(f'\nscreen_name: {player}\nmoney: {money}\nhome_country: {home_country}\nhome_airport: {home_airport}\n'
    #      f'location: {home_airport}\ndifficulty_level: {difficulty_level}\n')

    # arvo maa missä aarrearkku on
    treasure_land_country = False
    while not treasure_land_country:
        country = random.choice(list(countries_and_default_airports.keys()))

        # aarremaa ei saa olla pelaajan aloitusmaa
        if country != home_country:
            treasure_land_country = country

    # arvo aarremaalle lentokentät
    treasure_land_airports = get_treasure_land_airports(difficulty_level, treasure_land_country)
    #print(treasure_land_airports)

    # arvo maan sisältä aarrearkun lentokenttä
    treasure_land_default_airport = countries_and_default_airports[treasure_land_country]
    treasure_chest_airport = random.choice(treasure_land_airports)
    #print(f'{treasure_land_country} {len(treasure_land_airports)}')

    # testaa että aarrearkun lentokenttä ei ole sama kuin maan oletuslentokenttä
    while treasure_land_default_airport == treasure_chest_airport:
        treasure_chest_airport = random.choice(treasure_land_airports)

    #print(f'\nAarremaan oletuslentokenttä [{treasure_land_default_airport} ({get_airport_ident_from_name(treasure_land_default_airport)})]\n'
    #      f'Aarrearkun lentokenttä [{treasure_chest_airport} ({get_airport_ident_from_name(treasure_chest_airport)})]\n')

    # selvitä kuinka monta tietäjää pelissä on
    wise_man_count = get_wise_man_count(difficulty_level)
    #print(wise_man_count)

    # arvo tietäjien lentokentät
    wise_man_airports = [treasure_land_default_airport]
    wise_man_airports.extend(random.sample(list(treasure_land_airports), k=wise_man_count - 1))
    # print(wise_man_airports)

    # listalla ei saa olla aarrearkun lentokenttää, mutta listalla pitää olla maan oletuslentokenttä
    # poista aarrearkun lentokenttä tietäjien lentokentistä jos se on listassa
    while treasure_chest_airport in wise_man_airports:
        wise_man_airports.remove(treasure_chest_airport)
        #print(f'poista {treasure_chest_airport}')

        # arvo uusi lentokenttä, testaa että kenttä ei ole jo listassa
        new_airport = random.choice(list(treasure_land_airports))
        while new_airport in wise_man_airports:
            new_airport = random.choice(list(treasure_land_airports))

        # lisää arvottu uusi lentokenttä listaan
        wise_man_airports.append(new_airport)
        #print(f'lisää {new_airport}')

    #print(wise_man_airports)
    #print(home_airport)

    home_airport_ident = get_airport_ident_from_name(home_airport)
    #print(home_airport_ident)

    # tallenna pelaajan tiedot game tauluun
    input_player_info(player, money, home_airport_ident, home_airport_ident, difficulty_level)

    # tallenna tietokantaan pelin lentokentät
    game_id = get_screen_name_game_id(player)
    #print(game_id)

    # tallenna oletuslentokenttien tiedot tietokantaan
    for airport in itertools.chain(countries_and_default_airports.values(), treasure_land_airports):
        #print(f'{airport} ({airport in treasure_land_airports})')

        # hae tallennettavat arvot
        airport_ident = get_airport_ident_from_name(airport)

        question_id = False  #get_random_unused_question_id(game_id)
        if airport in wise_man_airports:
            #print('wise man airport')
            if airport == treasure_land_default_airport:
                question_id = get_random_question_id()
            else:
                question_id = get_random_unused_question_id(game_id)

        answered = 0
        has_treasure = 1 if bool(airport == treasure_chest_airport) else 0
        is_default_airport = 1 if bool(airport in countries_and_default_airports.values()) else 0

        #print(f'-\n{game_id}\n{airport_ident}\n{question_id}\n{answered}\n{has_treasure}\n{is_default_airport}\n')
        save_airport_to_game_airports(game_id, airport_ident, question_id, answered, has_treasure, is_default_airport)

    return game_id

#start_game()   #tämä pitää poistaa valmiissa pelissä
