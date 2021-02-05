import time
import random
import comm_plot
from feat_ext import read_SVC2004, read_SVC2004_2, read_MMSIG
from algo.single_tpl import single_tpl_min_based_classify
from algo.multi_tpl import mul_tpl_mean_based_classify
from algo.eb_dba import EB_DBA_based_classify
from algo.ls_dba import LS_DBA_based_classify


if __name__ == "__main__":
    user_no = random.randint(1, 41)
    sig_num = 40

    # comm_plot.plot_signatures(read_SVC2004_2, 1, sig_num)

    # comm_plot.plot_signatures_features(read_SVC2004_2, 17, 1)

    # comm_plot.heatmap_DTW(read_SVC2004_2, 1, 40, True)

    users_num = 40
    training = 5
    genuine = 20
    forged = 20
    penalty = 1
    times = 5

    # single_tpl_min_based_classify(
    #     read_SVC2004, users_num, training, genuine, forged, penalty)
    # single_tpl_min_based_classify(
    #     read_SVC2004_2, users_num, training, genuine, forged, penalty)
    # single_tpl_min_based_classify(
    #     read_MMSIG, 50, training, genuine, forged, penalty)

    # mul_tpl_mean_based_classify(
    #     read_SVC2004, users_num, training, genuine, forged, penalty)
    # mul_tpl_mean_based_classify(
    #     read_SVC2004_2, users_num, training, genuine, forged, penalty)
    # mul_tpl_mean_based_classify(
    #     read_MMSIG, 50, training, genuine, forged, penalty)

    # EB_DBA_based_classify(read_SVC2004, users_num,
    #                       training, genuine, forged, times, penalty)
    # EB_DBA_based_classify(read_SVC2004_2, users_num,
    #                         training, genuine, forged, times, penalty)
    # EB_DBA_based_classify(read_MMSIG, 50,
    #                       training, genuine, forged, times, penalty)

    # LS_DBA_based_classify(read_SVC2004, users_num,
    #                       training, genuine, forged, times, penalty)
    # LS_DBA_based_classify(read_SVC2004_2, users_num,
    #                       training, genuine, forged, times, penalty)
    # LS_DBA_based_classify(read_MMSIG, 50, training,
    #                       genuine, forged, times, penalty)
