import numpy as np
import matplotlib.pyplot as plt
import util


def user_independent_ROC(users_num: int, training: int, genuine: int, forged: int, DTW_test: np.ndarray, title="") -> float:
    # threshold_array = np.arange(0, 10, 0.01, dtype="float")
    threshold_array = np.arange(0, 4000, 1, dtype="float")
    FA = np.zeros(len(threshold_array), dtype="int")
    FR = np.zeros(len(threshold_array), dtype="int")

    for index, thre in enumerate(threshold_array):
        for u in range(users_num):
            for sig in range(training, genuine):
                if DTW_test[u, sig] > thre:
                    FR[index] = FR[index] + 1

            for sig in range(genuine, genuine + forged):
                if DTW_test[u, sig] < thre:
                    FA[index] = FA[index] + 1

    # calculate cross point (EER)
    genuine_count = users_num * (genuine - training)
    forged_count = users_num * forged
    FAR = FA / forged_count
    FRR = FR / genuine_count

    idx = np.argwhere(np.diff(np.sign(FAR - FRR))).reshape(-1)
    if len(idx) == 0:
        raise Exception("no cross point")
    idxl = idx[0]
    idxr = idx[-1]
    EER = ((FRR[idxr] + FAR[idxl]) / 2)

    plt.plot(FRR, FAR, label="ROC")
    plt.plot(FRR[idxl], EER, 'ro',
             label=f"EER: {round(EER*100, 2)}%")
    plt.title(title)
    plt.xlabel("False Reject Rate")
    plt.ylabel("False Acept Rate")
    plt.legend()
    # plt.show()

    print("user-independent threshold", threshold_array[idx])
    print(
        f"{util.OKGREEN} user-independent EER: {EER} {util.ENDC}")
    return EER


def user_thres_dependent_ROC(users_num: int, training: int, genuine: int, forged: int, DTW_test: np.ndarray, threshold_array: list) -> (float, float):
    FA = 0
    FR = 0

    for u in range(users_num):
        for sig in range(training, genuine):
            if DTW_test[u, sig] > threshold_array[u]:
                FR = FR + 1

        for sig in range(genuine, genuine + forged):
            if DTW_test[u, sig] < threshold_array[u]:
                FA = FA + 1

    # calculate cross point (EER)
    genuine_count = users_num * (genuine - training)
    forged_count = users_num * forged
    FAR = FA / forged_count
    FRR = FR / genuine_count

    print("user-thres-dependent threshold", threshold_array)
    print(f"{util.OKGREEN} user-thres-dependent FAR: {FAR}, FRR: {FRR} {util.ENDC}")
    return FAR, FRR


def user_dependent_ROC(users_num: int, training: int, genuine: int, forged: int, DTW_test: np.ndarray) -> float:
    # threshold_array = np.arange(0, 10, 0.01, dtype="float")
    threshold_array = np.arange(0, 4000, 1, dtype="float")
    l = len(threshold_array)
    EER = np.zeros(users_num, dtype="float")
    EER_idx = np.zeros(users_num, dtype="float")

    # print(DTW_test)

    for u in range(users_num):
        FA = np.zeros(l, dtype="int")
        FR = np.zeros(l, dtype="int")
        for index, thre in enumerate(threshold_array):
            for sig in range(training, genuine):
                if DTW_test[u, sig] > thre:
                    FR[index] = FR[index] + 1

            for sig in range(genuine, genuine + forged):
                if DTW_test[u, sig] < thre:
                    FA[index] = FA[index] + 1

        # calculate cross point EER)
        FAR = FA / forged
        FRR = FR / (genuine - training)

        idx = np.argwhere(np.diff(np.sign(FAR - FRR))).reshape(-1)
        if len(idx) == 0:
            raise Exception(f"no cross point, user_no: {u + 1}")

        idxl = idx[0]
        idxr = idx[-1]
        EER_idx[u] = threshold_array[idxl]
        EER[u] = (FRR[idxr] + FAR[idxl]) / 2

    # calculate mean (EER)
    EER = np.mean(EER)

    print("user-dependent threshold", EER_idx)
    print(f"{util.OKGREEN} user-dependent EER: {EER} {util.ENDC}")
    return EER
