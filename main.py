import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import time
import random


class my_timer():
    def __init__(self, str):
        print(str)

    def __enter__(self):
        self.start = time.time()

    def __exit__(self, exc_type, exc_value, exc_traceback):
        print(f"    cost: {time.time() - self.start} seconds")


def derivation(seq, ts=None) -> np.ndarray:
    """
        two order regression
        seq: x, y coordinates sequence
        ts: int or pd.Series, unit is milisecond
    """
    N = len(seq)

    if(type(ts) == int):
        d_ts = np.zeros(N, dtype="int") + ts
    elif(type(ts) == pd.Series):
        d_ts = ts.diff(2) / 2
    else:
        raise Exception("ts error")

    d_seq = np.zeros((N))

    d_seq[0] = (2*seq[2] + seq[1] - 3*seq[0]) / 5
    d_seq[1] = (2*seq[3] + seq[2] - 2*seq[1] - seq[0]) / 6
    for i in range(2, N - 2):
        d_seq[i] = (2*seq[i+2] + seq[i+1] - seq[i-1] - 2*seq[i-2]) / d_ts[i]
    d_seq[N - 2] = (seq[N-1] + 2*seq[N-2] - 2*seq[N-3] - seq[N-4]) / 6
    d_seq[N - 1] = (3*seq[N-1] - seq[N-2] - 2*seq[N-3]) / 5

    return d_seq


def feature_extraction(data: pd.DataFrame) -> pd.DataFrame:
    ts = data["ts"] if "ts" in data.columns else 10

    d_x = derivation(data["x"], ts=ts)
    d_y = derivation(data["y"], ts=ts)

    vel = np.sqrt(d_x*d_x + d_y*d_y)  # velocity

    N = len(d_x)
    angel = np.zeros((N))  # angel
    for i in range(N):
        if d_x[i] != 0:
            angel[i] = np.arctan(d_y[i] / d_x[i])
        elif d_x[i] == 0 and d_y[i] > 0:
            angel[i] = np.pi / 2
        elif d_x[i] == 0 and d_y[i] < 0:
            angel[i] = -np.pi / 2
        else:
            angel[i] = 0

    d_vel = derivation(vel, ts)
    d_angle = derivation(angel, ts)

    # log curvature radius
    logcr = np.log((np.abs(vel) + 0.01) / (np.abs(d_angle) + 0.01))
    # total acceleration magnitude
    tam = np.sqrt((d_vel*d_vel) + (vel*vel*d_angle*d_angle))

    return pd.concat([data, pd.DataFrame({"vel": vel, "angel": angel, "logcr": logcr, "tam": tam})], axis=1)


def read_MMSIG(user_no: int, index: int) -> pd.DataFrame:
    if user_no < 10:
        filename = f"../inair/U0{user_no}S{index}.txt"
    else:
        filename = f"../inair/U{user_no}S{index}.txt"

    data = pd.read_table(filename, sep=" ", dtype="int",
                         header=None, names=["x", "y"])

    # feature extraction & data preprocess
    data = feature_extraction(data)
    data = data.apply(stats.zscore)

    return data


def read_SVC2004(user_no: int, index: int) -> pd.DataFrame:
    filename = f"../SVC2004/U{user_no}S{index}.TXT"

    data = pd.read_table(filename, sep=" ", skiprows=1,
                         dtype="int", header=None, names=["x", "y", "ts", "pen"])

    # feature extraction & data preprocess
    data = feature_extraction(data)
    data = data.apply(stats.zscore)

    # return data
    return data.drop(columns=["ts", "pen"])


def plot_signatures(read_fun, user_no: int, sig_num: int, inverse_axis=False):
    """
    example:
            plot_signatures(read_MMSIG, 1, 40)
    """
    fig, ax_arr = plt.subplots(4, 10)

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
    sig_array = [read_fun(user_no, i + 1) for i in range(sig_num)]

    columns = sig_array[0].columns
    columns_len = len(columns)

    fig, ax_arr = plt.subplots(columns_len)

    for idx, column in enumerate(columns):
        ax = ax_arr[idx]
        ax.set_xticks([])
        ax.set_yticks([])
        ax.set_ylabel(column)
        for sig in range(sig_num):
            data = sig_array[sig][column]
            ax.plot(data)

    plt.show()


