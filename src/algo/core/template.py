import numpy as np
import algo.core.dtw as dtw
import matplotlib.pyplot as plt


# min-based single template strategy
def get_single_min_tpl(training_data: list, penalty=0) -> np.ndarray:
    train_num = len(training_data)
    DTW_between = np.zeros((train_num, train_num))
    for sig in range(train_num):
        for other_sig in range(sig + 1, train_num):
            DTW_between[sig, other_sig] = dtw.DTW(training_data[sig],
                                                  training_data[other_sig],
                                                  penalty=penalty)

    # 利用对称矩阵特性，节省DTW计算量
    DTW_between = DTW_between + DTW_between.T

    min_idx = np.argmin(np.sum(DTW_between, axis=0))

    return training_data[min_idx]


# mean-based multipul template strategy
def get_multi_mean_dtw(training_data: list, test_data: list, penalty=0) -> float:
    train_num = len(training_data)

    DTW_result = np.zeros((train_num))
    for other_sig in range(train_num):
        DTW_result[other_sig] = dtw.DTW(test_data,
                                        training_data[other_sig],
                                        penalty=penalty)

    return np.mean(DTW_result)


# EB-DBA single template stratgy
def get_eb_dba_tpl(training_data: list, times: int, penalty=0) -> np.ndarray:
    train_num = len(training_data)

    # linerear interpolation
    features_num = training_data[0].shape[-1]
    original_point = []
    resample_point = []
    L_sum = 0

    for sig in range(train_num):
        L = training_data[sig].shape[0]
        L_sum += L
        original_point.append(np.arange(0, L))

    avg_L = int(L_sum / train_num)
    for sig in range(train_num):
        L = original_point[sig][-1]
        resample_point.append(np.arange(0, L, L / avg_L)[0: avg_L])

    new_training_data = []
    for sig in range(train_num):
        new_sig = []
        for feat in range(features_num):
            interp = np.interp(
                resample_point[sig], original_point[sig], training_data[sig][:, feat])
            new_sig.append(interp)

        new_training_data.append(np.array(new_sig).T)

    # calculate the Euclidean Barycenter between training data.
    sum_sig = np.zeros(new_training_data[0].shape)
    for sig in range(train_num):
        sum_sig += new_training_data[sig]

    eb_dba_tpl = sum_sig / train_num

    # calculate the EB-DBA signature by iterator
    for t in range(times):
        L = eb_dba_tpl.shape[0]
        assoc_set = [[] for l in range(L)]
        for sig in range(train_num):
            W, path = dtw.DTW_with_path(training_data[sig],
                                        eb_dba_tpl, penalty=penalty)

            for n, l in path:
                assoc_set[l].append(training_data[sig][n])

        for l in range(L):
            eb_dba_tpl[l] = np.mean(assoc_set[l], axis=0)

    return eb_dba_tpl


# EB-DBA single template stratgy
def get_ls_dba_tpl(training_data: list, times: int, penalty=0) -> np.ndarray:
    train_num = len(training_data)

    # linerear interpolation
    features_num = training_data[0].shape[-1]
    original_point = []
    resample_point = []
    L_sum = 0

    for sig in range(train_num):
        L = training_data[sig].shape[0]
        L_sum += L
        original_point.append(np.arange(0, L))

    avg_L = int(L_sum / train_num)
    for sig in range(train_num):
        L = original_point[sig][-1]
        resample_point.append(np.arange(0, L, L / avg_L)[0: avg_L])

    new_training_data = []
    for sig in range(train_num):
        new_sig = []
        for feat in range(features_num):
            interp = np.interp(
                resample_point[sig], original_point[sig], training_data[sig][:, feat])
            new_sig.append(interp)

        new_training_data.append(np.array(new_sig).T)

    # calculate the Euclidean Barycenter between training data.
    sum_sig = np.zeros(new_training_data[0].shape)
    for sig in range(train_num):
        sum_sig += new_training_data[sig]

    eb_dba_tpl = sum_sig / train_num

    # calculate the EB-DBA signature by EB
    paths = []
    for t in range(times):
        L = eb_dba_tpl.shape[0]
        assoc_set = [[] for l in range(L)]
        for sig in range(train_num):
            W, path = dtw.DTW_with_path(training_data[sig],
                                        eb_dba_tpl, penalty=penalty)
            paths.insert(sig, path)
            for n, l in path:
                assoc_set[l].append(training_data[sig][n])

        for l in range(L):
            eb_dba_tpl[l] = np.mean(assoc_set[l], axis=0)

    # calculate local-stability
    mmps = np.zeros((train_num, avg_L), dtype="int")
    for sig in range(train_num):
        mmp = np.zeros(avg_L, dtype="int")
        for n, l in paths[sig]:
            mmp[l] += 1

        mmps[sig] = mmp

    ls = 1 / np.mean(mmps, axis=0)
    ls = (ls.reshape(1, avg_L))

    return eb_dba_tpl, ls
