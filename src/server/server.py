import sys
from flask import Flask
from flask import request

sys.path.append("../")
import algo.core.dtw as dtw
import algo.core.template as tpl
import feat_ext

app = Flask(__name__)

eb_dba_tpl = None

@app.route('/enrollment', methods=["POST"])
def enrollment():
    enrollment_signatures = []
    for sig in request.json["signatures"]:
        enrollment_signatures.append(feat_ext.read_json(sig).to_numpy())

    global eb_dba_tpl
    eb_dba_tpl = tpl.get_eb_dba_tpl(enrollment_signatures, 5, 1)

    return {
        "msg": "success"
    }


@app.route('/verification', methods=["GET"])
def verification():
    signature = feat_ext.read_json(request.json["signature"]).to_numpy()

    res = dtw.DTW(signature, eb_dba_tpl)

    app.logger.debug(res)

    return {
        "res": res
    }


if __name__ == "__main__":
    app.run()
