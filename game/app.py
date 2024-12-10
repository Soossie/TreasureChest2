from flask import Flask, Response
from flask_cors import CORS
import json

from game_functions import add_or_remove_money, update_co2_consumed, update_current_location, update_column_visited, \
    update_wise_man_question_answered
from game import Game
from airport import GameAirports, AvailableAirports, FlightInfo

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# wise man
@app.route('/wise-man/<game_id>/<is_correct_answer>')
def wise_man(game_id, is_correct_answer):
    try:
        # is_correct_answer täytyy olla luku, error jos ei ole
        # jos luku ei ole 0 tai 1, funktio ei lisää eikä poista rahaa
        is_correct_answer = int(is_correct_answer)

        # tarkista onko pelaaja jo vastannut nykyisen sijainnin kysymykseen
        current_location_info = GameAirports(game_id).get_current_airport_info_json()
        if current_location_info['wise_man']['answered']:
            return game_info(game_id)

        # tallenna tieto kysymykseen vastattu
        wise_man_question_id = current_location_info['wise_man']['wise_man_question_id']
        update_wise_man_question_answered(game_id, wise_man_question_id)

        game = Game.from_game_id(game_id)

        # poista ja/tai lisää rahaa riippuen oliko vastaus oikein
        if int(is_correct_answer) == 1:
            # poista ja lisää rahaa
            amount = game.wise_man_reward - game.wise_man_cost
            add_or_remove_money(game_id, amount, add=True)

        elif int(is_correct_answer) == 0:
            # poista rahaa
            amount = game.wise_man_cost
            add_or_remove_money(game_id, amount, remove=True)

        return game_info(game_id)

    except ValueError:
        status_code = 400
        response = {
            'status': status_code,
            'description': 'This is error message',
        }
    json_response = json.dumps(response)
    return Response(response=json_response, status=status_code, mimetype='application/json')


# lentää pelaajan uudelle lentokentälle
@app.route('/fly-to/<game_id>/<destination_icao>')
def fly_to(game_id, destination_icao):
    try:
        # testaa saako kentälle lentää (onko se saatavilla olevien kenttien listalla) ja että kenttä ei ole nykyinen kenttä
        # jos ei saa lentää, älä tee mitään ja palauta pelin tiedot
        if any([destination_icao not in GameAirports(game_id).game_airports,
                destination_icao == GameAirports(game_id).get_current_airport_info_json()['icao'],
                not FlightInfo(game_id, destination_icao).can_fly_to]):
            return game_info(game_id)

        flight_info = FlightInfo(game_id, destination_icao)
        # poista rahaa ja lisää co2 kulutus
        add_or_remove_money(game_id, flight_info.ticket_cost, remove=True)
        update_co2_consumed(game_id, flight_info.co2_consumption)

        # päivitä tietokantaan sijainti
        update_current_location(game_id, destination_icao)

        # advice guy antaa automaattisesti rahaa jos kentällä
        current_location_info = GameAirports(game_id).get_current_airport_info_json()
        if 'advice_guy' in current_location_info and not current_location_info['visited']:
            add_or_remove_money(game_id, Game.from_game_id(game_id).advice_guy_reward, add=True)

        # päivitä vierailu
        update_column_visited(game_id, destination_icao)

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
@app.route('/new-game/<player_name>/<difficulty_level>')
def new_game(player_name, difficulty_level):
    try:
        game = Game()
        game.start_game(player_name, difficulty_level)
        return game_info(game.id)

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
