from enum import Flag
import time
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import algo.core.dtw as dtw
from mpl_toolkits.mplot3d import Axes3D
import algo.core.template as tpl

OKGREEN = '\033[92m'
ENDC = '\033[0m'


class my_timer():
    def __init__(self, str):
        print(str)

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print(f"    cost: {time.time() - self.start} seconds")


def plot_signatures(read_fun, user_no: int, sig_num: int, inverse_axis=False):
    """
    example:
            plot_signatures(read_MMSIG, 1, 40)
    """
    fig, ax_arr = plt.subplots(4, 10, figsize=(17, 3.4))

    for sig in range(1, sig_num + 1):
        data = read_fun(user_no, sig)

        data_x, data_y = data["x"], data["y"]

        ax = ax_arr[int((sig - 1) / 10), int(sig % 10) - 1]
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.plot(data_x, data_y)

        if inverse_axis == True:
            ax.invert_xaxis()
            ax.invert_yaxis()

    plt.show()


def scatter_signatures(read_fun, user_no: int, sig_num: int, inverse_axis=False):
    """
    example:
            plot_signatures(read_MMSIG, 1, 40)
    """
    fig, ax_arr = plt.subplots(4, 10, figsize=(17, 3.4))

    for sig in range(1, sig_num + 1):
        data = read_fun(user_no, sig)

        data_x, data_y = data["x"], data["y"]

        ax = ax_arr[int((sig - 1) / 10), int(sig % 10) - 1]
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.scatter(data_x, data_y)

        if inverse_axis == True:
            ax.invert_xaxis()
            ax.invert_yaxis()

    plt.show()


def plot_signature(data: pd.DataFrame, inverse_axis: bool = True):
    data_x, data_y = data["x"], data["y"]

    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set_xlabel("x index")
    ax.set_ylabel("y index")
    ax.set_title("3D signature")

    if inverse_axis == True:
        ax.invert_xaxis()
        ax.invert_yaxis()

    ax.plot(data_x, data_y, "black", linewidth=3)

    plt.show()

def plot_signature_3D(data: pd.DataFrame):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    data_x, data_y, data_z = data["x"], data["y"], data["z"]

    ax.set_xlabel("x index")
    ax.set_ylabel("y index")
    ax.set_zlabel("z index")
    ax.set_title("3D signature")

    ax.plot(data_x, data_y, data_z)

    plt.show()


def plot_signatures_3D(read_fun, user_no: int, sig_num: int):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    for sig in range(1, sig_num + 1):
        data = read_fun(user_no, sig)
        data_x, data_y, data_z = data["x"], data["y"], data["z"]

        ax.set_xlabel("x index")
        ax.set_ylabel("y index")
        ax.set_zlabel("z index")
        ax.set_title("3D signature")

        ax.plot(data_x, data_y, data_z)

    plt.show()


def scatter_signature_3D(data: pd.DataFrame):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    data_x, data_y, data_z = data["x"], data["y"], data["z"]

    ax.set_xlabel("x index")
    ax.set_ylabel("y index")
    ax.set_zlabel("z index")
    ax.set_title("3D signature")

    ax.scatter(data_x, data_y, data_z)

    plt.show()


def plot_signatures_features(read_fun, user_no, sig_num, inverse_axis=False):
    sig = read_fun(user_no, sig_num)

    columns_len = len(sig.columns)

    fig, ax_arr = plt.subplots(4, 2, figsize=(6, 4))
    # fig, ax_arr = plt.subplots(columns_len+1, figsize=(3, 8))

    ax = ax_arr[0, 0]
    if inverse_axis == True:
        ax.invert_xaxis()
        ax.invert_yaxis()
    ax.set_xticks([])
    ax.set_yticks([])
    ax.plot(sig["x"], sig["y"])

    for idx, column in enumerate(sig.columns):
        idx = idx + 1
        ax = ax_arr[idx % 4, int(idx / 4)]
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_ylabel(column)

        data = sig[column]
        ax.plot(data)

    plt.show()

