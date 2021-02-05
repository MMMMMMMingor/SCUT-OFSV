import matplotlib.pyplot as plt
import util
import numpy as np
import dtw


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

    with util.my_timer("pcolormesh_DTW..."):
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
