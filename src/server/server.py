import sys
from flask import Flask, request, current_app
import crud
import numpy as np

sys.path.append("../")
import algo.core.dtw as dtw
import algo.core.template as tpl
import feat_ext

app = Flask(__name__)

@app.route('/enrollment', methods=["POST"])
def enrollment():
    username = request.json['username']
    enrollment_signatures = []
    for sig in request.json["signatures"]:
        enrollment_signatures.append(feat_ext.read_json(sig).to_numpy())

    new_user = crud.add_user(username, enrollment_signatures)

    single_min_tpl = tpl.get_single_min_tpl(enrollment_signatures, 1)
    eb_dba_tpl, ls = tpl.get_ls_dba_tpl(enrollment_signatures, 5, 1)

    crud.add_single_min_tpl(new_user.id, single_min_tpl)
    crud.add_eb_dba_tpl(new_user.id, eb_dba_tpl)
    crud.add_ls_dba_tpl(new_user.id, eb_dba_tpl, ls)

    return {
        "msg": "success"
    }


@app.route('/verification/single_min', methods=["GET"])
def verification_single_min():
    username = request.json['username']
    signature = feat_ext.read_json(request.json["signature"]).to_numpy()

    user_id = crud.get_user_id_by_name(username)
    single_min_tpl = crud.get_single_min_tpl(user_id)
    res = dtw.DTW(signature, single_min_tpl)

    current_app.logger.debug(f'DTW res: {res}')

    return {
        "res": res
    }


@app.route('/verification/multi_mean', methods=["GET"])
def verification_multi_mean():
    username = request.json['username']
    signature = feat_ext.read_json(request.json["signature"]).to_numpy()

    user_id = crud.get_user_id_by_name(username)
    signatures = crud.get_multi_tpl(user_id)
    res = tpl.get_multi_mean_dtw(signatures, signature, 1)

    current_app.logger.debug(f'DTW res: {res}')

    return {
        "res": res
    }


@app.route('/verification/eb_dba', methods=["GET"])
def verification_eb_dba():
    username = request.json['username']
    signature = feat_ext.read_json(request.json["signature"]).to_numpy()

    user_id = crud.get_user_id_by_name(username)
    eb_dba_tpl = crud.get_eb_dba_tpl(user_id)
    res = dtw.DTW(signature, eb_dba_tpl)

    current_app.logger.debug(f'DTW res: {res}')

    return {
        "res": res
    }


@app.route('/verification/ls_dba', methods=["GET"])
def verification_ls_dba():
    username = request.json['username']
    signature = feat_ext.read_json(request.json["signature"]).to_numpy()

    user_id = crud.get_user_id_by_name(username)
    eb_dba_tpl, ls = crud.get_ls_dba_tpl(user_id)
    res = dtw.DTW(signature, eb_dba_tpl, local_stability=ls)

    current_app.logger.debug(f'DTW res: {res}')

    return {
        "res": res
    }


if __name__ == "__main__":
    app.run()
