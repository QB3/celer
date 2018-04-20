from sklearn.linear_model import (Lasso as Lasso_sklearn,
                                  LassoCV as LassoCV_sklearn)

from .homotopy import celer_path


class Lasso(Lasso_sklearn):
    """Lasso scikit-learn estimator based on Celer solver

    The optimization objective for Lasso is::

    (1 / (2 * n_samples)) * ||y - Xw||^2_2 + alpha * ||w||_1

    Parameters
    ----------
    alpha : float, optional
        Constant that multiplies the L1 term. Defaults to 1.0.
        ``alpha = 0`` is equivalent to an ordinary least square.
        For numerical reasons, using ``alpha = 0`` with the
        ``Lasso`` object is not advised.

    max_iter : int, optional
        The maximum number of iterations (subproblem definition)

    gap_freq : int
        Number of coordinate descent epochs between each duality gap
        computations.

    max_epochs : int
        Maximum number of CD epochs on the subproblem.

    p0 : int
        First working set size.

    tol : float, optional
        The tolerance for the optimization: if the updates are
        smaller than ``tol``, the optimization code checks the
        dual gap for optimality and continues until it is smaller
        than ``tol``.

    verbose : bool or integer
        Amount of verbosity.

    prune : 0 | 1, optional
        Whether or not to use pruning when growing working sets.

    fit_intercept : bool
        Whether or not to fit an intercept.

    Attributes
    ----------
    coef_ : array, shape (n_features,)
        parameter vector (w in the cost function formula)

    sparse_coef_ : scipy.sparse matrix, shape (n_features, 1)
        ``sparse_coef_`` is a readonly property derived from ``coef_``

    intercept_ : float
        constant term in decision function.

    n_iter_ : int
        number of subproblems solved by celer to reach
        the specified tolerance.

    Examples
    --------
    >>> from celer import Lasso
    >>> clf = Lasso(alpha=0.1)
    >>> clf.fit([[0,0], [1, 1], [2, 2]], [0, 1, 2])
    Lasso(alpha=0.1, copy_X=True, fit_intercept=True, max_iter=1000,
       normalize=False, positive=False, precompute=False, random_state=None,
       selection='cyclic', tol=0.0001, warm_start=False)
    >>> print(clf.coef_)
    [0.85 0.  ]
    >>> print(clf.intercept_)  # doctest: +ELLIPSIS
    0.15...

    See also
    --------
    celer_path
    LassoCV

    References
    ----------
    .. [1] M. Massias, A. Gramfort, J. Salmon
       "Celer: Dual Extrapolation for Faster Lasso Solvers”, ArXiv preprint,
       2018, https://arxiv.org/abs/1802.07481

    """

    def __init__(self, alpha=1., max_iter=100, gap_freq=10,
                 max_epochs=50000, p0=10, verbose=0, tol=1e-6, prune=0):
        super(Lasso, self).__init__(
            alpha=alpha, tol=tol, max_iter=max_iter)
        self.verbose = verbose
        self.gap_freq = gap_freq
        self.max_epochs = max_epochs
        self.p0 = p0
        self.prune = prune
        self.fit_intercept = False
        self.return_n_iter = True

    def path(self, X, y, alphas, **kwargs):
        alphas, coefs, dual_gaps = celer_path(
            X, y, alphas=alphas, max_iter=self.max_iter,
            gap_freq=self.gap_freq, max_epochs=self.max_epochs, p0=self.p0,
            verbose=self.verbose, tol=self.tol, prune=self.prune)
        return (alphas, coefs, dual_gaps, [1])


class LassoCV(LassoCV_sklearn):
    """LassoCV scikit-learn estimator based on Celer solver

    The best model is selected by cross-validation.

    The optimization objective for Lasso is::
        (1 / (2 * n_samples)) * ||y - Xw||^2_2 + alpha * ||w||_1

    Parameters
    ----------
    eps : float, optional
        Length of the path. ``eps=1e-3`` means that
        ``alpha_min / alpha_max = 1e-3``.

    n_alphas : int, optional
        Number of alphas along the regularization path.

    alphas : numpy array, optional
        List of alphas where to compute the models.
        If ``None`` alphas are set automatically

    fit_intercept : boolean, default True
        whether to calculate the intercept for this model. If set
        to false, no intercept will be used in calculations
        (e.g. data is expected to be already centered).

    max_iter : int, optional
        The maximum number of iterations (subproblem definitions).

    tol : float, optional
        The tolerance for the optimization: the solver runs until the duality
        gap is smaller than ``tol`` or the maximum number of iteration is
        reached.

    cv : int, cross-validation generator or an iterable, optional
        Determines the cross-validation splitting strategy.
        Possible inputs for cv are:
        - None, to use the default 3-fold cross-validation,
        - integer, to specify the number of folds.
        - An object to be used as a cross-validation generator.
        - An iterable yielding train/test splits.
        For integer/None inputs, sklearn `KFold` is used.

    verbose : bool or integer
        Amount of verbosity.

    Attributes
    ----------
    alpha_ : float
        The amount of penalization chosen by cross validation
    coef_ : array, shape (n_features,) | (n_targets, n_features)
        parameter vector (w in the cost function formula)
    intercept_ : float | array, shape (n_targets,)
        independent term in decision function.
    mse_path_ : array, shape (n_alphas, n_folds)
        mean square error for the test set on each fold, varying alpha
    alphas_ : numpy array, shape (n_alphas,)
        The grid of alphas used for fitting
    dual_gap_ : ndarray, shape ()
        The dual gap at the end of the optimization for the optimal alpha
        (``alpha_``).
    n_iter_ : int
        number of iterations run by the coordinate descent solver to reach
        the specified tolerance for the optimal alpha.

    Notes
    -----
    For an example, see
    :ref:`examples/plot_lasso_cv.py
    <sphx_glr_auto_examples_linear_model_plot_lasso_model_selection.py>`.
    To avoid unnecessary memory duplication the X argument of the fit method
    should be directly passed as a Fortran-contiguous numpy array.

    See also
    --------
    celer_path
    Lasso
    """

    def __init__(self, eps=1e-3, n_alphas=100, alphas=None,
                 fit_intercept=False, max_iter=100,
                 tol=1e-6, cv=None, verbose=0, gap_freq=10,
                 max_epochs=50000, p0=10, prune=0,
                 normalize=False, precompute='auto'):
        super(LassoCV, self).__init__(
            eps=eps, n_alphas=n_alphas, alphas=alphas, max_iter=max_iter,
            tol=tol, cv=cv, fit_intercept=fit_intercept, verbose=verbose)
        self.gap_freq = gap_freq
        self.max_epochs = max_epochs
        self.p0 = p0
        self.prune = prune
        self.fit_intercept = False
        self.return_n_iter = True

    def path(self, X, y, alphas, **kwargs):
        alphas, coefs, dual_gaps = celer_path(
            X, y, alphas=alphas, max_iter=self.max_iter,
            gap_freq=self.gap_freq, max_epochs=self.max_epochs, p0=self.p0,
            verbose=self.verbose, tol=self.tol, prune=self.prune)
        return (alphas, coefs, dual_gaps)
