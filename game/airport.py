from database import Database
from game_functions import get_current_location, get_advice

db = Database()


class Airport:
    def __init__(self, icao):
        self.icao = icao
        self.name = self.get_airport_name()
        self.latitude, self.longitude = self.get_airport_coordinates()
        self.country_name = self.get_airport_country_name()
        self.iata_code = self.get_airport_iata_code()

    # hae lentokentän nimi
    def get_airport_name(self):
        sql = f'select airport.name from airport where ident = "{self.icao}";'
        cursor = db.get_conn().cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        return result[0]

    # hae lentokentän koordinaatit
    def get_airport_coordinates(self):
        sql = f'select latitude_deg, longitude_deg from airport where ident = "{self.icao}";'
        cursor = db.get_conn().cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        return result

    # hae lentokentän maan nimi
    def get_airport_country_name(self):
        sql = (f'select country.name from country inner join airport on country.iso_country = airport.iso_country '
               f'where ident = "{self.icao}";')
        cursor = db.get_conn().cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        return result[0]

    # hae lentokentän iata koodi
    def get_airport_iata_code(self):
        sql = f'select iata_code from airport where ident="{self.icao}";'
        cursor = db.get_conn().cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        return result[0]

    # palauttaa luokan tiedot json-muodossa
    def get_airport_info(self):
        return self.__dict__


class GameAirports:
    def __init__(self, game_id):
        self.game_id = game_id
        self.game_airports = self.get_all_game_airports()

    def get_all_game_airports(self):
        sql = f'select airport_ident from game_airports where game_id={self.game_id};'
        cursor = db.get_conn().cursor(buffered=True)
        cursor.execute(sql)
        result = cursor.fetchall()
        return [icao[0] for icao in result]

    def get_wise_man_info_for_airport(self, airport_icao):
        sql = (f'select wise_man_questions.id, wise_man_questions.question, wise_man_questions.answer from wise_man_questions '
               f'inner join game_airports on wise_man_questions.id = game_airports.wise_man_question_id '
               f'where game_airports.game_id={self.game_id} and game_airports.airport_ident="{airport_icao}";')
        cursor = db.get_conn().cursor(buffered=True)
        cursor.execute(sql)
        question_result = cursor.fetchall()

        # lopeta mikäli lentokentällä ei ole tietäjää
        if not question_result:
            return

        question_id = question_result[0][0]
        question = question_result[0][1]
        answer = question_result[0][2]

        sql = f'select answered from game_airports where game_id={self.game_id} and wise_man_question_id={question_id};'
        cursor = db.get_conn().cursor(buffered=True)
        cursor.execute(sql)
        answered_result = cursor.fetchone()[0]

        return {'wise_man_question': question, 'answer': answer, 'answered': answered_result}

    def get_advice_guy_info_for_airport(self, airport_icao):
        sql = (f'select has_advice_guy from game_airports '
               f'where game_id={self.game_id} and airport_ident="{airport_icao}";')
        cursor = db.get_conn().cursor(buffered=True)
        cursor.execute(sql)
        result = cursor.fetchone()[0]  # jos on advice guy, palautuu 1, muuten 0

        if result == 0:
            return
        return {'advice': get_advice()}

    def get_game_airports_table_info_for_airport(self, airport_icao):
        sql = (f'select has_treasure, is_default_airport, visited from game_airports '
               f'where game_id = {self.game_id} and airport_ident = "{airport_icao}";')
        cursor = db.get_conn().cursor(buffered=True)
        cursor.execute(sql)

        rows = cursor.fetchall()[0]
        columns = [item[0] for item in cursor.description]

        # muuta data dict (json) muotoon
        data = dict()
        for column, row in zip(columns, rows):
            data.update({column: row})
        return data

    def get_airport_info(self, airport_icao):
        airport = Airport(airport_icao)

        # lentokentän perustiedot (alkuperäinen airport-taulu)
        airport_info = airport.get_airport_info()

        # hae has_treasure, is_default_airport, visited tietokannasta
        info = self.get_game_airports_table_info_for_airport(airport_icao)

        # poista aarteen tieto jos pelaaja ei ole kentällä
        if airport_icao != get_current_location(self.game_id):
            info.pop('has_treasure')

        airport_info.update(info)

        # näytä wise man, advice guy vain jos pelaaja kentällä
        if airport_icao == get_current_location(self.game_id):

            wise_man_result = self.get_wise_man_info_for_airport(airport_icao)
            if wise_man_result:
                airport_info.update({'wise_man': wise_man_result})

            advice_guy_result = self.get_advice_guy_info_for_airport(airport_icao)
            if advice_guy_result:
                airport_info.update({'advice_guy': advice_guy_result})

        return airport_info

    def get_all_game_airports_info_json(self):
        all_infos = []

        # tallenna kaikkien paitsi nykyisen sijainnin tiedot
        for airport_icao in self.game_airports:
            if airport_icao == get_current_location(self.game_id):
                continue

            airport_info = self.get_airport_info(airport_icao)
            all_infos.append(airport_info)
        return all_infos

    def get_current_airport_info_json(self):
        current_location_icao = get_current_location(self.game_id)
        airport_info = self.get_airport_info(current_location_icao)
        return airport_info


#print(GameAirports(23).get_all_game_airports_info_json())


class AvailableAirports(GameAirports):
    def __init__(self, game_id):
        super().__init__(game_id)
        self.available_airports = self.get_available_airports_json()

    # hae lentokentät mitkä näytetään pelaajalle kartalla
    def get_available_airports_json(self):
        all_game_airports_info = self.get_all_game_airports_info_json()
        treasure_land_country_name = self.get_treasure_land_country_name()

        available_airports = []
        current_location_info = self.get_current_airport_info_json()

        # jos pelaaja on aarremaassa, hae kaikki aarremaan lentokentät
        if current_location_info['country_name'] == treasure_land_country_name:
            for airport_info in all_game_airports_info:
                if airport_info['country_name'] == treasure_land_country_name:
                    available_airports.append(airport_info)
        else:
            # jos pelaaja ei ole aarremaassa, hae oletuslentokenttien tiedot
            for airport_info in all_game_airports_info:
                if airport_info['is_default_airport']:
                    available_airports.append(airport_info)

        return available_airports

    def get_treasure_land_country_name(self):
        sql = f'select airport_ident from game_airports where game_id={self.game_id} and has_treasure=1;'
        cursor = db.get_conn().cursor(buffered=True)
        cursor.execute(sql)
        treasure_airport_icao = cursor.fetchone()[0]
        return Airport(treasure_airport_icao).get_airport_country_name()

#print(AvailableAirports(55))
