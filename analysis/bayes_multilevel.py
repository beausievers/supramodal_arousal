import numpy as np

import pandas as pd

import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn as sns

from bambi import Model

from sklearn import model_selection
from sklearn.metrics import roc_curve, roc_auc_score, r2_score
import tabulate

from logistic import plot_roc_cv


def get_terms(trace):
    terms = trace.varnames
    exclude = ["_sd_log__", "_offset", "_sd"]
    for e in exclude:
        terms = [t for t in terms if t[-len(e) :] != e]
    return terms


def get_group_id_index(result, varname, group_id):
    varname_group_string = f"{varname}[{group_id}]"
    return result.level_dict[varname].index(varname_group_string)


def get_weights(result, trace, varnames, group_dict=None):
    weights = []
    for v in varnames:
        if "|" not in v:
            weights.append(trace.get_values(v).mean())
        else:
            group_name = v.split("|")[1]
            group_id = group_dict[group_name]
            group_id_index = get_group_id_index(result, v, group_id)
            weights.append(trace.get_values(v)[:, group_id_index].mean())
    return weights


def df_add_term_cols(df, terms):
    """Appends interaction columns to a Pandas dataframe specified by terms.

    When creating new columns, converts bool series to int. Returns new
    dataframe.
    """
    new_df = df.copy()
    terms = [t for t in terms if "|" not in t]
    terms = [t for t in terms if t != "Intercept"]
    terms = [t for t in terms if t[0:2] != "1|"]

    for term in terms:
        col_names = term.split(":")

        # Create interaction term column
        if len(col_names) > 1:
            series = [new_df[col_name] for col_name in col_names]
            for i, s in enumerate(series):
                if s.dtype == bool:
                    series[i] = series[i].astype(int)
            new_df[term] = np.prod(np.array(series).T, axis=1)
    return new_df


def invlogit(x):
    return 1 / (1 + np.exp(-x))


def predict(row, terms, result, trace, debug=False):
    subID = row["subID"]
    weights = get_weights(result, trace, terms, {"subID": subID})
    terms_fixed = [t for t in terms if ("|" not in t and "_sd_interval" not in t)]
    if debug:
        print(f"weights: {weights}")
        print(f"terms: {terms}")
        print(f"terms_fixed: {terms_fixed}")

    # Separate fixed and random effects, then adjust fixed effects weights by
    # adding random effects offsets

    # BIG OL' WARNING: this is not generalized and only makes sense for the
    # specific analysis I'm doing.
    w = np.array(
        [weights[0 : int(len(weights) / 2)], weights[int(len(weights) / 2) :]]
    ).sum(axis=0)
    x = np.hstack([1, row[terms_fixed[1:]].as_matrix()])
    if debug:
        print(f"w: {w.shape} {w}")
        print(f"x: {x.shape} {x}")

    prob = invlogit(np.sum(x * w))
    return prob


def bambi_cv(
    df, model_string, model_dict, n_splits=5, dv="highArousal", grouping_var="subID"
):
    fold_acc = []
    fold_results = []
    fold_models = []
    fold_roc = []
    fold_auc = []

    cv = model_selection.StratifiedKFold(n_splits=n_splits, shuffle=True)

    for train_ix, test_ix in cv.split(df, df[grouping_var]):
        m = Model(df.loc[train_ix, :])
        r = m.fit(model_string, **model_dict)

        terms = get_terms(m.backend.trace)
        df_sm_ex = df_add_term_cols(df, terms)
        df_sm_ex_test = df_sm_ex.loc[test_ix, :]

        probs = []
        for _, row in df_sm_ex_test.iterrows():
            probs.append(predict(row, terms, r, m.backend.trace))
        preds = np.array(probs) > 0.5

        df_sm_ex_test["pred"] = preds

        fold_roc.append(roc_curve(df_sm_ex_test[dv], probs))
        fold_auc.append(roc_auc_score(df_sm_ex_test[dv], probs))
        fold_acc.append(np.mean(df_sm_ex_test["pred"] == df_sm_ex_test[dv]))
        fold_results.append(r)
        fold_models.append(m)

    return (fold_acc, fold_results, fold_models, fold_roc, fold_auc)


def predict_r2(row, terms, result, trace, interaction=True, debug=False):
    subID = row["subID"]
    weights = get_weights(result, trace, terms, {"subID": subID})
    terms_fixed = [t for t in terms if ("|" not in t and "_sd_interval" not in t)]
    if debug:
        print(f"weights: {weights}")
        print(f"terms: {terms}")
        print(f"terms_fixed: {terms_fixed}")

    # Separate fixed and random effects, then adjust fixed effects weights by
    # adding random effects offsets

    # BIG OL' WARNING: this is not generalized and only makes sense for the
    # specific analysis I'm doing.
    if interaction:
        w = np.array(
            [
                weights[0] + weights[9],
                weights[1],
                weights[2] + weights[11],
                weights[3] + weights[10],
                weights[4],
                weights[5],
                weights[6],
                weights[7],
            ]
        )
    else:
        w = np.array(
            [
                weights[0] + weights[5],
                weights[1],
                weights[2] + weights[6],
                weights[3] + weights[7],
            ]
        )
    x = np.hstack([1, row[terms_fixed[1:]].as_matrix()])
    if debug:
        print(f"w: {w.shape} {w}")
        print(f"x: {x.shape} {x}")

    yhat = np.sum(x * w)

    return yhat