def pcolormesh_DTW(read_fun, user_no: int, sig_num: int, verbose=False):
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
                dist = DTW(data1, data2)
                dist_mesh[sig, other_sig] = dist

                if(verbose):
                    print(f"sig: {sig}, other_sig: {other_sig}, DTW: {dist}")

    dist_mesh = dist_mesh + dist_mesh.T

    plt.pcolormesh(dist_mesh)
    plt.show()


def DTW(lhs: pd.DataFrame, rhs: pd.DataFrame, with_path=False):
    """
    dependent dynamic timing warping
        lhs and rhs should have same number of features.
    """
    lhs, rhs = lhs.T, rhs.T
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
    D = d

    for i in range(1, N):
        D[i, 0] += D[i - 1, 0]

    for j in range(1, M):
        D[0, j] += D[0, j - 1]

    for i in range(1, N):
        for j in range(1, M):
            D[i, j] += min(D[i - 1, j], D[i - 1, j - 1], D[i, j - 1])

    avg_L = np.sqrt(M * N)
    result = D[N - 1, M - 1] / avg_L

    if with_path == False:
        return result

    # get the DTW path
    path = []
    i, j = N - 1, M - 1
    path.append((i, j))
    while i > 0 or j > 0:
        idx = np.argmin([D[i - 1, j], D[i, j - 1], D[i - 1, j - 1]])
        if idx == 0:
            i = i - 1
        elif idx == 1:
            j = j - 1
        else:
            i, j = i - 1, j - 1
        path.append((i, j))

    path = path[:: -1]

    return result, path


def user_independent_ROC(users_num: int, training: int, genuine: int, forged: int, DTW_matrix, title="no title") -> float:
    threshold_array = np.arange(0, 5, 0.01, dtype="float")
    FA = np.zeros(len(threshold_array), dtype="int")
    FR = np.zeros(len(threshold_array), dtype="int")

    # print(DTW_matrix)

    for index, thre in enumerate(threshold_array):
        for u in range(users_num):
            for sig in range(training, genuine):
                if DTW_matrix[u, sig] > thre:
                    FR[index] = FR[index] + 1

            for sig in range(genuine, genuine + forged):
                if DTW_matrix[u, sig] < thre:
                    FA[index] = FA[index] + 1

    # calculate cross point (EER)
    genuine_count = users_num * (genuine - training)
    forged_count = users_num * forged
    FAR = FA / forged_count
    FRR = FR / genuine_count

    idx = np.argwhere(np.diff(np.sign(FAR - FRR))).reshape(-1) + 1
    if len(idx) == 0:
        raise Exception("no cross point")
    idx = idx[0]
    EER = ((FRR[idx] + FAR[idx]) / 2)

    plt.plot(FRR, FAR, label="ROC")
    plt.plot(FRR[idx], EER, 'ro',
             label=f"EER: {round(EER*100, 2)}%")
    plt.title("user independent ROC")
    plt.xlabel("False Reject Rate")
    plt.ylabel("False Acept Rate")
    plt.legend()
    plt.title(title)
    # plt.show()

    print(f"user-independent EER: {EER}, threshold: {threshold_array[idx]}")
    return EER


