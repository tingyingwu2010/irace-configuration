import argparse
import numpy as np

from scipy.optimize import differential_evolution

from sklearn.tree import DecisionTreeClassifier
from imblearn.metrics import geometric_mean_score

import pickle

with open('../X_train.pickle', 'rb') as f:
    X_train = pickle.load(f)

with open('../y_train.pickle', 'rb') as f:
    y_train = pickle.load(f)

with open('../X_test.pickle', 'rb') as f:
    X_test = pickle.load(f)

with open('../y_test.pickle', 'rb') as f:
    y_test = pickle.load(f)

__author__ = "Manolomon"
__license__ = "MIT"
__version__ = "1.0"

import pickle


def logger(xa, convergence):
    x_str = np.array_repr(xa).replace('\n', '')
    print(x_str)


def fitness_func(individual):  # Fitness Function
    global X_train
    global y_train
    classifier = DecisionTreeClassifier(
        criterion="gini" if individual[0] < 0.5 else "entropy",
        splitter="best" if individual[1] < 0.5 else "random",
        max_depth=None if individual[2] < 2 else int(round(individual[2])),
        min_samples_leaf=individual[3],
        min_weight_fraction_leaf=individual[4],
        max_features=individual[5],
        random_state=int(round(individual[6])),
        max_leaf_nodes=None if individual[7] < 2 else int(
            round(individual[7])),
        min_impurity_decrease=individual[8]
    )
    classifier.fit(X_train, y_train)

    g_mean = geometric_mean_score(
        y_test, classifier.predict(X_test), average='weighted')
    del classifier
    return -1 * g_mean


bounds = [
    (0, 1),  # criterion: {"gini", "entropy"}, default="gini"
    (0, 1),  # splitter: {"best", "random"}, default="best"
    (1, 100),  # max_depth: int, default=None
    (0, 0.5),  # min_samples_leaf: int or float, default=1
    (0, 0.5),  # min_weight_fraction_leaf: float, default=0.0
    (0, 1),   # max_features: int, float or {"auto", "sqrt", "log2"}, default=None
    (0, 10),  # random_state: int, RandomState instance, default=None
    (1, 100),  # max_leaf_nodes: int, default=None
    (0, 1)  # min_impurity_decrease: float, default=0.0
]

if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description='Decision Tree Hyperparameter tuning for software requirements categorization using Differential Evolution')
    ap.add_argument("-v", "--verbose",
                    help="increase output verbosity", action="store_true")
    ap.add_argument('--np', dest='np', type=int,
                    required=True, help='Population size')
    ap.add_argument('--max_gen', dest='max_gen', type=int,
                    required=True, help='Genarations')
    ap.add_argument('--f', dest='f', type=float,
                    required=True, help='Scale Factor')
    ap.add_argument('--cr', dest='cr', type=float,
                    required=True, help='Crossover percentage')
    ap.add_argument('--datfile', dest='datfile', type=str,
                    help='File where it will be save the score (result)')

    args = ap.parse_args()

    result = differential_evolution(fitness_func, bounds, disp=True, popsize=args.np, maxiter=args.max_gen,
                                    mutation=args.f, recombination=args.cr, strategy='rand1bin', callback=logger)

    # print("Best individual: [criterion=%s, splitter=%s, max_depth=%s, min_samples_leaf=%s, #min_weight_fraction_leaf=%s, max_features=%s, random_state=%s, max_leaf_nodes=%s, #min_impurity_decrease=%s] f(x)=%s" % (
    #    "gini" if result.x[0] < 0.5 else "entropy",
    #    "best" if result.x[1] < 0.5 else "random",
    #    None if result.x[2] < 2 else int(round(result.x[2])),
    #    result.x[3],
    #    result.x[4],
    #    result.x[5],
    #    int(round(result.x[6])),
    #    None if result.x[7] < 2 else int(round(result.x[7])),
    #    result.x[8],
    #    result.fun*(-100)))

    if args.datfile:
        with open(args.datfile, 'w') as f:
            f.write(str(result.fun*(-100)))
