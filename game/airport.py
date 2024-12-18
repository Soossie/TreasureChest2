import geopy.distance

from database import Database
from game_functions import get_current_location, get_advice, get_treasure_land_country_name, get_player_co2_consumed, \
    get_player_money, get_random_treasure

db = Database()

# lentokentän perustiedot suoraan tietokannasta
class Airport:
    def __init__(self, icao):
        self.icao = icao
        self.name = self.get_airport_name()
        self.latitude, self.longitude = self.get_airport_coordinates()
        self.country_name = self.get_airport_country_name()

    def get_airport_name(self):
        sql = f'select name from airport where ident = "{self.icao}";'
        cursor = db.get_conn().cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        return result[0]

    def get_airport_coordinates(self):
        sql = f'select latitude_deg, longitude_deg from airport where ident = "{self.icao}";'
        cursor = db.get_conn().cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        return result

    def get_airport_country_name(self):
        sql = (f'select country.name from country inner join airport on country.iso_country = airport.iso_country '
               f'where ident = "{self.icao}";')
        cursor = db.get_conn().cursor()
        cursor.execute(sql)
        result = cursor.fetchone()
        return result[0]

    # palauttaa luokan tiedot json-muodossa
    def get_airport_info(self):
        return self.__dict__

# kaikki pelin sisäiset lentokenttien tiedot (uniikit joka pelissä)
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

        return {'wise_man_question_id': question_id, 'wise_man_question': question, 'answer': answer, 'answered': answered_result}

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
        else:
            # arvo ja lisää aarre kentän tietoihin jos nykyinen kenttä on aarrekenttä
            if info['has_treasure'] == 1:
                info.update({'treasure': get_random_treasure(self.game_id)})
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

# tiedot tietylle lentokentälle lentämisestä
class FlightInfo:
    def __init__(self, game_id, destination_icao):
        self.game_id = game_id
        self.current_location = get_current_location(game_id)
        self.destination_icao = destination_icao
        self.distance = self.get_distance_to_airport(self.current_location, self.destination_icao)
        self.ticket_cost = self.count_ticket_cost()
        self.co2_consumption = self.get_co2_consumption()
        self.can_fly_to = self.has_enough_money_for_flight()

    # laske lentokenttien välinen etäisyys
    @classmethod
    def get_distance_to_airport(cls, current_location, destination_icao):
        # hae koordinaatit Airport-luokasta
        airport1 = Airport(current_location)
        airport2 = Airport(destination_icao)

        coordinates1 = (airport1.latitude, airport1.longitude)
        coordinates2 = (airport2.latitude, airport2.longitude)

        distance = geopy.distance.distance(coordinates1, coordinates2).km
        distance = int(distance)
        return distance

    # laske lentolipun hinta etäisyyden ja kansainvälisyyden perusteella
    def count_ticket_cost(self):
        international_flight = self.is_international_flight()

        price = {
            'international': [(200, 1.00), (500, 0.70), (800, 0.40), (40000, 0.25)],
            'domestic': [(200, 1.25), (500, 0.85), (800, 0.55), (40000, 0.4)],
        }
        price = price['international'] if international_flight else price['domestic']

        # lippu on 20% kalliimpi mikäli pelaaja on ylittänyt co2 budjetin
        over_co2_budget = bool(get_player_co2_consumed(self.game_id) > 1000)

        for max_distance, multiplier in price:
            if self.distance < max_distance:
                math_formula = int(100 + multiplier * self.distance)
                return int(math_formula * 1.20) if over_co2_budget else math_formula
        # failsafe
        failsafe_cost = 100
        return int(failsafe_cost * 1.20) if over_co2_budget else failsafe_cost

    def is_international_flight(self):
        sql = (f'select iso_country from airport '
               f'where ident = "{self.current_location}" or ident = "{self.destination_icao}";')
        cursor = db.get_conn().cursor()
        cursor.execute(sql)
        result = cursor.fetchall()
        return result[0][0] != result[1][0] if len(result) == 2 else True

    def get_co2_consumption(self):
        co2_per_km = 0.250 if self.distance < 700 else 0.190
        return int(co2_per_km * self.distance)

    def has_enough_money_for_flight(self):
        return self.ticket_cost <= get_player_money(self.game_id)

    # palauttaa luokan tiedot json-muodossa
    def get_flight_info(self):
        return {
            'distance': self.distance,
            'ticket_cost': self.ticket_cost,
            'co2_consumption': self.co2_consumption,
            'can_fly_to': self.can_fly_to,
        }

# kaikkien hetkellisesti saatavilla olevien lentokenttien kaikki tiedot
class AvailableAirports(GameAirports):
    def __init__(self, game_id):
        super().__init__(game_id)
        self.available_airports = self.get_available_airports_json()

    # hae lentokentät mitkä näytetään pelaajalle kartalla
    def get_available_airports_json(self):
        all_game_airports_info = self.get_all_game_airports_info_json()
        treasure_land_country_name = get_treasure_land_country_name(self.game_id)

        available_airports = []
        current_location_info = self.get_current_airport_info_json()

        # jos pelaaja on aarremaassa, hae kaikki aarremaan lentokenttien tiedot
        if current_location_info['country_name'] == treasure_land_country_name:
            for airport_info in all_game_airports_info:

                if airport_info['country_name'] == treasure_land_country_name:
                    airport_info.update({'flight_info': FlightInfo(self.game_id, airport_info['icao']).get_flight_info()})
                    available_airports.append(airport_info)
        else:
            # jos pelaaja ei ole aarremaassa, hae oletuslentokenttien tiedot
            for airport_info in all_game_airports_info:

                if airport_info['is_default_airport']:
                    airport_info.update({'flight_info': FlightInfo(self.game_id, airport_info['icao']).get_flight_info()})
                    available_airports.append(airport_info)

        return available_airports
