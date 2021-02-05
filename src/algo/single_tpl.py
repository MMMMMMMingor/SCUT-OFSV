import numpy as np
import util
import roc
import dtw


def single_tpl_min_based_classify(read_fun, users_num: int, training: int, genuine: int, forged: int, penalty=0):
    if training <= 0 or genuine < training or forged < 0:
        raise Exception("args has error")

    sig_num = genuine + forged

    # loading signature
    with util.my_timer("loading signature... "):
        users_data = []
        for u in range(users_num):
            sig_arr = [read_fun(u + 1, sig + 1).to_numpy()
                       for sig in range(sig_num)]
            users_data.append(sig_arr)

    # finding the signature has minimum DTW with others
    with util.my_timer("finding the signature has minimum DTW with others..."):
        training_data = []
        for u in range(users_num):
            DTW_between = np.zeros((training, training))
            for sig in range(training):
                for other_sig in range(sig + 1, training):
                    DTW_between[sig, other_sig] = dtw.DTW(users_data[u][sig],
                                                          users_data[u][other_sig],
                                                          penalty=penalty)

            DTW_between = DTW_between + DTW_between.T

            min_idx = np.argmin(np.sum(DTW_between, axis=0))
            training_data.append(users_data[u][min_idx])

    # testing with the minimum signature
    with util.my_timer("testing..."):
        DTW_all = np.zeros((users_num, sig_num))
        for u in range(users_num):
            for sig in range(training, sig_num):
                DTW_all[u, sig] = dtw.DTW(users_data[u][sig], training_data[u])

    # calculate FAR, FRR, EER
    with util.my_timer("calculating EER... "):
        ERR = roc.user_dependent_ROC(users_num, training,
                                     genuine, forged, DTW_all)
        ERR = roc.user_independent_ROC(users_num, training,
                                       genuine, forged, DTW_all, "min-based single template")
