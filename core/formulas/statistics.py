from collections import Counter
from math import sqrt, erf, pi, exp, ceil, floor
from dataclasses import dataclass
from typing import Dict, List
from scipy.integrate import quad as oIntegral


# 🗿

@dataclass
class DiscreteData:
    X: Dict[float, int]
    x_n: Dict[float, int]
    x_w: Dict[float, float]
    N: int
    x_v: float
    sigma: float
    D_v: float
    S: float


@dataclass
class ContinuousData:
    intervals: List[List[float]]
    N: List[int]
    W: List[float]
    middles: List[float]
    x_v: float
    sigma: float
    D_v: float
    S: float
    h: float

@dataclass
class DistributionData:
    X: List[int]
    P: List[float]
    M0: List[int]
    M: float
    D: float
    sigma: float


def process_discrete_data(data) -> DiscreteData:
    counter = Counter(data)
    # Частота
    x_n = {}
    for key in sorted(counter.keys()):
        x_n[key] = counter[key]
    sum_n = sum(x_n.values())
    # Относительная частота
    x_w = {}
    for key in sorted(counter.keys()):
        x_w[key] = counter[key] / sum_n
    # Среднее выборочное
    Xv = 0
    for xi in x_n:
        Xv += x_n[xi] * xi
    Xv /= sum_n
    # Выборочная дисперсия
    Dv = 0
    for xi in x_n:
        Dv += (xi - Xv) ** 2 * x_n[xi]
    Dv /= sum_n
    # Среднее квадратическое отклонение
    sigma = sqrt(Dv)
    # Исправленное среднее квадратическое отклонение
    S = 0
    for xi in x_n:
        S += (xi - Xv) ** 2 * x_n[xi]
    S /= sum_n - 1
    S = sqrt(S)
    return DiscreteData(list(x_n.keys()), x_n, x_w, sum_n, Xv, sigma, Dv, S)


# 🗿
def process_continuous_data(data, count) -> ContinuousData:
    length_of_interval = (max(data) - min(data)) / count
    xmax = max(data)
    sorted_uniq_data = list(sorted(set(data)))
    intervals = []
    middles = []
    N = []
    W = []
    # Интервалы и их середины
    left_border = min(data)
    for i in range(count):
        right_border = round(min(left_border + length_of_interval, xmax), 3)
        intervals.append([left_border, right_border])
        middles.append(round(left_border + round((right_border - left_border) / 2, 3), 3))

        # Частота для интервалов
        interval_count = 0
        for val in data:
            if i == count - 1:
                right_border += 1

            if left_border <= val < right_border:
                interval_count += 1
        N.append(interval_count)
        left_border = round(left_border + length_of_interval, 3)

    # Проверка частот для интервалов
    assert sum(N) == len(data)

    # Относительная частота для интервалов
    W = calculate_W(N)

    # Среднее выборочное
    Xv = calculate_Xv(middles, N)

    # Выборочная дисперсия
    Dv = calculate_Dv(Xv, N, middles)

    # Среднее квадратическое отклонение
    sigma = calculate_sigma(Dv)

    # Исправленное среднее квадратическое отклонение
    S = calculate_S(Xv, N, middles)

    return ContinuousData(intervals, N, W, middles, Xv, sigma, Dv, S, length_of_interval)


def calculate_W(N=[]):
    N_total = sum(N)
    W = []
    for ni in N:
        W.append(ni / N_total)

    return W

def calculate_Xv(middles=[], N=[]):
    Xv = 0
    for i, xi in enumerate(middles):
        Xv += xi * N[i]
    Xv /= sum(N)
    return Xv

def calculate_Dv(Xv, N=[], middles=[]):
    Dv = 0
    for i, xi in enumerate(middles):
        Dv += (xi - Xv) ** 2 * N[i]
    Dv /= sum(N)
    return Dv


def calculate_sigma(D):
    return sqrt(D)

def process_discrete_data(data) -> DiscreteData:
    counter = Counter(data)
    # Частота
    x_n = {}
    for key in sorted(counter.keys()):
        x_n[key] = counter[key]
    sum_n = sum(x_n.values())
    # Относительная частота
    x_w = {}
    for key in sorted(counter.keys()):
        x_w[key] = counter[key] / sum_n
    # Среднее выборочное
    Xv = 0
    for xi in x_n:
        Xv += x_n[xi] * xi
    Xv /= sum_n
    # Выборочная дисперсия
    Dv = 0
    for xi in x_n:
        Dv += (xi - Xv) ** 2 * x_n[xi]
    Dv /= sum_n
    # Среднее квадратическое отклонение
    sigma = sqrt(Dv)
    # Исправленное среднее квадратическое отклонение
    S = 0
    for xi in x_n:
        S += (xi - Xv) ** 2 * x_n[xi]
    S /= sum_n - 1
    S = sqrt(S)
    return DiscreteData(list(x_n.keys()), x_n, x_w, sum_n, Xv, sigma, Dv, S)

