import matplotlib.pyplot as plt
from matplotlib import gridspec
import numpy as np
import pandas as pd
import pystan
import scipy as sp
import seaborn as sns
from sklearn.base import BaseEstimator, ClassifierMixin
from sklearn.utils.validation import check_X_y, check_array, check_is_fitted
from sklearn.utils.multiclass import unique_labels
from sklearn.model_selection import StratifiedKFold
import sklearn.metrics as metrics

stan_string = """
data {
    int<lower = 0> N;
    vector[N] x;
    int<lower = 0,upper = 1> y[N];
}
parameters {
    real a; // intercept
    real b; // slope
}
model {
    y ~ bernoulli_logit(a + b * x);
}
"""


def sigmoid(x):
    """Apply the logistic function."""
    return 1 / (1 + np.exp(-x))


def find_nearest_index(array, value):
    """Return the index of the value in array closest to value."""
    idx = (np.abs(array - value)).argmin()
    return idx


my_red = sns.color_palette("coolwarm", 4)[3]
my_blue = sns.color_palette("coolwarm", 4)[0]


class BayesianLogisticClassifierCV(object):
    """A cross-validated Bayesian logistic regression classifier.

    Not compatible with sci-kit learn. Uses BayesianLogisticClassifier for
    regression/classification and scikit-learn for cross-validation.
    """

    def __init__(self, X, y, n_folds, n_iter, n_chains):
        """Initialize with data and settings."""
        self.X = X
        self.y = y
        self.n_folds = n_folds
        self.n_iter = n_iter
        self.n_chains = n_chains
        self.cv = StratifiedKFold(n_splits=self.n_folds)
        self.calculated_quantiles = False

    def fit(self):
        """Fit each CV fold using a BayesianLogisticClassifier."""
        self.fold_acc = []
        self.fold_roc = []
        self.fold_auc = []
        self.fold_clf = []

        for train, test in self.cv.split(self.X, self.y):
            clf = BayesianLogisticClassifier()
            clf.fit(
                self.X[train].reshape(len(self.X[train]), 1),
                self.y[train],
                self.n_iter,
                self.n_chains,
            )
            test_probabilities = clf.predict(self.X[test])
            test_predictions = test_probabilities >= 0.5
            self.fold_acc.append(metrics.accuracy_score(self.y[test], test_predictions))
            self.fold_roc.append(
                metrics.roc_curve(self.y[test], test_probabilities, pos_label=True)
            )
            self.fold_auc.append(metrics.roc_auc_score(self.y[test], test_predictions))
            self.fold_clf.append(clf)

    def calculate_quantiles(self):
        """Calculate quantiles for each regression fold."""
        for c in self.fold_clf:
            c.quantiles()
        self.calculated_quantiles = True

    def plot_mean_model(
        self,
        xs,
        title=None,
        true_cat=None,
        false_cat=None,
        plot_data=True,
        plot_discriminant=True,
        accuracy_string=None,
        discriminant_label_offset=None,
        plot_means=True,
        x_label=None,
        y_label=None,
        ax=None,
    ):
        """Plot the mean of all regression folds."""
        for c in self.fold_clf:
            c.predict(xs)
        self.calculate_quantiles()

        lower = []
        upper = []
        y_hat = []
        for c in self.fold_clf:
            lower.append(c.lower_qs_)
            upper.append(c.upper_qs_)
            y_hat.append(c.predict_y_)
        lower = np.mean(lower, axis=0)
        upper = np.mean(upper, axis=0)
        y_hat = np.mean(y_hat, axis=0)

        sns.set_style("ticks")
        sns.set_palette("muted")

        fsize = 14
        titlesize = 18
        y_jitter = 0.05

        if ax is None:
            f, ax = plt.subplots(figsize=(6, 3))

        ax.tick_params(labelsize=fsize)

        x_range = (np.min(xs), np.max(xs))
        x_ptp = np.ptp(xs)
        ax.set(
            xlim=(x_range[0] - 0.1 * x_ptp, x_range[1] + 0.1 * x_ptp), ylim=(-0.1, 1.1)
        )

        ax.fill_between(xs, lower, upper, facecolor="lightgrey", edgecolor="none")
        ax.plot(xs, y_hat, "k")

        if y_label is not None:
            ax.set_ylabel(y_label, fontsize=fsize)

        if x_label is not None:
            ax.set_xlabel(x_label, fontsize=fsize)

        if plot_discriminant:
            idx = find_nearest_index(y_hat, 0.5)
            boundary = xs[idx]
            ax.plot(
                (boundary, boundary),
                (0.0, 1.0),
                "k--",
                linewidth=1,
                color=sns.xkcd_rgb["grey"],
            )
            if discriminant_label_offset is None:
                dlo = [0.025, 0.42]
            else:
                dlo = discriminant_label_offset

            accuracy = np.mean(self.fold_acc) * 100
            if accuracy_string is None:
                accuracy_string = "{0:.2g}%".format(accuracy)
            ax.text(
                boundary + dlo[0] * x_ptp,
                dlo[1],
                "{0} accuracy\nboundary".format(accuracy_string),
                fontsize=fsize,
            )

        if plot_data:
            ax.scatter(
                self.X[self.y],
                1.0 + np.random.uniform(-y_jitter, y_jitter, len(self.X[self.y])),
                c=my_red,
                marker="^",
                s=40,
                alpha=0.8,
                linewidth=0,
            )
            ax.scatter(
                self.X[~self.y],
                0.0 + np.random.uniform(-y_jitter, y_jitter, len(self.X[~self.y])),
                c=my_blue,
                s=40,
                alpha=0.8,
                linewidth=0,
            )

        if plot_means:
            mean_true = np.mean(self.X[self.y])
            mean_false = np.mean(self.X[~self.y])

            ci_true = sp.stats.bayes_mvs(self.X[self.y])[0][1]
            ci_false = sp.stats.bayes_mvs(self.X[~self.y])[0][1]

            ax.plot([ci_true[0], ci_true[1]], [1.0, 1.0], "k-", linewidth=3)
            ax.plot([ci_false[0], ci_false[1]], [0.0, 0.0], "k-", linewidth=3)
            ax.plot(
                [mean_true, mean_false], [1.0, 0.0], marker="o", color="k", linewidth=0
            )

        if true_cat is not None:
            ax.text(x_range[1] + 0.125 * x_ptp, 1.0, true_cat, fontsize=fsize)
        if false_cat is not None:
            ax.text(x_range[1] + 0.125 * x_ptp, 0.0, false_cat, fontsize=fsize)

        if title is not None:
            ax.set_title(title, fontsize=titlesize)

        sns.despine(bottom=True, left=True)

    def plot_regressions(self, xs, ax=None):
        """Plot each regression fold."""
        for c in self.fold_clf:
            c.predict(xs)
        if not self.calculated_quantiles:
            self.calculate_quantiles()
        if ax is None:
            f, ax = plt.subplots(figsize=(6, 3))

        for c in self.fold_clf:
            c.plot_regression(
                plot_data=False, plot_discriminant=False, plot_means=False, ax=ax
            )

    def plot_roc(self, ax=None, auc_string=None):
        """Plot the mean ROC."""
        plot_roc(self.fold_roc, display_cv_folds=False, auc_string=auc_string, ax=ax)

    def plot_all(
        self,
        xs=None,
        title=None,
        true_cat=None,
        false_cat=None,
        reg_x_label=None,
        reg_y_label=None,
        discriminant_label_offset=None,
        accuracy_string=None,  # option for publication-ready images
        auc_string=None,  # option for publication-ready images
        small=False,
        dpi=None,
    ):
        """Plot both the mean model and the mean ROC with default settings."""
        if small:
            plt.figure(figsize=(10, 1.5), dpi=dpi)
        else:
            plt.figure(figsize=(10, 3), dpi=dpi)
        plt.subplots_adjust(wspace=0.45)
        gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1])
        ax0 = plt.subplot(gs[0])
        ax1 = plt.subplot(gs[1])

        if xs is None:
            range_5p = (np.max(self.X) - np.min(self.X)) * 0.05
            xs_max = np.max(self.X) + range_5p
            xs_min = np.min(self.X) - range_5p
            xs = np.linspace(xs_min, xs_max, 100)

        sns.set_style("ticks")
        sns.set_palette("muted")

        self.plot_mean_model(
            xs=xs,
            true_cat=true_cat,
            false_cat=false_cat,
            title=title,
            x_label=reg_x_label,
            y_label=reg_y_label,
            discriminant_label_offset=discriminant_label_offset,
            accuracy_string=accuracy_string,
            ax=ax0,
        )
        self.plot_roc(ax=ax1, auc_string=auc_string)


