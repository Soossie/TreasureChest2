import itertools
from game_functions import *
import random


# tarina
def get_story():
    story = ('You receive a mysterious envelope containing a golden key and an old treasure map.\n'
         'The magical treasure is hidden in one of the countries shown on the map.\n\n'

         'First, you need to find the country where the treasure is located, and then the correct airport.\n'
         'You travel by airplane and need money for the tickets. Along the way, you may encounter\n'
         'wise men who can help you earn more money if you answer their questions correctly.\n')
    return story

# säilytä toistaiseksi varmuuden vuoksi
"""
# pelin aloitus
def start_game():
    print(f'Treasure Chest\n\n{get_story()}')

    # kysyy pelaajan nimen
    player = input('Input player name: ')
    while screen_name_exists(player):
        player = input('Player name exists. Input a new name: ')

    # esittelee vaikeustasot
    print('\nDifficulty levels: easy, normal, hard.\n'
          'Difficulty level determines how many countries and airports the game generates.')

    difficulty_level = False
    while not difficulty_level:
        # kysyy käyttäjältä vaikeustason ja muuttaa syöteen pieniksi kirjaimiksi
        difficulty_level_input = input('Choose difficulty level. Input e (easy), n (normal), h (hard): ').lower()

        # valitsee vaikeustason käyttäjän antaman syötteen perusteella
        if difficulty_level_input in ('e', 'easy'):
            difficulty_level = 'easy'
        elif difficulty_level_input in ('n', 'normal'):
            difficulty_level = 'normal'
        elif difficulty_level_input in ('h', 'hard'):
            difficulty_level = 'hard'
        else:
            print('Invalid input.')

    # hae vihje
    want_clue = input("Do you want a clue? Input y (yes) or n (no): ")
    if want_clue in ('y', 'yes'):
        want_clue = True
    else:
        want_clue = False

    # määritä pelaajan aloitusrahan määrä vaikeustason mukaan
    money = get_default_money(difficulty_level)

    # arvo maat
    game_countries = get_game_countries(difficulty_level)

    # arvo jokaiselle maalle oletuslentokenttä
    countries_and_default_airport_icaos = {}

    for country_name in game_countries:
        default_airport_icao = get_random_default_airport_icao_for_country(country_name)
        countries_and_default_airport_icaos.update({country_name: default_airport_icao})

    # valitse yksi maista aloitusmaaksi ja maan oletuslentokenttä aloituslentokentäksi
    home_country, home_airport_icao = random.choice(list(countries_and_default_airport_icaos.items()))

    # lisää aloitusmaa pelaajan käytyjen maiden listaan
    add_home_country_to_visited_country_list(home_country)

    # arvo aarremaa
    treasure_land_country, treausure_land_default_airport_icao = False, False
    while not treasure_land_country:
        country = random.choice(list(countries_and_default_airport_icaos.keys()))

        # aarremaa ei saa olla pelaajan aloitusmaa
        if country != home_country:
            treasure_land_country = country

    # arvo aarremaalle lentokentät
    treasure_land_airport_icaos = get_treasure_land_airport_icaos(difficulty_level, treasure_land_country,
                                                                  treausure_land_default_airport_icao)

    # arvo maan sisältä aarrearkun lentokenttä
    treasure_land_default_airport_icao = countries_and_default_airport_icaos[treasure_land_country]
    treasure_chest_airport_icao = random.choice(treasure_land_airport_icaos)

    # testaa että aarrearkun lentokenttä ei ole sama kuin maan oletuslentokenttä
    while treasure_land_default_airport_icao == treasure_chest_airport_icao:
        treasure_chest_airport_icao = random.choice(treasure_land_airport_icaos)

    # selvitä kuinka monta tietäjää pelissä on
    wise_man_count = get_wise_man_count(difficulty_level)

    # arvo tietäjien lentokentät
    wise_man_airports = [treasure_land_default_airport_icao]
    wise_man_airports.extend(random.sample(list(treasure_land_airport_icaos), k=wise_man_count - 1))

    # listalla ei saa olla aarrearkun lentokenttää, mutta listalla pitää olla maan oletuslentokenttä
    # poista aarrearkun lentokenttä tietäjien lentokentistä jos se on listassa
    while treasure_chest_airport_icao in wise_man_airports:
        wise_man_airports.remove(treasure_chest_airport_icao)

        # arvo uusi lentokenttä, testaa että kenttä ei ole jo listassa
        new_airport = random.choice(list(treasure_land_airport_icaos))
        while new_airport in wise_man_airports:
            new_airport = random.choice(list(treasure_land_airport_icaos))

        # lisää arvottu uusi lentokenttä listaan
        wise_man_airports.append(new_airport)

    # tallenna pelaajan tiedot game tauluun
    input_player_info(player, money, home_airport_icao, home_airport_icao, difficulty_level)

    # hae pelin id pelaajan nimen perusteella
    game_id = get_game_id_by_screen_name(player)

    # tallenna oletuslentokenttien tiedot tietokantaan
    for airport_icao in itertools.chain(countries_and_default_airport_icaos.values(), treasure_land_airport_icaos):

        question_id = False
        if airport_icao in wise_man_airports:
            if airport_icao == treasure_land_default_airport_icao:
                question_id = get_random_question_id()
            else:
                question_id = get_random_unused_question_id(game_id)

        answered = 0
        has_treasure = 1 if bool(airport_icao == treasure_chest_airport_icao) else 0
        is_default_airport = 1 if bool(airport_icao in countries_and_default_airport_icaos.values()) else 0

        save_airport_to_game_airports(game_id, airport_icao, question_id, answered, has_treasure, is_default_airport)

    game_info = {
        'game_id': game_id,
        'player_name': player,
        'difficulty_level': difficulty_level,
        'want_clue': want_clue,
        'default_airport_icao': default_airport_icao,
        'countries_and_default_airport_icaos': countries_and_default_airport_icaos,
        'treasure_land_country': treasure_land_country,
        'treasure_land_airport_icaos': treasure_land_airport_icaos,
        'treasure_chest_airport_icao': treasure_chest_airport_icao,
    }
    return game_info
"""