def user_dependent_ROC(users_num: int, training: int, genuine: int, forged: int, DTW_matrix) -> float:
    threshold_array = np.arange(0, 5, 0.01, dtype="float")
    l = len(threshold_array)
    EER = np.zeros(users_num, dtype="float")
    EER_idx = np.zeros(users_num, dtype="float")

    # print(DTW_matrix)

    for u in range(users_num):
        FA = np.zeros(l, dtype="int")
        FR = np.zeros(l, dtype="int")
        for index, thre in enumerate(threshold_array):
            for sig in range(training, genuine):
                if DTW_matrix[u, sig] > thre:
                    FR[index] = FR[index] + 1

            for sig in range(genuine, genuine + forged):
                if DTW_matrix[u, sig] < thre:
                    FA[index] = FA[index] + 1

        # calculate cross point EER)
        FAR = FA / forged
        FRR = FR / (genuine - training)

        idx = np.argwhere(np.diff(np.sign(FAR - FRR))).reshape(-1)
        if len(idx) == 0:
            raise Exception(f"no cross point, user_no: {u + 1}")

        idx = idx[0]
        EER_idx[u] = threshold_array[idx]
        EER[u] = np.mean((FRR[idx] + FAR[idx]) / 2)

    print("user-dependent threshold", EER_idx)

    # calculate mean (EER)
    EER = np.mean(EER)

    print(f"user-dependent EER: {EER}")
    return EER


def single_tpl_min_based_classify(read_fun, users_num: int, training: int, genuine: int, forged: int):
    if training <= 0 or genuine < training or forged < 0:
        raise Exception("args has error")

    sig_num = genuine + forged

    # loading signature
    with my_timer("loading signature... "):
        users_data = []
        for u in range(users_num):
            sig_arr = [read_fun(u + 1, sig + 1).to_numpy()
                       for sig in range(sig_num)]
            users_data.append(sig_arr)

    # finding the signature has minimum DTW with others
    with my_timer("finding the signature has minimum DTW with others..."):
        training_data = []
        for u in range(users_num):
            DTW_between = np.zeros((training, training))
            for sig in range(training):
                for other_sig in range(sig + 1, training):
                    DTW_between[sig, other_sig] = DTW(
                        users_data[u][sig], users_data[u][other_sig])

            DTW_between = DTW_between + DTW_between.T

            min_idx = np.argmin(np.sum(DTW_between, axis=0))
            training_data.append(users_data[u][min_idx])

    # calculate DTW with the minimum signature
    with my_timer("calculating DTW... "):
        DTW_all = np.zeros((users_num, sig_num))
        for u in range(users_num):
            for sig in range(training, sig_num):
                DTW_all[u, sig] = DTW(users_data[u][sig], training_data[u])

    # calculate FAR, FRR, EER
    with my_timer("calculating EER... "):
        ERR = user_dependent_ROC(users_num, training,
                                 genuine, forged, DTW_all)
        ERR = user_independent_ROC(users_num, training,
                                   genuine, forged, DTW_all, "min-based single template")


def mul_tpl_mean_based_classify(read_fun, users_num: int, training: int, genuine: int, forged: int):
    if training <= 0 or genuine < training or forged < 0:
        raise Exception("args has error")

    sig_num = genuine + forged

    # loading signature
    with my_timer("loading signature... "):
        users_data = []
        for u in range(users_num):
            sig_arr = [read_fun(u + 1, sig + 1).to_numpy()
                       for sig in range(sig_num)]
            users_data.append(sig_arr)

    # calculate DTW
    with my_timer("calculating mean DTW... "):
        DTW_all = np.zeros((users_num, sig_num, training))
        for u in range(users_num):
            for sig in range(training, sig_num):
                for other_sig in range(training):
                    DTW_all[u, sig, other_sig] = DTW(users_data[u][sig],
                                                     users_data[u][other_sig])

        DTW_mean = np.zeros((users_num, sig_num))
        for u in range(users_num):
            for sig in range(training, sig_num):
                DTW_mean[u, sig] = np.mean(DTW_all[u, sig])

    # calculate FAR, FRR, EER
    with my_timer("calculating EER... "):
        ERR = user_dependent_ROC(users_num, training,
                                 genuine, forged, DTW_mean)
        ERR = user_independent_ROC(users_num, training,
                                   genuine, forged, DTW_mean, "mean-based multiple template")