def plot_signature_in_timestamp(data: pd.DataFrame):
    plt.rcParams["figure.figsize"] = (12,4)
    for ts, x in zip(data['ts'], data['x']):
        plt.vlines(x=ts, ymin=0, ymax=x)

    plt.scatter(data['ts'], data['x'], c='green')
    plt.show()

def plot_mean_template_with_train(mean_tpl: np.ndarray, training_sig: list):
    for sig in training_sig:
        plt.plot(sig[:, 0], sig[:, 1], "--")
    plt.plot(mean_tpl[:, 0], mean_tpl[:, 1], "black", linewidth=3)
    plt.show()


def plot_mean_template_with_train_3D(mean_tpl: np.ndarray, training_sig: list):
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    for sig in training_sig:
        ax.plot(sig[:, 0], sig[:, 1], sig[:, 2], "--")
    ax.plot(mean_tpl[:, 0], mean_tpl[:, 1], mean_tpl[:, 2], "black", linewidth=3)
    plt.show()


def heatmap_DTW(read_fun, user_no: int, sig_num: int, verbose=False):
    """
    example:
            pcolormesh_DTW(read_MMSIG, 1, 40)
    """
    sig_array = [read_fun(user_no, i + 1).to_numpy() for i in range(sig_num)]

    dist_mesh = np.zeros((sig_num, sig_num))

    with my_timer("pcolormesh_DTW..."):
        for sig in range(sig_num):

            for other_sig in range(sig + 1, sig_num):
                if(sig == other_sig):
                    continue

                data1 = sig_array[sig]
                data2 = sig_array[other_sig]
                dist = dtw.DTW(data1, data2)
                dist_mesh[sig, other_sig] = dist

                if(verbose):
                    print(f"sig: {sig}, other_sig: {other_sig}, DTW: {dist}")

    dist_mesh = dist_mesh + dist_mesh.T

    plt.title("DTW heatmap between signatures")
    plt.imshow(dist_mesh)
    plt.show()


def mean_without_min_max(distances: list) -> float:
    sum_without_min_max = sum(distances) - max(distances) - min(distances)

    return sum_without_min_max / len(distances) - 2


def personal_threshold(distances: list, delta: float = 2.8) -> float:
    threshold = np.mean(distances) + delta * np.sqrt(np.var(distances)) 

    return threshold


def get_single_min_threshold(single_min_tpl: np.ndarray, enrollment_signatures: list) -> float:
    single_min_thresholds = []
    for sig in enrollment_signatures:
        res = dtw.DTW(single_min_tpl, sig)
        single_min_thresholds.append(res)
    # return mean_without_min_max(single_min_thresholds)
    # return max(single_min_thresholds)
    return personal_threshold(single_min_thresholds, delta=2.8)


def get_multi_mean_threshold(enrollment_signatures: list) -> float:
    multi_mean_thresholds = []
    for i, sig in enumerate(enrollment_signatures):
        res = tpl.get_multi_mean_dtw(enrollment_signatures[0:i] + enrollment_signatures[i: -1], sig)
        multi_mean_thresholds.append(res)
    # return mean_without_min_max(multi_mean_thresholds)
    # return max(multi_mean_thresholds)
    return personal_threshold(multi_mean_thresholds, delta=2.8)


def get_eb_dba_tpl_threshold(eb_dba_tpl: np.ndarray, enrollment_signatures: list) -> float:
    eb_dba_thresholds = []
    for sig in enrollment_signatures:
        res = dtw.DTW(sig, eb_dba_tpl)
        eb_dba_thresholds.append(res)
    # return mean_without_min_max(eb_dba_thresholds)
    # return max(eb_dba_thresholds)
    return personal_threshold(eb_dba_thresholds, delta=2.8)


def get_ls_dba_tpl_threshold(eb_dba_tpl: np.ndarray, ls: np.ndarray, enrollment_signatures: list) -> float:
    ls_dba_thresholds = []
    for sig in enrollment_signatures:
        res = dtw.DTW(sig, eb_dba_tpl, local_stability=ls)
        ls_dba_thresholds.append(res)
    # return mean_without_min_max(ls_dba_thresholds)
    # return max(ls_dba_thresholds)
    return personal_threshold(ls_dba_thresholds, delta=2.8)