class BayesianLogisticClassifier(BaseEstimator, ClassifierMixin):
    """A Bayesian logistic regression classifier.

    Compatible with scikit-learn, uses Stan under the hood.
    """

    def fit(self, X, y, iter=5000, chains=4):
        """Fit the Stan model and estimate params."""
        X, y = check_X_y(X, y)
        self.classes_ = unique_labels(y)
        self.X_ = X
        self.y_ = y

        # sklearn wants X to be of shape (len(x), 1), but Stan wants
        # X to be a 1D array. We kludge thus:
        self.stan_X_ = X
        if len(X.shape) == 2 and X.shape[1] == 1:
            self.stan_X_ = X.reshape(X.shape[0])

        self.stan_ = stan_fit(self.stan_X_, self.y_, iter, chains)
        self.stan_params_ = {
            "a": self.stan_.extract("a", permuted=True)["a"],
            "b": self.stan_.extract("b", permuted=True)["b"],
        }
        self.mean_params_ = [
            np.mean(self.stan_params_["a"]),
            np.mean(self.stan_params_["b"]),
        ]

        return self

    def quantiles(self, p=2.5):
        """Calculate the upper and lower quantiles.

        Run after self.predict().
        """
        pairs = np.array([self.stan_params_["a"], self.stan_params_["b"]]).T

        self.chain_preds_ = []
        for pair in pairs:
            self.chain_preds_.append(predict(pair, self.predict_X_))
        self.chain_preds_ = np.array(self.chain_preds_)

        self.lower_qs_ = chain_quantiles(p, self.chain_preds_, self.predict_X_)
        self.upper_qs_ = chain_quantiles(100.0 - p, self.chain_preds_, self.predict_X_)

        return (self.lower_qs_, self.upper_qs_)

    def predict(self, X, y=None):
        """Estimate the probability of X being the positive class."""
        try:
            getattr(self, "mean_params_")
        except AttributeError:
            raise RuntimeError("Classifier must be trained before predicting.")
        self.predict_X_ = X
        self.predict_y_ = sigmoid(self.mean_params_[0] + self.mean_params_[1] * X)
        return self.predict_y_

    def score(self, X, y, sample_weight=None):
        """Return mean accuracy on test data X and true test labels Y."""
        if len(X.shape) == 2 and X.shape[1] == 1:
            X = X.reshape(X.shape[0])

        probabilities = self.predict(X)
        predicted_classes = (probabilities >= 0.5).astype(int)
        correct = predicted_classes == y
        return np.mean(correct)

    def plot_regression(
        self,
        title=None,
        true_cat=None,
        false_cat=None,
        plot_data=True,
        plot_discriminant=True,
        plot_means=True,
        ax=None,
    ):
        """Plot the logistic regression using Seaborn."""
        sns.set_style("ticks")
        sns.set_palette("muted")

        fsize = 14
        titlesize = 18
        y_jitter = 0.05

        if ax is None:
            f, ax = plt.subplots(figsize=(6, 3))

        ax.tick_params(labelsize=fsize)

        x_range = (np.min(self.predict_X_), np.max(self.predict_X_))
        x_ptp = np.ptp(self.predict_X_)
        ax.set(
            xlim=(x_range[0] - 0.1 * x_ptp, x_range[1] + 0.1 * x_ptp), ylim=(-0.1, 1.1)
        )

        ax.fill_between(
            self.predict_X_,
            self.lower_qs_,
            self.upper_qs_,
            facecolor="lightgrey",
            edgecolor="none",
        )
        ax.plot(self.predict_X_, self.predict_y_, "k")

        if plot_discriminant:
            idx = find_nearest_index(self.predict_y_, 0.5)
            ax.plot(
                (self.predict_X_[idx], self.predict_X_[idx]),
                (0.0, 1.0),
                "k--",
                linewidth=1,
                color=sns.xkcd_rgb["grey"],
            )

        if plot_data:
            ax.scatter(
                self.X_[self.y_],
                1.0 + np.random.uniform(-y_jitter, y_jitter, len(self.X_[self.y_])),
                c=my_red,
                marker="^",
                s=40,
                alpha=0.8,
                linewidth=0,
            )
            ax.scatter(
                self.X_[~self.y_],
                0.0 + np.random.uniform(-y_jitter, y_jitter, len(self.X_[~self.y_])),
                c=my_blue,
                marker="^",
                s=40,
                alpha=0.8,
                linewidth=0,
            )

        if plot_means:
            mean_true = np.mean(self.X_[self.y_])
            mean_false = np.mean(self.X_[~self.y_])

            ci_true = sp.stats.bayes_mvs(self.X_[self.y_])[0][1]
            ci_false = sp.stats.bayes_mvs(self.X_[~self.y_])[0][1]

            ax.plot([ci_true[0], ci_true[1]], [1.0, 1.0], "k-", linewidth=3)
            ax.plot([ci_false[0], ci_false[1]], [0.0, 0.0], "k-", linewidth=3)
            ax.plot(
                [mean_true, mean_false], [1.0, 0.0], marker="o", color="k", linewidth=0
            )

        if true_cat is not None:
            ax.text(x_range[1] + 0.125 * x_ptp, 1.0, true_cat, fontsize=fsize)
        if false_cat is not None:
            ax.text(x_range[1] + 0.125 * x_ptp, 0.0, false_cat, fontsize=fsize)

        if title is not None:
            ax.set_title(title, fontsize=titlesize)

        sns.despine(bottom=True, left=True)


