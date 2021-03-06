import numpy as np
import util
import roc
import random 
import algo.core.dtw as dtw
import algo.core.template as tpl


def single_tpl_min_based_classify(read_fun, users_num: int, training: int, genuine: int, forged: int, penalty=0):
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
    
    # shuffle true signatures
    for u in range(users_num):
        genuine_sig = users_data[u][:genuine]
        random.shuffle(genuine_sig)
        users_data[u] = genuine_sig + users_data[u][genuine:]

    # finding the signature has minimum DTW with others
    with util.my_timer("finding the signature has minimum DTW with others..."):
        single_tpls = []
        for u in range(users_num):
            single_tpl = tpl.get_single_min_tpl(users_data[u][0:training], penalty)
            single_tpls.append(single_tpl)

    # testing with the minimum signature
    with util.my_timer("testing..."):
        DTW_test = np.zeros((users_num, sig_sum))
        for u in range(users_num):
            for sig in range(training, sig_sum):
                DTW_test[u, sig] = dtw.DTW(users_data[u][sig], single_tpls[u])

    with util.my_timer("calculate threshold..."):
        threshold_array = []
        for u in range(users_num):
            threshold_array.append(util.get_single_min_threshold(single_tpls[u], users_data[u][0:training]))

    # calculate FAR, FRR, EER
    with util.my_timer("calculating EER... "):
        ERR = roc.user_dependent_ROC(users_num, training,
                                     genuine, forged, DTW_test)
        FAR, FRR = roc.user_thres_dependent_ROC(users_num, training,
                                                genuine, forged, DTW_test, threshold_array)
        ERR = roc.user_independent_ROC(users_num, training,
                                       genuine, forged, DTW_test, "single min based single template")
