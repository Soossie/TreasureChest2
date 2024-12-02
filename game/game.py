import itertools

from flask import render_template
from geopy.units import kilometers
from game_functions import *
import random


class Game:
    # to-do:
    # selvitä miten json-datan saa javascriptistä pythoniin (tarvitseeko?)

    # luokan luominen json-datasta
    @classmethod
    def from_json(cls, json_data):
        data = json.loads(json.dumps(json_data))
        obj = cls()
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)
        return obj

    @classmethod
    def from_game_id(cls, game_id):
        data = get_game_info_from_database(game_id)
        obj = cls()
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        obj.wise_man_cost, obj.wise_man_reward = get_wise_man_cost_and_reward(obj.difficulty_level)
        # obj.advice_guy_reward = ?
        return obj

    def __init__(self):
        # tietokannassa
        self.id = None
        self.screen_name = None
        self.difficulty_level = None
        self.money = None
        self.home_airport = None
        self.location = None
        self.co2_consumed = 0

        # nämä eivät ole tietokannassa, mieti tarvitseeko ne olla ja saako niitä
        # treasure land clue lokaalisti javascriptissä
        #self.treasure_land_clue = None  # riippuu haluaako pelaaja vihjeen vai ei
        #self.visited_country_list = []  # hae visited sarakkeesta game_airports taulusta icao koodin perusteella maa
        self.visited_airport_list = []  # 1 tai 0, visited sarake game_airports taulusta

        # ei tietokantaan
        self.wise_man_cost = None
        self.wise_man_reward = None
        self.advice_guy_reward = None

    # def start_game(self, player, difficulty_level, want_clue):  # argumentit haetaan javascriptin puolelta
    def start_game(self):
        # kysyy pelaajan nimen
        self.screen_name = input('Input player name: ')

        # esittelee vaikeustasot
        print('\nDifficulty levels: easy, normal, hard.\n'
              'Difficulty level determines how many countries and airports the game generates.')

        while not self.difficulty_level:
            # kysyy käyttäjältä vaikeustason ja muuttaa syöteen pieniksi kirjaimiksi
            difficulty_level_input = input('Choose difficulty level. Input e (easy), n (normal), h (hard): ').lower()

            # valitsee vaikeustason käyttäjän antaman syötteen perusteella
            if difficulty_level_input in ('e', 'easy'):
                self.difficulty_level = 'easy'
            elif difficulty_level_input in ('n', 'normal'):
                self.difficulty_level = 'normal'
            elif difficulty_level_input in ('h', 'hard'):
                self.difficulty_level = 'hard'
            else:
                print('Invalid input.')

        self.wise_man_cost, self.wise_man_reward = get_wise_man_cost_and_reward(self.difficulty_level)
        self.advice_guy_reward = get_advice_guy_cost_and_reward(self.difficulty_level)

        # hae vihje
        #want_clue = input("Do you want a clue? Input y (yes) or n (no): ")
        #if want_clue in ('y', 'yes'):
        #    want_clue = True
        #else:
        #    want_clue = False

        # määritä pelaajan aloitusrahan määrä vaikeustason mukaan
        self.money = get_default_money(self.difficulty_level)

        # arvo maat ja maille oletuslentokentät
        countries_and_default_airport_icaos = {}
        for country_name in get_game_countries(self.difficulty_level):
            default_airport_icao = get_random_default_airport_icao_for_country(country_name)
            countries_and_default_airport_icaos.update({country_name: default_airport_icao})

        # valitse yksi maista aloitusmaaksi ja maan oletuslentokenttä aloituslentokentäksi
        home_country, self.home_airport = random.choice(list(countries_and_default_airport_icaos.items()))
        self.location = self.home_airport

        # lisää aloitusmaa pelaajan käytyjen maiden listaan
        #self.visited_country_list.append(home_country)

        # arvo aarremaa
        treasure_land_country, treausure_land_default_airport_icao = False, False
        while not treasure_land_country:
            country = random.choice(list(countries_and_default_airport_icaos.keys()))

            # aarremaa ei saa olla pelaajan aloitusmaa
            if country != home_country:
                treasure_land_country = country

        # arvo aarremaalle lentokentät
        treasure_land_airport_icaos = get_treasure_land_airport_icaos(self.difficulty_level, treasure_land_country,
                                                                      treausure_land_default_airport_icao)

        # arvo maan sisältä aarrearkun lentokenttä
        treasure_land_default_airport_icao = countries_and_default_airport_icaos[treasure_land_country]
        treasure_chest_airport_icao = random.choice(treasure_land_airport_icaos)

        # testaa että aarrearkun lentokenttä ei ole sama kuin maan oletuslentokenttä
        while treasure_land_default_airport_icao == treasure_chest_airport_icao:
            treasure_chest_airport_icao = random.choice(treasure_land_airport_icaos)

        # selvitä kuinka monta tietäjää pelissä on
        wise_man_count = get_wise_man_count(self.difficulty_level)

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

        # hae arvice guyn määrä ja arvo lentokentät
        advice_guys_in_countries_count, advice_guys_in_treasure_land_count = get_advice_guy_count(self.difficulty_level)

        # oletuslentokentillä
        advice_guy_airports_in_countries = []
        while len(advice_guy_airports_in_countries) < advice_guys_in_countries_count:
            new_airport = random.choice(list(countries_and_default_airport_icaos.values()))
            # lentokentällä ei saa olla tietäjä, aarre tai pelaajan kotikenttä
            if new_airport in advice_guy_airports_in_countries or new_airport in wise_man_airports:
                continue
            advice_guy_airports_in_countries.append(new_airport)

        # aarremaan sisällä
        advice_guy_airports_in_treasure_land = []
        while len(advice_guy_airports_in_treasure_land) < advice_guys_in_treasure_land_count:
            new_airport = random.choice(list(treasure_land_airport_icaos))
            # lentokentällä ei saa olla tietäjä, aarre tai pelaajan kotikenttä
            if new_airport in advice_guy_airports_in_treasure_land or new_airport in wise_man_airports or new_airport in advice_guy_airports_in_countries:
                continue
            advice_guy_airports_in_treasure_land.append(new_airport)

        # tallenna pelaajan tiedot game tauluun
        input_player_info(self.screen_name, self.money, self.home_airport, self.location, self.difficulty_level, self.co2_consumed)

        # hae juuri tehdyn pelin id (viimeinen id)
        self.id = get_last_game_id()

        # tallenna oletuslentokenttien tiedot tietokantaan
        for airport_icao in itertools.chain(countries_and_default_airport_icaos.values(), treasure_land_airport_icaos):

            question_id = False
            if airport_icao in wise_man_airports:
                if airport_icao == treasure_land_default_airport_icao:
                    question_id = get_random_question_id()
                else:
                    question_id = get_random_unused_question_id(self.id)

            answered = 0
            has_treasure = 1 if bool(airport_icao == treasure_chest_airport_icao) else 0
            is_default_airport = 1 if bool(airport_icao in countries_and_default_airport_icaos.values()) else 0
            has_advice_guy = 1 if bool(airport_icao in advice_guy_airports_in_countries or airport_icao in advice_guy_airports_in_treasure_land) else 0
            visited = 0
            save_airport_to_game_airports(self.id, airport_icao, question_id, answered, has_treasure,
                                          is_default_airport, has_advice_guy, visited)

        # sijoita vihje muuttujaan
        #if want_clue:
        #    self.treasure_land_clue = get_clue(self.id)

    # palauttaa luokan tiedot json-muodossa
    def get_game_info(self):
        return self.__dict__