def bayesian_logistic(x, y, prediction_range=None, prediction_resolution=100):
    """Generate the Stan model along with important derivative values."""
    fit = stan_fit(x, y)
    params = pd.DataFrame(
        {
            "a": fit.extract("a", permuted=True)["a"],
            "b": fit.extract("b", permuted=True)["b"],
        }
    )
    mean_params = params.mean()
    if prediction_range is None:
        prediction_range = (np.min(x), np.max(x))
    xs = np.linspace(prediction_range[0], prediction_range[1], prediction_resolution)
    y_hat = predict(mean_params, xs)

    def predict_curried(params):
        return predict(params, xs)

    chain_preds = []
    for row in params.itertuples():
        chain_preds.append(predict_curried(row[1:]))
    chain_preds = np.array(chain_preds)

    lower_qs = chain_quantiles(2.5, chain_preds, xs)
    upper_qs = chain_quantiles(97.5, chain_preds, xs)
    return {
        "fit": fit,
        "params": params,
        "mean_params": mean_params,
        "xs": xs,
        "y_hat": y_hat,
        "lower_qs": lower_qs,
        "upper_qs": upper_qs,
    }


def chain_quantiles(q, chain_preds, xs):
    """Calculate the quantile q for every prediction in chain_preds over xs."""
    quantiles = []
    for x in range(chain_preds.shape[1]):
        param_values = chain_preds[:, x]
        quantiles.append(np.percentile(param_values, q))
    return quantiles


