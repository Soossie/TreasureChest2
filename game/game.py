import itertools

from game_functions import *
import random
from airport import Airport


class Game:

    @classmethod
    def from_game_id(cls, game_id):
        data = cls.get_game_info_from_database(game_id)
        obj = cls()
        for key, value in data.items():
            if hasattr(obj, key):
                setattr(obj, key, value)

        obj.wise_man_cost, obj.wise_man_reward = get_wise_man_cost_and_reward(obj.difficulty_level)
        obj.advice_guy_reward = get_advice_guy_reward(obj.difficulty_level)
        obj.clue = obj.get_clue()
        obj.in_treasure_land = bool(Airport(obj.location).country_name == get_treasure_land_country_name(obj.id))
        return obj

    def __init__(self):
        # tietokannassa, nimet täytyy olla samat kuin tietokannassa
        self.id = None
        self.screen_name = None
        self.difficulty_level = None
        self.money = None
        self.home_airport = None
        self.location = None
        self.co2_consumed = 0

        # ei tietokantaan
        self.wise_man_cost = None
        self.wise_man_reward = None
        self.advice_guy_reward = None
        self.clue = None
        self.in_treasure_land = None

    # def start_game(self, player, difficulty_level, want_clue):  # argumentit haetaan javascriptin puolelta
    def start_game(self, player_name, difficulty_level_input):
        self.screen_name = player_name

        # esittelee vaikeustasot
        #print('\nDifficulty levels: easy, normal, hard.\n'
        #      'Difficulty level determines how many countries and airports the game generates.')

        #while not self.difficulty_level:
        #    # kysyy käyttäjältä vaikeustason ja muuttaa syöteen pieniksi kirjaimiksi
        #    difficulty_level_input = input('Choose difficulty level. Input e (easy), n (normal), h (hard): ').lower()

        # valitsee vaikeustason käyttäjän antaman syötteen perusteella
        if difficulty_level_input in ('e', 'easy'):
            self.difficulty_level = 'easy'
        elif difficulty_level_input in ('n', 'normal'):
            self.difficulty_level = 'normal'
        elif difficulty_level_input in ('h', 'hard'):
            self.difficulty_level = 'hard'
        #else:
        #    return print('Invalid difficulty level. Please input one of the following: e, n, h')

        self.wise_man_cost, self.wise_man_reward = get_wise_man_cost_and_reward(self.difficulty_level)
        self.advice_guy_reward = get_advice_guy_reward(self.difficulty_level)

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

        # poista aarremaan oletuslentokenttä aarremaan lentokentiltä (jotta kyseinen lentokenttä ei esiintyisi kahdesti tietokannassa)
        if treasure_land_default_airport_icao in treasure_land_airport_icaos:
            treasure_land_airport_icaos.remove(treasure_land_default_airport_icao)

        # testaa että aarrearkun lentokenttä ei ole sama kuin maan oletuslentokenttä
        while treasure_land_default_airport_icao == treasure_chest_airport_icao:
            treasure_chest_airport_icao = random.choice(treasure_land_airport_icaos)

        # selvitä kuinka monta tietäjää pelissä on
        wise_man_count = get_wise_man_count(self.difficulty_level)

        # arvo tietäjien lentokentät
        wise_man_airports = [treasure_land_default_airport_icao, treasure_chest_airport_icao]

        for _ in range(wise_man_count - 1):
            while True:
                # arvo aarremaan lentokenttä tietäjälle missä ei ole vielä tietäjää
                random_treasure_land_airport = random.choice(list(treasure_land_airport_icaos))
                if random_treasure_land_airport not in wise_man_airports:
                    wise_man_airports.append(random_treasure_land_airport)
                    break
        # debug
        print(f'wise man airports ({len(wise_man_airports)}): {wise_man_airports}')

        # hae advice guyn määrä ja arvo lentokentät
        advice_guys_in_countries_count, advice_guys_in_treasure_land_count = get_advice_guy_count(self.difficulty_level)

        # advice guy oletuslentokentillä
        advice_guy_airports_in_countries = []
        while len(advice_guy_airports_in_countries) < advice_guys_in_countries_count:
            new_airport = random.choice(list(countries_and_default_airport_icaos.values()))
            # lentokentällä ei saa olla tietäjä, aarre tai pelaajan kotikenttä
            if (new_airport in advice_guy_airports_in_countries or new_airport in wise_man_airports
                    or new_airport == self.home_airport):
                continue
            advice_guy_airports_in_countries.append(new_airport)

        # advice guy aarremaan sisällä
        advice_guy_airports_in_treasure_land = []
        while len(advice_guy_airports_in_treasure_land) < advice_guys_in_treasure_land_count:
            new_airport = random.choice(list(treasure_land_airport_icaos))
            # lentokentällä ei saa olla tietäjä, aarre tai pelaajan kotikenttä
            if (new_airport in advice_guy_airports_in_treasure_land or new_airport in wise_man_airports
                    or new_airport in advice_guy_airports_in_countries or new_airport == self.home_airport
                    or new_airport == treasure_chest_airport_icao):
                continue
            advice_guy_airports_in_treasure_land.append(new_airport)

        # tallenna pelaajan tiedot game tauluun
        input_player_info(self.screen_name, self.money, self.home_airport, self.location, self.difficulty_level, self.co2_consumed)

        # hae juuri tehdyn pelin id (viimeinen id tietokannassa)
        self.id = get_last_game_id()

        # tallenna lentokenttien tiedot tietokantaan
        for airport_icao in itertools.chain(countries_and_default_airport_icaos.values(), treasure_land_airport_icaos):

            # arvo kysymys jos lentokentällä wise man
            question_id = get_random_unused_question_id(self.id) if airport_icao in wise_man_airports else False

            answered = 0
            has_treasure = 1 if bool(airport_icao == treasure_chest_airport_icao) else 0
            is_default_airport = 1 if bool(airport_icao in countries_and_default_airport_icaos.values()) else 0
            has_advice_guy = 1 if bool(airport_icao in advice_guy_airports_in_countries or airport_icao in advice_guy_airports_in_treasure_land) else 0
            visited = 0
            save_airport_to_game_airports(self.id, airport_icao, question_id, answered, has_treasure,
                                          is_default_airport, has_advice_guy, visited)

        # debug:
        print(f'oletuslentokentät ({len(countries_and_default_airport_icaos)}): {countries_and_default_airport_icaos.values()}')
        print(f'aarremaan lentokentät ({len(treasure_land_airport_icaos)}): {treasure_land_airport_icaos}')

        # vihje on aarremaan nimen ensimmäinen kirjain
        self.clue = self.get_clue()
        self.in_treasure_land = bool(Airport(self.location).country_name == get_treasure_land_country_name(self.id))

        # lisää pelaadan kotilentokenttä käytyjen kenttien listaan
        update_column_visited(self.id, self.home_airport)

    # hakee tietokannasta game-taulusta tietyn pelin tiedot
    # (id, screen_name, money, home_airport, location, difficulty_level)
    @classmethod
    def get_game_info_from_database(cls, game_id):
        sql = f'select * from game where id = "{game_id}";'
        cursor = db.get_conn().cursor()
        cursor.execute(sql)

        rows = cursor.fetchall()[0]
        columns = [item[0] for item in cursor.description]

        # muuta data dict (json) muotoon
        data = dict()
        for column, row in zip(columns, rows):
            data.update({column: row})
        return data

    def get_clue(self):
        treasure_land_country_name = get_treasure_land_country_name(self.id)
        return f'The treasure is hidden in a country that begins with the letter {treasure_land_country_name[0]}.'

    # palauttaa luokan tiedot json-muodossa
    def get_game_info(self):
        return self.__dict__
