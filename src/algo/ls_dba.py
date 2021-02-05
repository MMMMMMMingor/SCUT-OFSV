import numpy as np
import util
import roc
import matplotlib.pyplot as plt
import dtw


def LS_DBA_based_classify(read_fun, users_num: int, training: int, genuine: int, forged: int, times: int, penalty=0):
    if training <= 0 or genuine < training or forged < 0:
        raise Exception("args has error")

    sig_num = genuine + forged
    avg_L = []  # average length
    Paths = []  # DTW paths

    # loading signature
    with util.my_timer("loading signature... "):
        users_data = []
        for u in range(users_num):
            sig_arr = [read_fun(u + 1, sig + 1).to_numpy()
                       for sig in range(sig_num)]
            users_data.append(sig_arr)

    # linerear interpolation
    with util.my_timer("linerear interpolation... "):
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

            avg_l = int(L_sum / training)
            for sig in range(training):
                L = origin_L[sig][-1]

                # 防止长度大于avg_l
                resam_L.append(np.arange(0, L, L / avg_l)[0: avg_l])

            original_L.append(origin_L)
            resample_L.append(resam_L)
            avg_L.append(avg_l)

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
    with util.my_timer("calculating EB-DBA..."):
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
            paths = []
            for t in range(times):
                L = EB_data[u].shape[0]
                assoc_set = [[] for l in range(L)]
                for sig in range(training):
                    W, path = dtw.DTW(users_data[u][sig],
                                      EB_DBA_data[u], with_path=True, penalty=penalty)
                    paths.insert(sig, path)
                    for n, l in path:
                        assoc_set[l].append(users_data[u][sig][n])

                DBA = np.zeros((L, features_num))
                for l in range(L):
                    DBA[l] = (np.mean(assoc_set[l], axis=0))
                EB_DBA_data[u] = DBA

            Paths.insert(u, paths)

    # for u in range(users_num):
    #     for sig in range(training):
    #         plt.plot(users_data[u][sig][:, 0], users_data[u][sig][:, 1], "--")
    #     plt.plot(EB_DBA_data[u][:, 0], EB_DBA_data[u]
    #              [:, 1], "black", linewidth=3)
    #     plt.show()

    # calculate local-stability
    with util.my_timer("calculating local-stability..."):
        LS = []
        for u in range(users_num):
            mmps = np.zeros((training, avg_L[u]), dtype="int")
            for sig in range(training):
                mmp = np.zeros(avg_L[u], dtype="int")
                for n, l in Paths[u][sig]:
                    mmp[l] += 1

                mmps[sig] = mmp

            ls = 1 / np.mean(mmps, axis=0)
            # if u == 16:
            #     plt.plot(ls)
            #     plt.show()
            LS.append(ls.reshape(1, avg_L[u]))

    # calculate DTW with the EB-DBA signature
    with util.my_timer("testing..."):
        DTW_all = np.zeros((users_num, sig_num))
        for u in range(users_num):
            for sig in range(training, sig_num):
                DTW_all[u, sig] = dtw.DTW(
                    users_data[u][sig], EB_DBA_data[u], penalty=penalty, local_stability=LS[u])

    # calculate FAR, FRR, EER
    with util.my_timer("calculating EER... "):
        ERR = roc.user_dependent_ROC(users_num, training,
                                     genuine, forged, DTW_all)
        ERR = roc.user_independent_ROC(users_num, training,
                                       genuine, forged, DTW_all, "LS-DBA based single template")
