import sys
import time
from flask import Flask, request, current_app, render_template
from markupsafe import escape
import crud
import numpy as np

sys.path.append("../")
import algo.core.dtw as dtw
import algo.core.template as tpl
import feat_ext
import util


app = Flask(__name__)

@app.route('/api/user/<username>', methods=["GET"])
def user_exit(username):
    try:
        user = crud.get_user_id_by_name(escape(username))
    except(Exception):
        return {'exist': 'false'}
    
    return {'exist': 'true'}


@app.route('/api/enrollment', methods=["POST"])
def enrollment():
    try:
        with util.my_timer('enrollment'):
            username = request.json['username']
            enrollment_signatures = []
            for sig in request.json["signatures"]:
                enrollment_signatures.append(feat_ext.read_dict(sig).to_numpy())

            new_user = crud.add_user(username)

            with util.my_timer('cal single'):
                single_min_tpl = tpl.get_single_min_tpl(enrollment_signatures, 1)

            with util.my_timer('cal ls-dba'):
                eb_dba_tpl, ls = tpl.get_ls_dba_tpl(enrollment_signatures, 5, 1)

            with util.my_timer('cal_enroll_threshold'):
                t1, t2, t3, t4 = crud.cal_enroll_threshold(single_min_tpl, eb_dba_tpl, ls, enrollment_signatures)

            crud.add_single_min_tpl(new_user.id, single_min_tpl, t1)
            crud.add_multi_mean_tpl(new_user.id, enrollment_signatures, t2)
            crud.add_eb_dba_tpl(new_user.id, eb_dba_tpl, t3)
            crud.add_ls_dba_tpl(new_user.id, eb_dba_tpl, ls, t4)

            return {"msg": "success"}
    except:
        return {'msg', 'false'}


@app.route('/api/verification/single_min', methods=["POST"])
def verification_single_min():
    start = time.time()
    username = request.json['username']
    signature = feat_ext.read_dict(request.json["signature"]).to_numpy()

    user_id = crud.get_user_id_by_name(username)
    single_min_tpl, threshold = crud.get_single_min_tpl(user_id)
    res = dtw.DTW(signature, single_min_tpl)

    current_app.logger.debug(f'DTW res: {res}')

    if res < threshold:
        result = crud.add_result(
            user= username, 
            algo= 'single-min-template',
            threshold= round(threshold, 3),
            result= round(res, 3),
            cost= round(time.time() - start, 5),
        )
        return {'res_id': result.id,'true_or_false': 'true'}

    return {'res': res, 'thres': threshold, 'true_or_false': 'false'}


@app.route('/api/verification/multi_mean', methods=["POST"])
def verification_multi_mean():
    start = time.time()
    username = request.json['username']
    signature = feat_ext.read_dict(request.json["signature"]).to_numpy()

    user_id = crud.get_user_id_by_name(username)
    signatures, threshold = crud.get_multi_tpl(user_id)
    res = tpl.get_multi_mean_dtw(signatures, signature)

    current_app.logger.debug(f'DTW res: {res}')

    if res < threshold:
        result = crud.add_result(
            user= username, 
            algo= 'multi-mean-template',
            threshold= round(threshold, 3),
            result= round(res, 3),
            cost= round(time.time() - start, 5),
        )
        return {'res_id': result.id,'true_or_false': 'true'}

    return {'res': res, 'thres': threshold, 'true_or_false': 'false'}


@app.route('/api/verification/eb_dba', methods=["POST"])
def verification_eb_dba():
    start = time.time()
    username = request.json['username']
    signature = feat_ext.read_dict(request.json["signature"]).to_numpy()

    user_id = crud.get_user_id_by_name(username)
    eb_dba_tpl, threshold = crud.get_eb_dba_tpl(user_id)
    res = dtw.DTW(signature, eb_dba_tpl)

    current_app.logger.info(f'DTW res: {res}')

    if res < threshold:
        result = crud.add_result(
            user= username, 
            algo= 'eb-dba-template',
            threshold= round(threshold, 3),
            result= round(res, 3),
            cost= round(time.time() - start, 5),
        )
        return {'res_id': result.id,'true_or_false': 'true'}

    return {'res': res, 'thres': threshold, 'true_or_false': 'false'}


@app.route('/api/verification/ls_dba', methods=["POST"])
def verification_ls_dba():
    start = time.time()
    username = request.json['username']
    signature = feat_ext.read_dict(request.json["signature"]).to_numpy()

    user_id = crud.get_user_id_by_name(username)
    eb_dba_tpl, ls, threshold = crud.get_ls_dba_tpl(user_id)
    res = dtw.DTW(signature, eb_dba_tpl, local_stability=ls)

    current_app.logger.debug(f'DTW res: {res}')

    if res < threshold:
        result = crud.add_result(
            user= username, 
            algo= 'ls-dba-template',
            threshold= round(threshold, 3),
            result= round(res, 3),
            cost= round(time.time() - start, 5),
        )
        return {'res_id': result.id,'true_or_false': 'true'}

    return {'res': res, 'thres': threshold, 'true_or_false': 'false'}

@app.route('/api/result/<res_id>', methods=["GET"])
def get_result(res_id):
    res = crud.get_result(res_id)
    return render_template('template.html', user=res.user, algo=res.algo, threshold=res.threshold, result=res.result, cost=res.cost)


if __name__ == "__main__":
    app.run()
    # from waitress import serve
    # serve(app, host="0.0.0.0", port=5000) 
