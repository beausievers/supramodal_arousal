import numpy as np
import scipy as sp

import statsmodels.api as sm
from sklearn.lda import LDA 
from sklearn import cross_validation
from sklearn import datasets 
from sklearn import metrics 

import matplotlib.pyplot as plt
from matplotlib import gridspec
import seaborn as sns

import copy

def find_nearest_idx(a, a0):
    "Element in nd array `a` closest to the scalar value `a0`"
    idx = np.abs(a - a0).argmin()
    return idx

def get_p_string(p_value, prepend=''):
    if p_value is None:
        p_string = ''
    elif p_value < .001:
        p_string = "{0}p < .001".format(prepend)
    else:
        p_formatted = "{0:.2g}".format(p_value).lstrip('0')
        p_string = "{0}p = {1}".format(prepend, p_formatted)
    return p_string
    
def logistic_plot_full(x, y, data, n_folds=3, n_perm=2000, 
                  x_label=None, y_label=None, 
                  true_cat=None, false_cat=None, title=None,
                  plot_means=True, plot_discriminant=False, 
                  discriminant_label_offset=None, accuracy_string=None,
                  display_cv_folds=True):
    base_acc, base_auc, base_fold_roc, p_acc, p_auc = logistic_cv(data[x], 
        data[y], n_folds, n_perm)
    
    f = plt.figure(figsize=(10,3))
    plt.subplots_adjust(wspace=0.45)
    gs = gridspec.GridSpec(1, 2, width_ratios=[2,1])
    ax0 = plt.subplot(gs[0])
    ax1 = plt.subplot(gs[1])
       
    logistic_plot(x, y, data, x_label=x_label, y_label=y_label, 
                  true_cat=true_cat, false_cat=false_cat, title=title,
                  plot_means=plot_means, plot_discriminant=plot_discriminant,
                  discriminant_label_offset=discriminant_label_offset,
                  accuracy_string=accuracy_string,
                  p_acc=p_acc, ax=ax0)
    plot_roc_cv(base_fold_roc, p_auc=p_auc, display_cv_folds=display_cv_folds,
                ax=ax1)
    
def logistic_plot(x, y, data, x_label=None, y_label=None, 
                  true_cat=None, false_cat=None, title=None,
                  plot_means=True, plot_discriminant=False, p_acc=None, 
                  discriminant_label_offset=None, accuracy_string = None,
                  ax=None):
    sns.set_style('ticks')
    sns.set_palette('muted')
    
    fsize = 14
    titlesize = 18

    if ax is None:
        f, ax = plt.subplots(figsize=(6,3))
    
    ax.tick_params(labelsize=fsize)
    
    x_range = (np.min(data[x]), np.max(data[x]))
    x_ptp = np.ptp(data[x])
    ax.set(xlim=(x_range[0] - .1 * x_ptp, x_range[1] + .1 * x_ptp), ylim=(-.1, 1.1))
    
    sns.regplot(x=x, y=y, data=data, logistic=True, y_jitter=.03, scatter=False, 
                ax=ax, color=sns.xkcd_rgb["dark grey"])

    if y_label is None:
        ax.set_ylabel("probability({0})".format(y), fontsize=fsize)
    else:
        ax.set_ylabel(y_label, fontsize=fsize)
        
    if x_label is None:
        ax.set_xlabel(x, fontsize=fsize)
    else:
        ax.set_xlabel(x_label, fontsize=fsize)
        
    data_true  = data[data[y]]
    data_false = data[~data[y]]
    
    y_jitter = .05
    
    my_blue = sns.color_palette("coolwarm", 4)[0]
    my_red = sns.color_palette("coolwarm", 4)[3]
    
    ax.scatter(data_true[x], 
                data_true[y] + np.random.uniform(-y_jitter, y_jitter, len(data_true[y])), 
                c=my_red,
                marker='^', 
                s=40, alpha=0.8, linewidth=0)
    ax.scatter(data_false[x], 
                data_false[y] + np.random.uniform(-y_jitter, y_jitter, len(data_false[y])), 
                c=my_blue,
                s=31, alpha=0.8, linewidth=0)
    
    if plot_discriminant:
        glm_binom = sm.GLM(data[y],
                          np.column_stack([np.ones(len(data[x])), data[x]]),
                          family=sm.families.Binomial())
        model = glm_binom.fit()
        
        stack = np.column_stack([np.ones(len(data[x])), data[x]])
        pred = model.predict(stack)

        binary_predictions = pred >= 0.5
        actual = data[y]

        correct_count = np.sum(binary_predictions == actual)
        accuracy = correct_count / float(len(actual))
        
        full_x = np.linspace(np.min(data[x]), np.max(data[x]), 200)
        full_pred = model.predict(np.column_stack([np.ones(len(full_x)), full_x]))
        boundary = full_x[find_nearest_idx(full_pred, 0.5)]
        ax.plot([boundary, boundary], [0, 1], 'k--', linewidth=1, color=sns.xkcd_rgb['grey'])
        
        if discriminant_label_offset == None:
            dlo = [0.025, 0.42]
        else:
            dlo = discriminant_label_offset
            
        p_string = get_p_string(p_acc, prepend=', ')
        if accuracy_string is None:
            accuracy_string = "{0:.2g}%".format(accuracy)
        ax.text(boundary + dlo[0] * x_ptp, dlo[1], "{0} accuracy\nboundary{1}".format(accuracy_string, p_string), fontsize=fsize)

    if plot_means:
        mean_true = np.mean(data[data[y]][x])
        mean_false = np.mean(data[~data[y]][x])
        
        ci_true = sp.stats.bayes_mvs(data[data[y]][x])[0][1]
        ci_false = sp.stats.bayes_mvs(data[~data[y]][x])[0][1]
        
        ax.plot([ci_true[0], ci_true[1]], [1.0, 1.0], 'k-', linewidth=3)
        ax.plot([ci_false[0], ci_false[1]], [0.0, 0.0], 'k-', linewidth=3)
        ax.plot([mean_true, mean_false], [1.0, 0.0], marker='o', color='k', linewidth=0)
    
    if true_cat is not None:
        ax.text(x_range[1] + .125 * x_ptp, 1.0, true_cat, fontsize=fsize)
    if false_cat is not None:
        ax.text(x_range[1] + .125 * x_ptp, 0.0, false_cat, fontsize=fsize)
        
    if title is not None:
        ax.set_title(title, fontsize=titlesize)
    
    sns.despine(bottom=True, left=True)
    
