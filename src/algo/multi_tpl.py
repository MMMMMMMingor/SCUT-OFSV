import numpy as np
import util
import roc
import algo.core.dtw as dtw
import algo.core.template as tpl


def mul_tpl_mean_based_classify(read_fun, users_num: int, training: int, genuine: int, forged: int, penalty):
    if training <= 0 or genuine < training or forged < 0:
        raise Exception("args has error")

    sig_sum = genuine + forged

    # loading signature
    with util.my_timer("loading signature... "):
        users_data = []
        for u in range(users_num):
            sig_arr = [read_fun(u + 1, sig + 1).to_numpy()
                       for sig in range(sig_sum)]
            users_data.append(sig_arr)

    # calculate DTW for test
    with util.my_timer("testing... "):
        DTW_mean_test = np.zeros((users_num, sig_sum))
        for u in range(users_num):
            for sig in range(training, sig_sum):
                mean_dtw = tpl.get_multi_mean_dtw(users_data[u][0:training], users_data[u][sig], penalty)
                DTW_mean_test[u, sig] = mean_dtw

    # calculate FAR, FRR, EER
    with util.my_timer("calculating EER... "):
        ERR = roc.user_dependent_ROC(users_num, training,
                                 genuine, forged, DTW_mean_test)
        ERR = roc.user_independent_ROC(users_num, training,
                                   genuine, forged, DTW_mean_test, "mean-based multiple template")
