import sys
from model import User, SingleMin, MultiMean, EB_DBA, LS_DBA
import pickle
import numpy as np

sys.path.append("../")
import algo.core.dtw as dtw
import algo.core.template as tpl
import util

def add_user(username: str) -> User:
    new_user = User.create(name=username)
    return new_user


def get_user(user_id: int) -> User:
    user = User.select().where(User.id == user_id).get()
    return user


def get_user_id_by_name(username: str) -> int:
    user_id = User.select(User.id).where(User.name == username).get()
    return user_id


def add_single_min_tpl(user_id: int, single_min_tpl: np.ndarray, threshold: float) -> SingleMin:
    buffer = pickle.dumps(single_min_tpl)
    new_one = SingleMin.create(
        user_id=user_id, single_min_tpl=buffer, threshold=threshold)
    return new_one


def get_single_min_tpl(user_id: int) -> (np.ndarray, float):
    single_min = SingleMin.select().where(SingleMin.user_id == user_id).get()
    return pickle.loads(single_min.single_min_tpl), single_min.threshold


def add_multi_mean_tpl(user_id: int, signatures: list, threshold: float) -> MultiMean:
    buffer = pickle.dumps(signatures)
    new_one = MultiMean.create(
        user_id=user_id, signatures=buffer, threshold=threshold)
    return new_one


def get_multi_tpl(user_id) -> (list, float):
    multi_mean = MultiMean.select().where(MultiMean.user_id == user_id).get()
    return pickle.loads(multi_mean.signatures), multi_mean.threshold


def add_eb_dba_tpl(user_id: int, eb_dba_tpl: np.ndarray, threshold: float) -> EB_DBA:
    buffer = pickle.dumps(eb_dba_tpl)
    new_one = EB_DBA.create(
        user_id=user_id, eb_dba_tpl=buffer, threshold=threshold)
    return new_one


def get_eb_dba_tpl(user_id: int) -> (np.ndarray, float):
    eb_dba = EB_DBA.select().where(EB_DBA.user_id == user_id).get()
    return pickle.loads(eb_dba.eb_dba_tpl), eb_dba.threshold


def add_ls_dba_tpl(user_id: int, eb_dba_tpl: np.ndarray, ls: np.ndarray, threshold: float) -> LS_DBA:
    buffer1 = pickle.dumps(eb_dba_tpl)
    buffer2 = pickle.dumps(ls)
    new_one = LS_DBA.create(
        user_id=user_id, eb_dba_tpl=buffer1, ls=buffer2, threshold=threshold)
    return new_one


def get_ls_dba_tpl(user_id: int) -> (np.ndarray, np.ndarray, float):
    ls_dba = LS_DBA.select().where(LS_DBA.user_id == user_id).get()
    return pickle.loads(ls_dba.eb_dba_tpl), pickle.loads(ls_dba.ls), ls_dba.threshold


def cal_enroll_threshold(single_min_tpl: np.ndarray, eb_dba_tpl: np.ndarray, ls: np.ndarray, enrollment_signatures: list) -> (float, float, float, float):
    with util.my_timer('single min'):
        single_min_thresholds = []
        for sig in enrollment_signatures:
            res = dtw.DTW(single_min_tpl, sig)
            single_min_thresholds.append(res)

    with util.my_timer('multi mean'):
        multi_mean_thresholds = []
        for i, sig in enumerate(enrollment_signatures):
            res = tpl.get_multi_mean_dtw(enrollment_signatures[0:i] + enrollment_signatures[i: -1], sig)
            multi_mean_thresholds.append(res)

    with util.my_timer('eb-dba'):
        eb_dba_thresholds = []
        for sig in enrollment_signatures:
            res = dtw.DTW(sig, eb_dba_tpl)
            eb_dba_thresholds.append(res)

    with util.my_timer('ls-dba'):
        ls_dba_thresholds = []
        for sig in enrollment_signatures:
            res = dtw.DTW(sig, eb_dba_tpl, local_stability=ls)
            ls_dba_thresholds.append(res)

    return max(single_min_thresholds), max(multi_mean_thresholds), max(eb_dba_thresholds), max(ls_dba_thresholds)