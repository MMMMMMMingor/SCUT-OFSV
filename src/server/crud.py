from orm import Database
from model import User, SingleMin, EB_DBA, LS_DBA
import pickle
import numpy as np


def add_user(username: str, signatures: list) -> User:
    new_user = User.create(name=username, signatures=pickle.dumps(signatures))
    return new_user


def get_user(user_id: int) -> User:
    user = User.select().where(User.id == user_id).get()
    return user


def get_user_id_by_name(username: str) -> int:
    user_id = User.select(User.id).where(User.name == username).get()
    return user_id


def add_single_min_tpl(user_id: int, single_min_tpl: np.ndarray) -> SingleMin:
    buffer = pickle.dumps(single_min_tpl)
    new_one = SingleMin.create(user_id=user_id, single_min_tpl=buffer)
    return new_one

def get_multi_tpl(user_id) -> list:
    user = User.select().where(User.id == user_id).get()
    return pickle.loads(user.signatures)


def get_single_min_tpl(user_id: int) -> np.ndarray:
    single_min = SingleMin.select().where(SingleMin.user_id == user_id).get()
    return pickle.loads(single_min.single_min_tpl)


def add_eb_dba_tpl(user_id: int, eb_dba_tpl: np.ndarray) -> EB_DBA:
    buffer = pickle.dumps(eb_dba_tpl)
    new_one = EB_DBA.create(user_id=user_id, eb_dba_tpl=buffer)
    return new_one


def get_eb_dba_tpl(user_id: int) -> np.ndarray:
    eb_dba = EB_DBA.select().where(EB_DBA.user_id == user_id).get()
    return pickle.loads(eb_dba.eb_dba_tpl)


def add_ls_dba_tpl(user_id: int, eb_dba_tpl: np.ndarray, ls: np.ndarray) -> EB_DBA:
    buffer1 = pickle.dumps(eb_dba_tpl)
    buffer2 = pickle.dumps(ls)
    new_one = LS_DBA.create(user_id=user_id, eb_dba_tpl=buffer1, ls=buffer2)
    return new_one


def get_ls_dba_tpl(user_id: int) -> (np.ndarray, np.ndarray):
    eb_dba = LS_DBA.select().where(LS_DBA.user_id == user_id).get()
    return pickle.loads(eb_dba.eb_dba_tpl), pickle.loads(eb_dba.ls)
