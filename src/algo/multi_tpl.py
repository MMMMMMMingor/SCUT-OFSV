import numpy as np
import util
import roc
import dtw


def mul_tpl_mean_based_classify(read_fun, users_num: int, training: int, genuine: int, forged: int, penalty):
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

    # calculate DTW for test
    with util.my_timer("testing... "):
        DTW_all = np.zeros((users_num, sig_num, training))
        for u in range(users_num):
            for sig in range(training, sig_num):
                for other_sig in range(training):
                    DTW_all[u, sig, other_sig] = dtw.DTW(users_data[u][sig],
                                                         users_data[u][other_sig],
                                                         penalty=penalty)

        DTW_mean = np.zeros((users_num, sig_num))
        for u in range(users_num):
            for sig in range(training, sig_num):
                DTW_mean[u, sig] = np.mean(DTW_all[u, sig])

    # calculate FAR, FRR, EER
    with util.my_timer("calculating EER... "):
        ERR = roc.user_dependent_ROC(users_num, training,
                                 genuine, forged, DTW_mean)
        ERR = roc.user_independent_ROC(users_num, training,
                                   genuine, forged, DTW_mean, "mean-based multiple template")
