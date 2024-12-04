from flask import Flask, Response
from flask_cors import CORS

from game_functions import *
from game import Game
from airport import GameAirports, AvailableAirports, FlightInfo

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

# to-do:
# päivitä visited_airport_list
# lisää co2 päästöjä tietokantaan jokaisen lennon jälkeen
# matkustaessa tarkista onko lentokentällä tietäjä, advice guy, onke se aarremaan oletuslentokenttä, onko siellä aarre

"""
# wise man
@app.route('/wise-man/<game_id>')
def wise_man(game_id, amount):
    try:
        status_code = 200
        
        original_money = get_player_money(game_id)
        add_or_remove_money(game_id, int(amount), remove=True)
        new_money = get_player_money(game_id)

        response = {
            'game_id': game_id,
            'original_money': original_money,
            'new_money': new_money,
        }
    except ValueError:
        status_code = 400
        response = {
            'status': status_code,
            'description': 'This is error message',
        }
    json_response = json.dumps(response)
    return Response(response=json_response, status=status_code, mimetype='application/json')
"""


# lentää pelaajan uudelle lentokentälle
@app.route('/fly-to/<game_id>/<destination_icao>')
def fly_to(game_id, destination_icao):
    try:
        #status_code = 200

        # testaa saako kentälle lentää (onko se saatavilla olevien kenttien listalla) ja että kenttä ei ole nykyinen kenttä
        # jos ei saa lentää, älä tee mitään ja palauta pelin tiedot
        if any([destination_icao not in GameAirports(game_id).game_airports,
                destination_icao == GameAirports(game_id).get_current_airport_info_json()['icao'],
                ]):
            return game_info(game_id)

        flight_info = FlightInfo(game_id, destination_icao)
        # poista rahaa ja lisää co2 kulutus
        add_or_remove_money(game_id, flight_info.ticket_cost, remove=True)
        update_co2_consumed(game_id, flight_info.co2_consumption)

        # päivitä tietokantaan sijainti
        update_current_location(game_id, destination_icao)
        update_column_visited(game_id, destination_icao)

        # advice guy antaa automaattisesti rahaa jos kentällä
        current_location_info = GameAirports(game_id).get_current_airport_info_json()
        if 'advice_guy' in current_location_info:
            add_or_remove_money(game_id, Game.from_game_id(game_id).advice_guy_reward, add=True)

        return game_info(game_id)

    except ValueError:
        status_code = 400
        response = {
            'status': status_code,
            'description': 'This is error message',
        }
    json_response = json.dumps(response)
    return Response(response=json_response, status=status_code, mimetype='application/json')


# tulostaa tietyn pelin tiedot
@app.route('/game-info/<game_id>')
def game_info(game_id):
    try:
        status_code = 200

        game = Game.from_game_id(game_id)
        response = {
            'game_info': game.get_game_info(),
            'current_location_info': GameAirports(game.id).get_current_airport_info_json(),
            'available_airports_info': AvailableAirports(game.id).available_airports,
        }
    except ValueError:
        status_code = 400
        response = {
            'status': status_code,
            'description': 'This is error message',
        }
    json_response = json.dumps(response)
    return Response(response=json_response, status=status_code, mimetype='application/json')


# aloittaa uuden pelin
@app.route('/new-game')
def new_game():
    try:
        status_code = 200
        game = Game()
        game.start_game()
        response = {
            'game_info': game.get_game_info(),
            'current_location_info': GameAirports(game.id).get_current_airport_info_json(),
            #'game_airports_info': GameAirports(game.id).get_all_game_airports_info_json(),
            'available_airports_info': AvailableAirports(game.id).available_airports,
            #'testvalue.visited_country_list': game.visited_country_list,  # testiarvo. esimerkki miten olion muuttujia voi tulostaa
        }
    except ValueError:
        status_code = 400
        response = {
            'status': status_code,
            'description': 'This is error message',
        }
    json_response = json.dumps(response)
    return Response(response=json_response, status=status_code, mimetype='application/json')


@app.errorhandler(404)
def page_not_found(status_code):
    response = {
        'status': '404',
        'description': 'Page not found',
    }
    json_response = json.dumps(response)
    return Response(response=json_response, status=404, mimetype='application/json')


if __name__ == '__main__':
    app.run(use_reloader=True, host='127.0.0.1', port=3000)