def logistic_cv(X, y, n_folds=3, n_perm=2000):
    cv = cross_validation.StratifiedKFold(y, n_folds)
    X_sm = sm.add_constant(np.array(X))
    rs = np.random.RandomState()
    
    # Compute base logistic regression
    base_fold_acc = []
    base_fold_roc = []
    base_fold_auc = []
    
    for train, test in cv:
        glm_binom = sm.GLM(y[train], X_sm[train], family=sm.families.Binomial())
        glm_binom_fitted = glm_binom.fit()
        pred_sm = glm_binom_fitted.predict(X_sm[test])
        pred_bin_sm = pred_sm >= 0.5
        acc_sm = metrics.accuracy_score(y[test], pred_bin_sm)
        base_fold_acc.append(acc_sm)
        fold_roc_data = metrics.roc_curve(y[test], 
                                          pred_sm, 
                                          pos_label=True)
        base_fold_roc.append(fold_roc_data)
        base_fold_auc.append(metrics.roc_auc_score(y[test], pred_sm))
    
    base_acc = np.mean(base_fold_acc)
    base_auc = np.mean(base_fold_auc)
    
    print("Base accuracy: {0}  Base AUC: {1}".format(base_acc, base_auc))
    
    print("Computing null distrubtion from {0} permutations".format(n_perm))
    perm_acc = []
    perm_auc = []
    
    for _ in xrange(n_perm):
        perm_fold_acc = []
        perm_fold_auc = []
        
        labels = copy.deepcopy(y)
        labels = rs.permutation(labels)
        
        for train, test in cv:
            glm_binom = sm.GLM(labels[train], X_sm[train], family=sm.families.Binomial())
            glm_binom_fitted = glm_binom.fit()
            pred_sm = glm_binom_fitted.predict(X_sm[test])
            pred_bin_sm = pred_sm >= 0.5
            acc_sm = metrics.accuracy_score(y[test], pred_bin_sm)
            perm_fold_acc.append(acc_sm)
            perm_fold_auc.append(metrics.roc_auc_score(labels[test], pred_sm))
        
        perm_acc.append(np.mean(perm_fold_acc))
        perm_auc.append(np.mean(perm_fold_auc))
        
    p_acc = (np.sum(perm_acc >= base_acc) + 1.0) / (n_perm + 1.0)
    p_auc = (np.sum(perm_auc >= base_auc) + 1.0) / (n_perm + 1.0)
    
    print("Accuracy p-value: {0}".format(p_acc))
    print("AUC p-value: {0}".format(p_auc))
    
    return (base_acc, base_auc, base_fold_roc, p_acc, p_auc)
    
def plot_roc_cv(roc_folds, display_cv_folds=True, p_auc=None, ax=None):
    fpr_folds = [x[0] for x in roc_folds]
    tpr_folds = [x[1] for x in roc_folds]
    
    sns.set_style('ticks')
    sns.set_palette("husl", len(fpr_folds))
    
    fsize = 14
    titlesize = 14
    
    if ax is None:
        f, ax = plt.subplots(1, 1, figsize=(3,3))
        
    ax.set_xlim(-.1, 1.1)
    ax.set_ylim(-.1, 1.1)
    ax.tick_params(labelsize=fsize)
    ax.set_xlabel("False Positive Rate", fontsize=fsize)
    ax.set_ylabel("True Positive Rate", fontsize=fsize)

    mean_tpr = 0.0
    mean_fpr = np.linspace(0, 1, 100)
    
    fold_aucs = []
    
    ax.plot([0, 1], [0, 1], 'k--')
    
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
    
    p_string = get_p_string(p_auc, prepend=', ')
    ax.set_title("AUC = {0:.2g}{1}".format(mean_auc, p_string), 
                 fontsize=titlesize)
    sns.despine(left=True, bottom=True)