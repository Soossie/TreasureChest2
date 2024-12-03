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

    def get_visited_value(self, airport_icao):
        sql = f'select visited from game_airports where game_id = {self.game_id} and airport_ident = "{airport_icao}";'
        cursor = db.get_conn().cursor(buffered=True)
        cursor.execute(sql)
        result = cursor.fetchone()
        return result[0]

    def get_airport_info(self, airport_icao):
        airport = Airport(airport_icao)

        # lentokentän perustiedot (alkuperäinen airport-taulu)
        airport_info = airport.get_airport_info()

        # onko pelaaja käynyt kentällä
        airport_info.update({'visited': self.get_visited_value(airport_icao)})

        # näytä wise man, advice guy, aarteen tiedot vain join pelaaja kentällä
        if airport_icao == get_current_location(self.game_id):

            wise_man_result = self.get_wise_man_info_for_airport(airport_icao)
            if wise_man_result:
                airport_info.update({'wise_man': wise_man_result})

            advice_guy_result = self.get_advice_guy_info_for_airport(airport_icao)
            if advice_guy_result:
                airport_info.update({'advice_guy': advice_guy_result})

            # to-do: onko aarre


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


print(GameAirports(23).get_all_game_airports_info_json())


class AvailableAirports:
    def __init__(self):
        self.airports = {}
        pass