def bambi_cv_r2(
    df,
    model_string,
    model_dict,
    n_splits=5,
    dv="sc",
    grouping_var="subID",
    interaction=True,
    debug=False,
):
    fold_results = []
    fold_models = []
    fold_r2s = []

    cv = model_selection.StratifiedKFold(n_splits=n_splits, shuffle=True)

    for train_ix, test_ix in cv.split(df, df[grouping_var]):
        m = Model(df.loc[train_ix, :])
        r = m.fit(model_string, **model_dict)

        terms = get_terms(m.backend.trace)
        df_sm_ex = df_add_term_cols(df, terms)
        df_sm_ex_test = df_sm_ex.loc[test_ix, :]

        yhats = []
        ys = []
        for _, row in df_sm_ex_test.iterrows():
            yhats.append(
                predict_r2(
                    row, terms, r, m.backend.trace, interaction=interaction, debug=debug
                )
            )
            ys.append(row[dv])

        fold_r2s.append(r2_score(ys, yhats))
        fold_results.append(r)
        fold_models.append(m)
    return fold_r2s, fold_results, fold_models


def plot_fixed(
    param,
    summary_df,
    data_df,
    steps=100,
    x_label=None,
    y_label=None,
    title=None,
    ax=None,
):
    sns.set_style("ticks")
    sns.set_palette("muted")

    fsize = 14
    titlesize = 18

    x_min = data_df[param].min()
    x_max = data_df[param].max()

    summary_param = param

    if type(x_min) is bool or type(x_min) is np.bool_:
        x_min = float(x_min)
        x_max = float(x_max)
        summary_param += "[T.True]"

    slope_mean = summary_df.loc[summary_param]["mean"]
    slope_lower = summary_df.loc[summary_param]["hpd0.95_lower"]
    slope_upper = summary_df.loc[summary_param]["hpd0.95_upper"]

    i_mean = summary_df.loc["Intercept"]["mean"]
    i_lower = summary_df.loc["Intercept"]["hpd0.95_lower"]
    i_upper = summary_df.loc["Intercept"]["hpd0.95_upper"]

    xs = np.linspace(np.floor(x_min), np.ceil(x_max), steps)

    X = np.hstack([np.array([1] * len(xs))[:, None], xs[:, None]])
    yhat = invlogit(np.dot(X, np.vstack([i_mean, slope_mean]))).T[0]
    yhat_lower = invlogit(np.dot(X, np.vstack([i_lower, slope_lower]))).T[0]
    yhat_upper = invlogit(np.dot(X, np.vstack([i_upper, slope_upper]))).T[0]

    if ax is None:
        fig, ax = plt.subplots(figsize=(7, 5))

    ax.tick_params(labelsize=fsize)

    ax.plot(xs, yhat, color="black")
    ax.fill_between(xs, yhat_upper, yhat_lower, color="gray", alpha=0.4)

    if x_label is None:
        x_label = param
    if y_label is None:
        y_label = f"p(highArousal | {param})"

    ax.set_xlabel(x_label, fontsize=fsize)
    ax.set_ylabel(y_label, fontsize=fsize)

    if title is not None:
        ax.set_title(title, fontsize=titlesize)

    sns.despine(bottom=True, left=True)


def plot_full_cv(
    fold_results, fold_roc, param, data_df, x_label=None, y_label=None, title=None
):
    plt.figure(figsize=(10, 3))
    plt.subplots_adjust(wspace=0.45)
    gs = gridspec.GridSpec(1, 2, width_ratios=[2, 1])
    ax0 = plt.subplot(gs[0])
    ax1 = plt.subplot(gs[1])

    summary_dfs = [res.summary() for res in fold_results]
    df_concat = pd.concat(summary_dfs)
    mean_df = df_concat.groupby(df_concat.index).mean()

    plot_fixed(
        param, mean_df, data_df, x_label=x_label, y_label=y_label, title=title, ax=ax0
    )
    plot_roc_cv(fold_roc, display_cv_folds=False, ax=ax1)


table_headers = ["M", "SD", "CI lower", "CI upper", "Effective N", "Gelman-Rubin"]


def summary_table(results, table_headers=table_headers):
    all_summaries = [res.summary() for res in results]
    all_summaries_concat = pd.concat(all_summaries)
    all_summaries_mean = (
        all_summaries_concat.groupby(all_summaries_concat.index).mean().round(2)
    )
    table = (
        tabulate.tabulate(all_summaries_mean, headers=table_headers, tablefmt="pipe")
        .replace("|subID", "\|subID")
        .replace("[T.True]", "")
    )
    return table
