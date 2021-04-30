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


def plot_signatures_features(read_fun, user_no, sig_num):
    sig = read_fun(user_no, sig_num)

    columns_len = len(sig.columns)

    fig, ax_arr = plt.subplots(columns_len + 1, figsize=(3, 8))

    ax = ax_arr[0]
    ax.set_xticks([])
    ax.set_yticks([])
    ax.plot(sig["x"], sig["y"])

    for idx, column in enumerate(sig.columns):
        idx = idx + 1
        ax = ax_arr[idx]
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_ylabel(column)

        data = sig[column]
        ax.plot(data)

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


def mean_without_min_max(thresholds: list) -> float:
    sum_without_min_max = sum(thresholds) - max(thresholds) - min(thresholds)

    return sum_without_min_max / len(thresholds) - 2

def get_single_min_threshold(single_min_tpl: np.ndarray, enrollment_signatures: list) -> float:
    single_min_thresholds = []
    for sig in enrollment_signatures:
        res = dtw.DTW(single_min_tpl, sig)
        single_min_thresholds.append(res)
    return mean_without_min_max(single_min_thresholds)


def get_multi_mean_threshold(enrollment_signatures: list) -> float:
    multi_mean_thresholds = []
    for i, sig in enumerate(enrollment_signatures):
        res = tpl.get_multi_mean_dtw(enrollment_signatures[0:i] + enrollment_signatures[i: -1], sig)
        multi_mean_thresholds.append(res)
    return mean_without_min_max(multi_mean_thresholds)


def get_eb_dba_tpl_threshold(eb_dba_tpl: np.ndarray, enrollment_signatures: list) -> float:
    eb_dba_thresholds = []
    for sig in enrollment_signatures:
        res = dtw.DTW(sig, eb_dba_tpl)
        eb_dba_thresholds.append(res)
    return mean_without_min_max(eb_dba_thresholds)


def get_ls_dba_tpl_threshold(eb_dba_tpl: np.ndarray, ls: np.ndarray, enrollment_signatures: list) -> float:
    ls_dba_thresholds = []
    for sig in enrollment_signatures:
        res = dtw.DTW(sig, eb_dba_tpl, local_stability=ls)
        ls_dba_thresholds.append(res)
    return mean_without_min_max(ls_dba_thresholds)