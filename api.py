from flask import Flask, g, jsonify, request, make_response
from persistence import Persistence

MIN_SCORE = 0
MAX_SCORE = None
MIN_DIFFICULTY = 1
MAX_DIFFICULTY = 3


app = Flask(__name__)


class ParseError(Exception):
    def __init__(self, msg):
        self.msg = msg


def get_db():
    db = getattr(g, '_persistence', None)
    if db is None:
        db = g._persistence = Persistence('highscore.sqlite')
    return db


@app.route('/api/v1.0/highscores', methods=["GET"])
def get_highscore():
    db = get_db()
    result = [get_object(t) for t in db.get_all_scores()]
    return jsonify(result)


@app.route('/api/v1.0/highscores/name/<name>', methods=["GET"])
def get_highscore_for_name(name):
    db = get_db()
    result = [get_object(t) for t in db.get_scores_for_name(name)]
    return jsonify(result)


@app.route('/api/v1.0/highscores/difficulty/<int:difficulty>', methods=["GET"])
def get_highscore_for_difficulty(difficulty):
    db = get_db()
    result = [get_object(t) for t in db.get_scores_for_difficulty(difficulty)]
    return jsonify(result)
    

@app.route('/api/v1.0/highscores/name/<name>/difficulty/<int:difficulty>', methods=["GET"])
def get_highscore_for_name_and_difficulty(name, difficulty):
    db = get_db()
    result = [get_object(t) for t in db.get_scores_for_name_and_difficulty(name, difficulty)]
    return jsonify(result)


@app.route('/api/v1.0/highscores', methods=["POST"])
def save_highscore():
    name, difficulty, score = parse_tuple(request.json)

    db = get_db()
    items = list(db.get_scores_for_name_and_difficulty(name, difficulty))

    if len(items) > 0:
        _, _, current_score = items[0]
        if current_score >= score:
            return make_response("", 304)

    db.save(name, difficulty, score)
    return make_response(jsonify(get_object((name, difficulty, score))), 201)


@app.errorhandler(ParseError)
def parse_error_handler(error):
    return make_response(jsonify({'parse error': error.msg}), 400)


def get_object(tup):
    name, diff, score = tup
    return {
        "name": name,
        "difficulty": diff,
        "score": score
    }


def parse_tuple(json):
    if not json:
        raise ParseError("no valid json!")
    name = get_string(json, 'name')
    diff = get_int(json, 'difficulty')
    if not check_range(diff, MIN_DIFFICULTY, MAX_DIFFICULTY):
        raise ParseError("difficulty not in valid range!")
    score = get_int(json, 'score')
    if not check_range(score, MIN_SCORE, MAX_SCORE):
        raise ParseError('score not in valid range!')
    return (name, diff, score)


def check_range(value, min, max):
    if min is None and max is None:
        return True
    if min is None and value <= max:
        return True
    if max is None and value >= min:
        return True
    return min <= value <= max


def get_string(json, key):
    if not key in json:
        raise ParseError("missing key '{0}'!".format(key))
    return json[key]


def get_int(json, key):
    str_value = get_string(json, key)
    try:
        return int(str_value)
    except ValueError:
        raise ParseError("Value for `{0}` is not a valid integer!".format(key))


if __name__ == '__main__':
    app.run(debug=False)