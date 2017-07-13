import json
import subprocess
from operator import itemgetter
from os import path
from praatinterface import PraatLoader
from subprocess import Popen, PIPE, call

def read_praat_out(text):
    if not text:
        return None
    lines = text.splitlines()
    head = lines.pop(0)
    head = head.split("\t")[1:]
    output = {}
    for l in lines:
        if '\t' in l:
            line = l.split("\t")
            time = line.pop(0)
            values = {}
            for j in range(len(line)):
                v = line[j]
                if v != '--undefined--':
                    try:
                        v = float(v)
                    except ValueError:
                        print(text)
                        print(head)
                else:
                    v = 0
                values[head[j]] = v
            if values:
                output[float(time)] = values
    return output

def get_praat_pitch(audio_file):
    """Given a wav file, use Praat to return a dictionary containing pitch (in Hz)
    at each millisecond."""

    praatpath = "/usr/bin/praat"
    runscript = path.abspath('./praat/praatScripts/pitch.praat')

    praat_output = subprocess.check_output (praatpath + ' --run ' + runscript + ' "' + audio_file + '"', shell=True)
    pitch_data = read_praat_out(praat_output)

    return pitch_data


def format_pitch_data(pitch_data):
    """Put pitch data in the format needed for graphing."""

    datapoints = [{"x": time, "y": meta['Pitch']} for time, meta in pitch_data.iteritems()]

    return sorted(datapoints, key=itemgetter("x"))


def smooth_pitch_data(datapoints):
    """Thin out data set to allow for b-spline smoothing in chart, and return as JSON."""

    i = 0
    datapoints_keep = []
    if datapoints:
        # reduce number of datapoints per second from 1000 to 20, remove points with pitch of zero
        while i < len(datapoints):
            point = datapoints[i]
            if point["y"]:
                datapoints_keep.append(point)
            i += 50
        # make sure last item is included so length of curve isn't lost
        datapoints_keep.append(datapoints[-1])

    return json.dumps(datapoints_keep, sort_keys=True)


def analyze_pitch(audio_file):
    """Run full pitch analysis."""

    return smooth_pitch_data(format_pitch_data(get_praat_pitch(audio_file)))


if __name__ == "__main__":
    print analyze_pitch(path.abspath('./sounds/fr-5.wav'))
