import json
import base64
import os

from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, url_for
import jinja2

from model import Recording, connect_to_db, db
from pitchgraph import analyze_pitch


app = Flask(__name__)
app.secret_key = 'development key'
app.jinja_env.undefined = jinja2.StrictUndefined



@app.route('/<path>')
def send_audio_file(path):
    return send_from_directory('sounds', path)


@app.route('/analyze', methods=["POST"])
def analyze_user_rec():
    """Analyze the user's recording, save the audio data and pitch data to
    database, and send pitch data back to page."""

    # cut off first 22 chars ("data:audio/wav;base64,")
    user_b64 = request.form.get("user_rec")[22:]
    user_wav = base64.b64decode(user_b64)
    user_recording_path = os.path.abspath('./sounds/user-rec.wav')
    with open(user_recording_path, 'wb') as f:
        f.write(user_wav)

    user_pitch_data = analyze_pitch(user_recording_path)

    # store audio data (user_b64) and user_pitch_data in db
    ex_id = request.form.get("ex_id")
    attempts = Recording.query.filter_by(ex_id=ex_id).all()
    if attempts:
        attempt_num = max(attempt.attempt_num for attempt in attempts) + 1
    else:
        attempt_num = 1

    new_rec = Recording(ex_id=ex_id,
                        attempt_num=attempt_num,
                        audio_data=user_b64,
                        pitch_data=user_pitch_data)
    db.session.add(new_rec)
    db.session.commit()

    return jsonify(attempt=new_rec.serialize())

if __name__ == "__main__":
    app.debug = True
    connect_to_db(app)
    app.run()