def calculate_S(Xv, N=[], middles=[]):
    S_square = 0
    for i, xi in enumerate(middles):
        S_square += (xi - Xv) ** 2 * N[i]
    S_square /= sum(N) - 1
    return sqrt(S_square)


def process_continuous_intervals(data_split_by_intervals: ContinuousData) -> ContinuousData:
    for i in data_split_by_intervals.intervals:
        mid = (i[1] - i[0]) / 2 + i[0]
        data_split_by_intervals.middles.append(mid)

    #   Относительные частоты
    data_split_by_intervals.W = calculate_W(data_split_by_intervals.N)

    # Среднее выборочное
    Xv = calculate_Xv(data_split_by_intervals.middles, data_split_by_intervals.N)

    # Выборочная дисперсия
    Dv = calculate_Dv(Xv, data_split_by_intervals.N, data_split_by_intervals.middles)

    # Среднее квадратическое отклонение
    sigma = calculate_sigma(Dv)

    # Исправленное среднее квадратическое отклонение
    S = calculate_S(Xv, data_split_by_intervals.N, data_split_by_intervals.middles)

    length_of_interval = data_split_by_intervals.intervals[0][1] - data_split_by_intervals.intervals[0][0]

    return ContinuousData(
        data_split_by_intervals.intervals,
        data_split_by_intervals.N,
        data_split_by_intervals.W,
        data_split_by_intervals.middles,
        Xv,
        sigma,
        Dv,
        S,
        length_of_interval,
    )

def process_distribution_data(currentData: DistributionData) -> DistributionData:

    # Мат ожидание
    M = calculate_Xv(currentData.X, currentData.P)

    # Выборочная дисперсия
    D = calculate_dispersion(M, currentData.X, currentData.P)

    # Среднее квадратическое отклонение
    sigma = calculate_sigma(D)

    # Мода
    M0 = find_M0(currentData.X, currentData.P)

    return DistributionData(
        currentData.X,
        currentData.P,
        M0,
        M,
        D,
        sigma,
    )

def calculate_dispersion(M, X = [], P = []):
    X_square = []

    for x in X:
        X_square.append(x**2)

    M_square_x = calculate_Xv(X, P)

    return (M_square_x - M**2)

def find_M0(X = [], P = []) -> []:
    M0 = []
    max_value = max(P);

    for x in X:
        if x == max_value:
            M0.append(x)

    return M0


def process_continuous_plot_data(data: ContinuousData):
    plot_data = {}
    k = len(data.intervals)
    f = {'lines': [], 'dotsx': [], 'dotsy': []}
    func = '0,\tпри x <= ' + str(round(data.intervals[0][1], 3)) + '\n'

    intlen = 3 * (data.intervals[0][1] - data.intervals[0][0])
    line = [[data.intervals[0][1] - intlen, data.intervals[0][1]], [0, 0]]
    f['lines'].append(line)

    counter = data.W[0]
    for i in range(1, k):
        newstr = ''
        newstr += (
                str(round(counter, 2))
                + ',\tпри '
                + str(round(data.intervals[i - 1][1], 3))
                + ' < x <= '
                + str(round(data.intervals[i][1], 3))
        )
        line = [
            [data.intervals[i][1], data.intervals[i][0]],
            [counter, counter],
        ]
        f['lines'].append(line)

        f['dotsx'].append(data.intervals[i - 1][1])
        f['dotsy'].append(counter)

        counter += data.W[i]
        func += newstr + '\n'
    func += '1,\tпри x > ' + str(round(data.intervals[k - 1][1], 3))

    line = [
        [data.intervals[k - 1][1], data.intervals[k - 1][1] + intlen],
        [counter, counter],
    ]
    f['lines'].append(line)

    f['dotsx'].append(data.intervals[k - 1][1])
    f['dotsy'].append(counter)

    plot_data['F*'] = func
    plot_data['func'] = f

    return plot_data


def process_discrete_plot_data(discrete_data: DiscreteData):
    # Эмпирическая функция
    f = {'lines': [], 'dotsx': [], 'dotsy': []}
    plot_data = {}
    k = len(discrete_data.X)

    func = '0,\tпри x < ' + str(discrete_data.X[0]) + '\n'

    intlen = 3 * (discrete_data.X[1] - discrete_data.X[0])
    line = [[discrete_data.X[0] - intlen, discrete_data.X[0]], [0, 0]]
    f['lines'].append(line)

    counter = list(discrete_data.x_w.values())[0]
    for i in range(1, k):
        newstr = ''
        newstr += (
                str(round(counter, 2))
                + ',\tпри '
                + str(discrete_data.X[i - 1])
                + ' <= x < '
                + str(discrete_data.X[i])
        )

        line = [
            [discrete_data.X[i - 1], discrete_data.X[i]],
            [counter, counter],
        ]
        f['lines'].append(line)

        f['dotsx'].append(discrete_data.X[i - 1])
        f['dotsy'].append(counter)

        counter += list(discrete_data.x_w.values())[i]
        func += newstr + '\n'

    func += '1,\tпри x >= ' + str(discrete_data.X[k - 1])
    line = [
        [discrete_data.X[k - 1], discrete_data.X[k - 1] + intlen],
        [counter, counter],
    ]
    f['lines'].append(line)

    f['dotsx'].append(discrete_data.X[k - 1])
    f['dotsy'].append(counter)

    plot_data['F*'] = func
    plot_data['func'] = f

    return plot_data

