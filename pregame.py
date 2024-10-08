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
        # kysyy käyttäjältä vaikeustason
        difficulty_level_input = input('Choose difficulty level. Input e (easy), n (normal), h (hard): ')

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

    # hae vihje
    want_clue = input("Do you want a clue? Input y (yes) or n (no): ")
    if want_clue in ['y', 'yes']:
        want_clue = True
    else:
        want_clue = False

    # määritä pelaajan aloitusrahan määrä vaikeustason mukaan
    money = get_default_money(difficulty_level)

    # arvo maat
    game_countries = get_game_countries(difficulty_level)

    # arvo jokaiselle maalle oletuslentokenttä
    countries_and_default_airports = {}

    for country_name in game_countries:
        default_airport = get_random_default_airport_for_country(country_name)
        countries_and_default_airports.update({country_name: default_airport})

    # valitse yksi maista aloitusmaaksi ja maan oletuslentokenttä aloituslentokentäksi
    home_country, home_airport = random.choice(list(countries_and_default_airports.items()))

    # lisää aloitusmaa pelaajan käytyjen maiden listaan
    add_home_country_to_visited_country_list(home_country)

    # arvo aarremaa
    treasure_land_country, treausure_land_default_airport_ident = False, False
    while not treasure_land_country:
        country = random.choice(list(countries_and_default_airports.keys()))

        # aarremaa ei saa olla pelaajan aloitusmaa
        if country != home_country:
            treasure_land_country = country
            treausure_land_default_airport_ident = get_airport_ident_from_name(countries_and_default_airports[country])

    # arvo aarremaalle lentokentät
    treasure_land_airports = get_treasure_land_airports(difficulty_level, treasure_land_country,
                                                        treausure_land_default_airport_ident)

    # arvo maan sisältä aarrearkun lentokenttä
    treasure_land_default_airport = countries_and_default_airports[treasure_land_country]
    treasure_chest_airport = random.choice(treasure_land_airports)

    # testaa että aarrearkun lentokenttä ei ole sama kuin maan oletuslentokenttä
    while treasure_land_default_airport == treasure_chest_airport:
        treasure_chest_airport = random.choice(treasure_land_airports)

    # selvitä kuinka monta tietäjää pelissä on
    wise_man_count = get_wise_man_count(difficulty_level)

    # arvo tietäjien lentokentät
    wise_man_airports = [treasure_land_default_airport]
    wise_man_airports.extend(random.sample(list(treasure_land_airports), k=wise_man_count - 1))

    # listalla ei saa olla aarrearkun lentokenttää, mutta listalla pitää olla maan oletuslentokenttä
    # poista aarrearkun lentokenttä tietäjien lentokentistä jos se on listassa
    while treasure_chest_airport in wise_man_airports:
        wise_man_airports.remove(treasure_chest_airport)

        # arvo uusi lentokenttä, testaa että kenttä ei ole jo listassa
        new_airport = random.choice(list(treasure_land_airports))
        while new_airport in wise_man_airports:
            new_airport = random.choice(list(treasure_land_airports))

        # lisää arvottu uusi lentokenttä listaan
        wise_man_airports.append(new_airport)

    home_airport_ident = get_airport_ident_from_name(home_airport)

    # tallenna pelaajan tiedot game tauluun
    input_player_info(player, money, home_airport_ident, home_airport_ident, difficulty_level)

    # tallenna tietokantaan pelin lentokentät
    game_id = get_screen_name_game_id(player)

    # tallenna oletuslentokenttien tiedot tietokantaan
    for airport in itertools.chain(countries_and_default_airports.values(), treasure_land_airports):

        # hae tallennettavat arvot
        airport_ident = get_airport_ident_from_name(airport)

        question_id = False
        if airport in wise_man_airports:
            if airport == treasure_land_default_airport:
                question_id = get_random_question_id()
            else:
                question_id = get_random_unused_question_id(game_id)

        answered = 0
        has_treasure = 1 if bool(airport == treasure_chest_airport) else 0
        is_default_airport = 1 if bool(airport in countries_and_default_airports.values()) else 0

        save_airport_to_game_airports(game_id, airport_ident, question_id, answered, has_treasure, is_default_airport)

    return (game_id, countries_and_default_airports, game_countries, default_airport, treasure_land_airports,
            difficulty_level, treasure_land_country, treasure_chest_airport, want_clue)
