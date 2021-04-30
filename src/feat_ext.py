import numpy as np
import scipy.stats as stats
import pandas as pd
from scipy.ndimage import gaussian_filter


def __normolization_centroid(a: pd.Series, index: list):
    if a.name in index:
        minimum = a.min()
        maximum = a.max()
        centroid = (maximum - minimum) / 2

        a = (a - centroid) / (maximum - minimum)

    return a


def __normolization_min_max(a: pd.Series, index: list):
    if a.name in index:
        minimum = a.min()
        maximum = a.max()

        a = (a - minimum) / (maximum - minimum)

    return a


def __derivation(seq) -> np.ndarray:
    """
        second order regression
        seq: x, y coordinates sequence
    """
    N = len(seq)

    d_seq = np.zeros((N))

    d_seq[0] = (2*seq[2] + seq[1] - 3*seq[0]) / 5
    d_seq[1] = (2*seq[3] + seq[2] - 2*seq[1] - seq[0]) / 6
    for i in range(2, N - 2):
        d_seq[i] = (2*seq[i+2] + seq[i+1] - seq[i-1] - 2*seq[i-2]) / 10
    d_seq[N - 2] = (seq[N-1] + 2*seq[N-2] - 2*seq[N-3] - seq[N-4]) / 6
    d_seq[N - 1] = (3*seq[N-1] - seq[N-2] - 2*seq[N-3]) / 5

    return d_seq


def __guassion_filter(data: pd.DataFrame, sigma=1):
    x = gaussian_filter(data["x"], sigma=sigma)
    y = gaussian_filter(data["y"], sigma=sigma)
    return pd.DataFrame({'x': x, 'y': y})


def __guassion_filter_3D(data: pd.DataFrame, sigma=1):
    x = gaussian_filter(data["x"], sigma=sigma)
    y = gaussian_filter(data["y"], sigma=sigma)
    z = gaussian_filter(data["z"], sigma=sigma)
    return pd.DataFrame({'x': x, 'y': y, 'z': z})


def feature_extraction(data: pd.DataFrame) -> pd.DataFrame:
    # data = data.apply(stats.zscore)
    # data = data.apply(__normolization_centroid, index=['x', 'y'])
    data = data.apply(__normolization_min_max, index=['x', 'y'])

    d_x = __derivation(data["x"])
    d_y = __derivation(data["y"])

    vel = np.sqrt(d_x*d_x + d_y*d_y)  # velocity

    N = len(d_x)
    angel = np.zeros((N))  # angel
    for i in range(N):
        if d_x[i] != 0:
            angel[i] = np.arctan(d_y[i] / d_x[i])
        elif d_x[i] == 0 and d_y[i] > 0:
            angel[i] = np.pi / 2
        elif d_x[i] == 0 and d_y[i] < 0:
            angel[i] = -np.pi / 2
        else:
            angel[i] = 0

    d_vel = __derivation(vel)
    d_angle = __derivation(angel)

    # log curvature radius
    # logcr = np.log((np.abs(vel) + 0.01) / (np.abs(d_angle) + 0.01))
    logcr = np.log((np.abs(vel) + 0.001) / (np.abs(d_angle) + 0.001))
    # total acceleration magnitude
    tam = np.sqrt((d_vel*d_vel) + (vel*vel*d_angle*d_angle))

    data = pd.concat([data, pd.DataFrame(
        {"vel": vel, "angel": angel, "logcr": logcr, "tam": tam})], axis=1)

    # data = data.apply(stats.zscore)
    # data = data.apply(__normolization_centroid, index=['x', 'y'])
    # data = data.apply(__normolization_min_max, index=['x', 'y'])

    return data


def feature_extraction_3D(data: pd.DataFrame) -> pd.DataFrame:
    # data = data.apply(stats.zscore)
    # data = data.apply(__normolization_centroid, index=['x', 'y', 'z'])
    data = data.apply(__normolization_min_max, index=['x', 'y', 'z'])

    d_x = __derivation(data["x"])
    d_y = __derivation(data["y"])
    d_z = __derivation(data["z"])

    vel = np.sqrt(d_x*d_x + d_y*d_y + d_z*d_z)  # velocity

    N = len(d_x)
    angel = np.zeros((N))  # angel
    for i in range(N):
        if d_x[i] != 0:
            angel[i] = np.arctan(d_y[i] / d_x[i])
        elif d_x[i] == 0 and d_y[i] > 0:
            angel[i] = np.pi / 2
        elif d_x[i] == 0 and d_y[i] < 0:
            angel[i] = -np.pi / 2
        else:
            angel[i] = 0

    d_vel = __derivation(vel)
    d_angle = __derivation(angel)

    # log curvature radius
    # logcr = np.log((np.abs(vel) + 0.01) / (np.abs(d_angle) + 0.01))
    logcr = np.log((np.abs(vel) + 0.001) / (np.abs(d_angle) + 0.001))
    # total acceleration magnitude
    tam = np.sqrt((d_vel*d_vel) + (vel*vel*d_angle*d_angle))

    data = pd.concat([data, pd.DataFrame(
        {"vel": vel, "angel": angel, "logcr": logcr, "tam": tam})], axis=1)


    return data


def read_MMSIG(user_no: int, index: int) -> pd.DataFrame:
    if user_no < 10:
        filename = f"../data/SCUT-MMSIG-database/inair/U0{user_no}S{index}.txt"
    else:
        filename = f"../data/SCUT-MMSIG-database/inair/U{user_no}S{index}.txt"

    data = pd.read_table(filename, sep=" ", dtype="int",
                         header=None, names=["x", "y"])

    # feature extraction & data preprocess
    # data = __guassion_filter(data, sigma=1)
    data = feature_extraction(data)

    return data


def read_SVC2004(user_no: int, index: int) -> pd.DataFrame:
    filename = f"../data/SVC2004/U{user_no}S{index}.TXT"

    data = pd.read_table(filename, sep=" ", skiprows=1,
                         dtype="int", header=None, names=["x", "y", "ts", "pen"])
    data = data.drop(columns=["ts", "pen"])

    # feature extraction & data preprocess
    # data = __guassion_filter(data, sigma=1)
    data = feature_extraction(data)

    # return data
    return data


def read_SVC2004_2(user_no: int, index: int) -> pd.DataFrame:
    filename = f"../data/SVC2004-2/U{user_no}S{index}.TXT"

    data = pd.read_table(filename, sep=" ", skiprows=1,
                         dtype="int", header=None, names=["x", "y", "ts", "pen", "Az", "Al", "Pr"])
    data = data.drop(columns=["ts", "pen", "Az", "Al", "Pr"])

    # feature extraction & data preprocess
    # data = __guassion_filter(data, sigma=1)
    data = feature_extraction(data)

    # return data
    return data


def read_my_sig(user_no: int, index: int):
    filename = f"../data/my-sig/U{user_no}S{index}.json"
    data = pd.read_json(filename, dtype="float64")

    # feature extraction & data preprocess
    data = __guassion_filter_3D(data, sigma=1)
    data = feature_extraction_3D(data)
    return data


def read_dict(json: dict) -> pd.DataFrame:
    data = pd.DataFrame(json, dtype="float64")

    # feature extraction & data preprocess
    data = __guassion_filter_3D(data, sigma=1)
    data = feature_extraction_3D(data)

    return data