def process_discrete_plot_data(distribution_data: DistributionData):
    # Эмпирическая функция
    f = {'lines': [], 'dotsx': [], 'dotsy': []}
    plot_data = {}
    k = len(distribution_data.X)

    func = '0,\tпри x < ' + str(distribution_data.X[0]) + '\n'

    intlen = 3 * (distribution_data.X[1] - distribution_data.X[0])
    line = [[distribution_data.X[0] - intlen, distribution_data.X[0]], [0, 0]]
    f['lines'].append(line)

    counter = list(distribution_data.P.values())[0]
    for i in range(1, k):
        newstr = ''
        newstr += (
                str(round(counter, 2))
                + ',\tпри '
                + str(distribution_data.X[i - 1])
                + ' <= x < '
                + str(distribution_data.X[i])
        )

        line = [
            [distribution_data.X[i - 1], distribution_data.X[i]],
            [counter, counter],
        ]
        f['lines'].append(line)

        f['dotsx'].append(distribution_data.X[i - 1])
        f['dotsy'].append(counter)

        counter += list(distribution_data.P.values())[i]
        func += newstr + '\n'

    func += '1,\tпри x >= ' + str(distribution_data.X[k - 1])
    line = [
        [distribution_data.X[k - 1], distribution_data.X[k - 1] + intlen],
        [counter, counter],
    ]
    f['lines'].append(line)

    f['dotsx'].append(distribution_data.X[k - 1])
    f['dotsy'].append(counter)

    plot_data['F*'] = func
    plot_data['func'] = f

    return plot_data

def integrand(x):
    return exp(-((x ** 2) / 2))


def normal_theorethical_probability(interval, a, sigma):
    l_integral_border = (interval[0] - a) / sigma
    r_integral_border = (interval[1] - a) / sigma
    integral, rounding = oIntegral(integrand, l_integral_border, r_integral_border)
    return (1 / sqrt(2 * pi)) * integral


def process_normal_density(a, sigma):
    density = lambda x, a, sigma: (
            (1 / (sqrt(2 * pi) * sigma)) * exp(-(((x - a) ** 2) / (2 * sigma ** 2)))
    )
    x = [i for i in range(int(a) - 50, int(a) + 50)]
    y = [density(xi, a, sigma) for xi in x]
    return x, y

def distribution_function_visual():
    a

# Считает наблюдаемое значение критерия
def normal_chi2(m, a, sigma, data: ContinuousData):
    value = 0
    n = sum(data.N)
    for i in range(m):
        npi = n * normal_theorethical_probability(data.intervals[i], a, sigma)
        value += ((data.N[i] - npi) ** 2) / npi
    return value


def theoretical_probability_of_evenly(interval, a, b):
    return (interval[1] - interval[0]) / (b - a)


def evenly_process_density(a, b):
    return 1 / (b - a)


def prepare_evenly_process_density_plots(a, b, intervals=[]):
    Xmin = intervals[0][0]
    Xmax = intervals[len(intervals) - 1][1]
    density = evenly_process_density(Xmin, Xmax)
    x = [Xmin, Xmax]
    y = [density for xi in x]
    return x, y

def prepare_distribution_polygon_plots(X = [], P = []):
    return X, P

def theoretical_frequencies_of_evenly(N_total, a, b, intervals=[]):
    n = []
    density = evenly_process_density(intervals[0][0], intervals[len(intervals) - 1][1])
    n_current = N_total * density * (intervals[0][1] - a)
    n.append(n_current)
    for i in range(1, len(intervals) - 1):
        n_current = N_total * density * (intervals[i][1] - intervals[i - 1][1])
        n.append(n_current)
    if len(intervals) > 1:
        n_current = N_total * density * (b - intervals[len(intervals) - 2][1])
        n.append(n_current)
    return n


def evenly_chi2(a, b, data: ContinuousData):
    value = 0
    n_theoretical = []
    n_theoretical = theoretical_frequencies_of_evenly(sum(data.N), a, b, data.intervals)
    n = sum(data.N)
    for i in range(len(data.intervals)):
        chi_square = ((data.N[i] - n_theoretical[i]) ** 2) / data.N[i]
        value += chi_square
    return value


def calculate_a_in_evenly_distribution(Xv, sigma):
    return Xv - (sqrt(3) * sigma)


def calculate_b_in_evenly_distribution(Xv, sigma):
    return Xv + (sqrt(3) * sigma)