def EB_DBA_based_classify(read_fun, users_num: int, training: int, genuine: int, forged: int, times: int):
    if training <= 0 or genuine < training or forged < 0:
        raise Exception("args has error")

    sig_num = genuine + forged

    # loading signature
    with my_timer("loading signature... "):
        users_data = []
        for u in range(users_num):
            sig_arr = [read_fun(u + 1, sig + 1).to_numpy()
                       for sig in range(sig_num)]
            users_data.append(sig_arr)

    # linerear interpolation
    with my_timer("linerear interpolation... "):
        features_num = users_data[0][0].shape[-1]
        original_L = []
        resample_L = []
        for u in range(users_num):
            L_sum, L_avg = 0, 0
            origin_L, resam_L = [], []
            for sig in range(training):
                L = users_data[u][sig].shape[0]
                L_sum += L
                origin_L.append(np.arange(0, L))

            avg_L = int(L_sum / training)
            for sig in range(training):
                L = origin_L[sig][-1]
                resam_L.append(np.arange(0, L, L / avg_L)[0: avg_L])

            original_L.append(origin_L)
            resample_L.append(resam_L)

        new_users_data = []
        for u in range(users_num):
            new_data = []
            for sig in range(training):
                new_sig = []
                for feat in range(features_num):
                    interp = np.interp(
                        resample_L[u][sig], original_L[u][sig], users_data[u][sig][:, feat])
                    new_sig.append(interp)

                new_data.append(np.array(new_sig).T)

            new_users_data.append(new_data)

    # calculate the EB-DBA
    with my_timer("calculating EB-DBA..."):
        # calculate the Euclidean Barycenter between training data.
        EB_data = []
        for u in range(users_num):
            sum_sig = np.zeros(new_users_data[u][0].shape)
            for sig in range(training):
                sum_sig += new_users_data[u][sig]

            EB_data.append(sum_sig / training)

        # calculate the EB-DBA signature by EB
        EB_DBA_data = EB_data.copy()
        for u in range(users_num):
            for t in range(times):
                L = EB_data[u].shape[0]
                assoc_set = [[] for l in range(L)]
                for sig in range(training):
                    W, path = DTW(users_data[u][sig],
                                  EB_DBA_data[u], with_path=True)

                    for n, l in path:
                        # n, l = path[p]
                        assoc_set[l].append(users_data[u][sig][n])

                DBA = np.zeros((L, features_num))
                for l in range(L):
                    DBA[l] = (np.mean(assoc_set[l], axis=0))
                EB_DBA_data[u] = DBA

    for u in range(users_num):
        for sig in range(training):
            plt.plot(users_data[u][sig][:, 0], users_data[u][sig][:, 1], "--")
        plt.plot(EB_DBA_data[u][:, 0], EB_DBA_data[u][:, 1], "black", linewidth=3)
        plt.show()

    # calculate DTW with the EB-DBA signature
    with my_timer("calculating DTW..."):
        DTW_all = np.zeros((users_num, sig_num))
        for u in range(users_num):
            for sig in range(training, sig_num):
                DTW_all[u, sig] = DTW(users_data[u][sig], EB_DBA_data[u])

    # calculate FAR, FRR, EER
    with my_timer("calculating EER... "):
        ERR = user_dependent_ROC(users_num, training,
                                 genuine, forged, DTW_all)
        ERR = user_independent_ROC(users_num, training,
                                   genuine, forged, DTW_all, "EB-DBA based single template")


if __name__ == "__main__":
    user_no = random.randint(1, 41)
    sig_num = 40

    # plot_signatures(read_SVC2004, user_no, sig_num)

    # plot_signatures_features(read_SVC2004, user_no, sig_num)

    # pcolormesh_DTW(read_MMSIG, 26, 40, True)

    users_num = 5
    training = 5
    genuine = 20
    forged = 20
    times = 5
    EB_DBA_based_classify(read_SVC2004, users_num,
                          training, genuine, forged, times)


    pass
