import time
import random
import util
import pandas as pd
from feat_ext import read_SVC2004, read_SVC2004_2, read_MMSIG, read_my_sig, read_dict
from algo.single_tpl import single_tpl_min_based_classify
from algo.multi_tpl import mul_tpl_mean_based_classify
from algo.eb_dba import EB_DBA_based_classify
from algo.ls_dba import LS_DBA_based_classify


if __name__ == "__main__":
    user_no = random.randint(1, 41)
    sig_num = 40

    util.plot_signatures(read_SVC2004, user_no, sig_num)

    # util.scatter_signatures(read_MMSIG, 1, sig_num)

    # util.plot_signatures_features(read_MMSIG, 1, sig_num)

    # util.plot_signatures_features(read_my_sig, 2, 1, inverse_axis=True)

    # util.heatmap_DTW(read_SVC2004_2, 1, 40, True)

    # data = read_my_sig(2, 3)
    # util.plot_signature(data)
    # util.plot_signature_3D(data)
    # util.scatter_signature_3D(data)
    # util.plot_signature_in_timestamp(data)

    # util.plot_signatures_3D(read_my_sig, 1, 5)

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
    # single_tpl_min_based_classify(
    #     read_my_sig, 1, training, 10, 3, penalty)

    # mul_tpl_mean_based_classify(
    #     read_SVC2004, users_num, training, genuine, forged, penalty)
    # mul_tpl_mean_based_classify(
    #     read_SVC2004_2, users_num, training, genuine, forged, penalty)
    # mul_tpl_mean_based_classify(
    #     read_MMSIG, 50, training, genuine, forged, penalty)
    # mul_tpl_mean_based_classify(
    #     read_my_sig, 1, training, 10, 3, penalty)

    # EB_DBA_based_classify(read_SVC2004, users_num,
    #                       training, genuine, forged, times, penalty)
    # EB_DBA_based_classify(read_SVC2004_2, users_num,
    #                         training, genuine, forged, times, penalty)
    # EB_DBA_based_classify(read_MMSIG, 50,
    #                       training, genuine, forged, times, penalty)
    # EB_DBA_based_classify(
    #     read_my_sig, 1, training, 10, 3, penalty)

    # LS_DBA_based_classify(read_SVC2004, users_num,
    #                       training, genuine, forged, times, penalty)
    # LS_DBA_based_classify(read_SVC2004_2, users_num,
    #                       training, genuine, forged, times, penalty)
    # LS_DBA_based_classify(read_MMSIG, 50, training,
    #                       genuine, forged, times, penalty)
    # LS_DBA_based_classify(
    #     read_my_sig, 1, training, 10, 3, penalty)