def predict(params, x):
    """Given parameters and x, return est. probability of +class membership."""
    return sigmoid(params[0] + params[1] * x)


def stan_fit(x, y, iter=5000, chains=4):
    """Given predictor x and responses y, return a Stan fit object."""
    stan_data = {"x": x, "y": [int(b) for b in y], "N": len(x)}
    return pystan.stan(model_code=stan_string, data=stan_data, iter=iter, chains=chains)


def get_p_string(p_value, prepend=""):
    """Return a string expressing a p-value."""
    if p_value is None:
        p_string = ""
    elif p_value < 0.001:
        p_string = "{0}p < .001".format(prepend)
    else:
        p_formatted = "{0:.2g}".format(p_value).lstrip("0")
        p_string = "{0}p = {1}".format(prepend, p_formatted)
    return p_string


def plot_roc(roc_folds, display_cv_folds=True, p_auc=None, auc_string=None, ax=None):
    """Plot the mean of a list of sklearn ROC curves."""
    fpr_folds = [x[0] for x in roc_folds]
    tpr_folds = [x[1] for x in roc_folds]

    sns.set_style("ticks")
    sns.set_palette("husl", len(fpr_folds))

    fsize = 14
    titlesize = 14

    if ax is None:
        f, ax = plt.subplots(1, 1, figsize=(3, 3))

    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
    ax.tick_params(labelsize=fsize)
    ax.set_xlabel("False Positive Rate", fontsize=fsize)
    ax.set_ylabel("True Positive Rate", fontsize=fsize)

    mean_tpr = 0.0
    mean_fpr = np.linspace(0, 1, 100)

    fold_aucs = []

    ax.plot([0, 1], [0, 1], "k--")

    for fpr, tpr in zip(fpr_folds, tpr_folds):
        fold_auc = metrics.auc(fpr, tpr)
        fold_aucs.append(fold_auc)

        mean_tpr += sp.interp(mean_fpr, fpr, tpr)
        mean_tpr[0] = 0.0

        if display_cv_folds:
            ax.plot(fpr, tpr, alpha=0.7)

    mean_tpr /= len(fpr_folds)
    mean_tpr[-1] = 1.0
    mean_auc = np.mean(fold_aucs)

    ax.plot(mean_fpr, mean_tpr, c=sns.xkcd_rgb["dark grey"], linewidth=2.5)

    if auc_string is None:
        auc_string = "{0:.2g}".format(mean_auc)

    p_string = get_p_string(p_auc, prepend=", ")
    ax.set_title("AUC = {0}{1}".format(auc_string, p_string), fontsize=titlesize)
    sns.despine(left=True, bottom=True)
