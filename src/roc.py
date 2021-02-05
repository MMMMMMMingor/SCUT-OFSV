import numpy as np
import matplotlib.pyplot as plt
import util


def user_independent_ROC(users_num: int, training: int, genuine: int, forged: int, DTW_matrix, title="no title") -> float:
    # threshold_array = np.arange(0, 10, 0.01, dtype="float")
    threshold_array = np.arange(0, 4000, 1, dtype="float")
    FA = np.zeros(len(threshold_array), dtype="int")
    FR = np.zeros(len(threshold_array), dtype="int")

    # print(DTW_matrix)

    for index, thre in enumerate(threshold_array):
        for u in range(users_num):
            for sig in range(training, genuine):
                if DTW_matrix[u, sig] > thre:
                    FR[index] = FR[index] + 1

            for sig in range(genuine, genuine + forged):
                if DTW_matrix[u, sig] < thre:
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
    plt.title("user independent ROC")
    plt.xlabel("False Reject Rate")
    plt.ylabel("False Acept Rate")
    plt.legend()
    plt.title(title)
    # plt.show()

    print(
        f"{util.OKGREEN} user-independent EER: {EER}, threshold: {threshold_array[idx]} {util.ENDC}")
    return EER


def user_dependent_ROC(users_num: int, training: int, genuine: int, forged: int, DTW_matrix) -> float:
    # threshold_array = np.arange(0, 10, 0.01, dtype="float")
    threshold_array = np.arange(0, 4000, 1, dtype="float")
    l = len(threshold_array)
    EER = np.zeros(users_num, dtype="float")
    EER_idx = np.zeros(users_num, dtype="float")

    for u in range(users_num):
        FA = np.zeros(l, dtype="int")
        FR = np.zeros(l, dtype="int")
        for index, thre in enumerate(threshold_array):
            for sig in range(training, genuine):
                if DTW_matrix[u, sig] > thre:
                    FR[index] = FR[index] + 1

            for sig in range(genuine, genuine + forged):
                if DTW_matrix[u, sig] < thre:
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

    print("user-dependent threshold", EER_idx)

    # calculate mean (EER)
    EER = np.mean(EER)

    print(f"{util.OKGREEN} user-dependent EER: {EER} {util.ENDC}")
    return EER
