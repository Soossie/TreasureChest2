from flask import Flask, Response
from flask_cors import CORS

from game_functions import *
from game import Game


app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


# lentää pelaajan uudelle lentokentälle
@app.route('/fly-to/<game_id>/<destination_icao>')
def fly_to(game_id, destination_icao):
    try:
        status_code = 200

        update_current_location(game_id, destination_icao)
        response = {
            'game_id': game_id,
            'new_location_icao': get_current_location(game_id),
        }
    except ValueError:
        status_code = 400
        response = {
            'status': status_code,
            'description': 'This is error message',
        }
    json_response = json.dumps(response)
    return Response(response=json_response, status=status_code, mimetype='application/json')


# hakee kaikki tiettyyn lentoon tarvittavat tiedot
@app.route('/flight-info/<game_id>/<destination_icao>')
def flight_info(game_id, destination_icao):
    try:
        status_code = 200

        current_location_icao = get_current_location(game_id)
        response = {
            'game_id': game_id,
            'current_location_icao': current_location_icao,
            'destination_icao': destination_icao,
            'distance': get_distance_between_airports(current_location_icao, destination_icao),
            'ticket_cost': count_ticket_cost(current_location_icao, destination_icao),
            'co2_consumption': get_co2_consumption(current_location_icao, destination_icao),
        }
        print(response)
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
        # tapa millä tiedot haetaan ja mitä haetaan on vielä työn alla, ei lopullinen versio!
        response = {
            'game_info': get_game_info(game_id),
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
            'testvalue.visited_country_list': game.visited_country_list,  # testiarvo. esimerkki miten olion muuttujia voi tulostaa
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
