import numpy as np
import util
import roc
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

    # calculate the eb-dba
    with util.my_timer("calculating EB-DBA..."):
        eb_dba_tpls = []
        for u in range(users_num):
            eb_dba_tpl = tpl.get_eb_dba_tpl(
                users_data[u][0:training], times, penalty)
            eb_dba_tpls.append(eb_dba_tpl)

    # for u in range(users_num):
    #     for sig in range(training):
    #         plt.plot(users_data[u][sig][:, 0], users_data[u][sig][:, 1], "--")
    #     plt.plot(eb_dba_tpls[u][:, 0], eb_dba_tpls[u]
    #              [:, 1], "black", linewidth=3)
    #     plt.show()

    # testing with the EB-DBA signature
    with util.my_timer("testing..."):
        DTW_test = np.zeros((users_num, sig_sum))
        for u in range(users_num):
            for sig in range(training, sig_sum):
                DTW_test[u, sig] = dtw.DTW(
                    users_data[u][sig], eb_dba_tpls[u], penalty=penalty)

    # calculate FAR, FRR, EER
    with util.my_timer("calculating EER... "):
        ERR = roc.user_dependent_ROC(users_num, training,
                                     genuine, forged, DTW_test)
        ERR = roc.user_independent_ROC(users_num, training,
                                       genuine, forged, DTW_test, "EB-DBA based single template")
