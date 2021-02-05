import numpy as np
import pandas as pd


def DTW(lhs: np.ndarray, rhs: np.ndarray, penalty=0, with_path=False, local_stability=None):
    """
    dependent dynamic timing warping
        lhs and rhs should have same number of features.
    """
    lhs, rhs = lhs.T, rhs.T
    features_num, N = lhs.shape
    _, M = rhs.shape

    if(features_num != _):
        raise Exception("features num not equals!")

    # distance calculate
    d = np.zeros((N, M))
    for i in range(features_num):
        lhs_feat = lhs[i, :].reshape(N, 1)
        rhs_feat = rhs[i, :]
        res = lhs_feat - rhs_feat  # numpy boardcast trick
        res = res ** 2
        # res = np.sqrt(res)
        d += res

    # d = np.sqrt(d)

    # local stability
    if local_stability is not None:
        d = d * local_stability

    # DTW core (dynamic program)
    D = d

    for i in range(1, N):
        D[i, 0] += D[i - 1, 0]

    for j in range(1, M):
        D[0, j] += D[0, j - 1]

    for i in range(1, N):
        for j in range(1, M):
            D[i, j] += min(D[i - 1, j] + penalty,
                           D[i, j - 1] + penalty,
                           D[i - 1, j - 1])

    avg_L = np.sqrt(M * N)
    # result = D[N - 1, M - 1] / avg_L
    result = D[N - 1, M - 1]

    if with_path == False:
        return result

    # return the DTW path
    path = []
    i, j = N - 1, M - 1
    path.append((i, j))
    while i > 0 or j > 0:
        idx = np.argmin([
            D[i - 1, j] + penalty,
            D[i, j - 1] + penalty,
            D[i - 1, j - 1]])
        if idx == 0:
            i = i - 1
        elif idx == 1:
            j = j - 1
        else:
            i, j = i - 1, j - 1
        path.append((i, j))

    path = path[:: -1]

    return result, path
