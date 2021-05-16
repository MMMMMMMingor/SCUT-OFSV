import numpy as np
import util
import roc
import random
import matplotlib.pyplot as plt
import algo.core.dtw as dtw
import algo.core.template as tpl


def EB_DBA_based_classify(read_fun, users_num: int, training: int, genuine: int, forged: int, times: int, penalty=0):
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

    # shuffle genuine signatures
    for u in range(users_num):
        genuine_sig = users_data[u][:genuine]
        random.shuffle(genuine_sig)
        users_data[u] = genuine_sig + users_data[u][genuine:]

    # calculate the eb-dba
    with util.my_timer("calculating EB-DBA..."):
        eb_dba_tpls = []
        for u in range(users_num):
            eb_dba_tpl = tpl.get_eb_dba_tpl(
                users_data[u][0:training], times, penalty)
            eb_dba_tpls.append(eb_dba_tpl)

    # for u in range(users_num):
    #     # util.plot_mean_template_with_train(eb_dba_tpls[u], users_data[u][:training])
    #     util.plot_mean_template_with_train_3D(eb_dba_tpls[u], users_data[u][:training])

    # testing with the EB-DBA signature
    with util.my_timer("testing..."):
        DTW_test = np.zeros((users_num, sig_sum))
        for u in range(users_num):
            for sig in range(training, sig_sum):
                DTW_test[u, sig] = dtw.DTW(
                    users_data[u][sig], eb_dba_tpls[u], penalty=penalty)

    with util.my_timer("calculate threshold..."):
        threshold_array = []
        for u in range(users_num):
            threshold_array.append(util.get_eb_dba_tpl_threshold(eb_dba_tpls[u], users_data[u]))

    # calculate FAR, FRR, EER
    with util.my_timer("calculating EER... "):
        ERR = roc.user_dependent_ROC(users_num, training,
                                     genuine, forged, DTW_test)
        FAR, FRR = roc.user_thres_dependent_ROC(users_num, training,
                                                genuine, forged, DTW_test, threshold_array)
        ERR = roc.user_independent_ROC(users_num, training,
                                       genuine, forged, DTW_test, "EB-DBA based single template")
