import urllib2
import base64
import ast


def get_match_result(match_id=2588548):
    raw_file = urllib2.urlopen('http://robotgame.net/match/%s' % match_id).read()

    preamble = "<script type=\"text/javascript\" src=\"data:text/javascript;base64,"

    start_pos = raw_file.find(preamble) + len(preamble)
    end_pos = raw_file.find('\"', start_pos) - 1

    decoded_moves = base64.decodestring(raw_file[start_pos:end_pos].replace('\n', ''))

    moves = ast.literal_eval(decoded_moves[16:len(decoded_moves)-2])

    return moves
