
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats


def read_MMSIG(user_no: int, index: int) -> pd.DataFrame:
    if user_no < 10:
        filename = f"../inair/U0{user_no}S{index}.txt"
    else:
        filename = f"../inair/U{user_no}S{index}.txt"

    data = pd.read_table(filename, sep=" ", dtype="int", header=None)

    data = data.apply(stats.zscore)

    return data


def read_SVC2004(user_no: int, index: int) -> pd.DataFrame:
    filename = f"../SVC2004/U{user_no}S{index}.TXT"

    data = pd.read_table(filename, sep=" ", skiprows=1,
                         dtype="int", header=None)

    data = data.apply(stats.zscore)

    # return data
    return data.drop(columns=[2])


def plot_signatures(read_fun, user_no: int, sig_num: int, inverse_axis=False):
    """
    example:
            plot_signatures(read_MMSIG, 1, 40)
    """
    fig, ax_arr = plt.subplots(4, 10)

    for sig in range(1, sig_num + 1):
        data = read_fun(user_no, sig)

        data_x, data_y = data.iloc[:, 0], data.iloc[:, 1]

        ax = ax_arr[int((sig - 1) / 10), int(sig % 10) - 1]
        ax.get_xaxis().set_visible(False)
        ax.get_yaxis().set_visible(False)
        ax.plot(data_x, data_y)

        if inverse_axis == True:
            ax.invert_xaxis()
            ax.invert_yaxis()

    plt.show()


def pcolormesh_DTW(read_fun, user_no: int, sig_num: int, verbose=False):
    """
    example:
            pcolormesh_DTW(read_MMSIG, 1, 40)
    """
    sig_array = [read_fun(user_no, i + 1) for i in range(sig_num)]

    # print(sig_array[0])

    dist_mesh = np.zeros((sig_num, sig_num))

    for sig in range(sig_num):

        for other_sig in range(sig + 1, sig_num):
            if(sig == other_sig):
                continue

            data1 = sig_array[sig]
            data2 = sig_array[other_sig]
            dist = DTW(data1, data2)
            dist_mesh[sig, other_sig] = dist

            if(verbose):
                print(f"sig: {sig}, other_sig: {other_sig}, DTW: {dist}")

    dist_mesh = dist_mesh + dist_mesh.T

    plt.pcolormesh(dist_mesh)
    plt.show()


def DTW(lhs: pd.DataFrame, rhs: pd.DataFrame):
    """
    dynamic timing warping
        lhs and rhs should have same features num.
    """
    lhs, rhs = lhs.to_numpy().T, rhs.to_numpy().T
    features_num, N = lhs.shape
    _, M = rhs.shape

    if(features_num != _):
        raise Exception("features num not equals!")

    # distance calculate
    d = np.zeros((N, M))
    for i in range(features_num):
        lhs_feat = lhs[i, :].reshape(N, 1)
        rhs_feat = rhs[i, :]
        res = lhs_feat - rhs_feat  # numpy boardcast trick
        res = np.sqrt(res ** 2)
        d += res

    # DTW core (dynamic program)
    D = np.zeros((N, M))
    D[0, 0] = d[0, 0]

    for i in range(1, N):
        D[i, 0] = d[i, 0] + D[i - 1, 0]

    for j in range(1, M):
        D[0, j] = d[0, j] + D[0, j - 1]

    for i in range(1, N):
        for j in range(1, M):
            D[i, j] = d[i, j] + min(D[i - 1, j], D[i - 1, j - 1], D[i, j - 1])

    return D[N - 1, M - 1]


def classification(read_fun, users_num: int, training_sample: int, genuine: int, forged: int):
    if training_sample <= 0 or genuine < training_sample or forged < 0:
        raise Exception("args has error")

    sig_num = genuine + forged

    # loading signature
    users_data = []
    for u in range(users_num):
        sig_arr = [read_fun(u + 1, sig + 1) for sig in range(sig_num)]
        users_data.append(sig_arr)

    # calculate DTW
    DTW_res = np.zeros((users_num, sig_num, training_sample))
    for u in range(users_num):
        for sig in range(training_sample, sig_num):
            for other_sig in range(training_sample):
                DTW_res[u, sig, other_sig] = DTW(users_data[u][sig],
                                                 users_data[u][other_sig])

    DTW_mean = np.zeros((users_num, sig_num))
    for u in range(users_num):
        for sig in range(training_sample, sig_num):
            DTW_mean[u, sig] = np.mean(DTW_res[u, sig])

    # calculate FAR, FRR, EER
    threshold_array = np.arange(5, 200, 5, dtype="float")
    FA = np.zeros(len(threshold_array), dtype="float")
    FR = np.zeros(len(threshold_array), dtype="float")

    for index, thre in enumerate(threshold_array):
        for u in range(users_num):
            for sig in range(training_sample, genuine):
                if DTW_mean[u, sig] > thre:
                    FR[index] = FR[index] + 1

            for sig in range(genuine, genuine + forged):
                if DTW_mean[u, sig] < thre:
                    FA[index] = FA[index] + 1

    genuine_count = users_num * (genuine - training_sample)
    forged_count = users_num * forged
    FAR = FA / genuine_count
    FRR = FR / forged_count
    # calculate cross point (ERR)
    idx = np.argwhere(np.diff(np.sign(FAR - FRR))).flatten()

    plt.plot(threshold_array, FAR, label="FAR")
    plt.plot(threshold_array, FRR, label="FRR")
    plt.plot(threshold_array[idx], FRR[idx], 'ro', label="ERR")
    plt.title("ROC")
    plt.xlabel('threhold')
    plt.ylabel('percentage')
    plt.legend()
    plt.show()


if __name__ == "__main__":

    # plot_signatures(read_SVC2004, 1, 40)

    # pcolormesh_DTW(read_SVC2004, 3, 40, True)

    users_num = 5
    training_sample = 5
    genuine = 20
    forged = 20
    classification(read_SVC2004, users_num, training_sample, genuine, forged)

    pass
