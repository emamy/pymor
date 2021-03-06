# -*- coding: utf-8 -*-
# This file is part of the pyMOR project (http://www.pymor.org).
# Copyright 2013-2017 pyMOR developers and contributors. All rights reserved.
# License: BSD 2-Clause License (http://opensource.org/licenses/BSD-2-Clause)


import numpy as np
from packaging.version import Version
import scipy.version
from scipy.sparse.linalg import bicgstab, spsolve, splu, spilu, lgmres, lsqr, LinearOperator

from pymor.algorithms.genericsolvers import _parse_options
from pymor.core.config import config
from pymor.core.defaults import defaults
from pymor.core.exceptions import InversionError
from pymor.core.logger import getLogger
from pymor.operators.numpy import NumpyMatrixOperator


@defaults('bicgstab_tol', 'bicgstab_maxiter', 'spilu_drop_tol',
          'spilu_fill_factor', 'spilu_drop_rule', 'spilu_permc_spec', 'spsolve_permc_spec',
          'spsolve_keep_factorization',
          'lgmres_tol', 'lgmres_maxiter', 'lgmres_inner_m', 'lgmres_outer_k', 'least_squares_lsmr_damp',
          'least_squares_lsmr_atol', 'least_squares_lsmr_btol', 'least_squares_lsmr_conlim',
          'least_squares_lsmr_maxiter', 'least_squares_lsmr_show', 'least_squares_lsqr_atol',
          'least_squares_lsqr_btol', 'least_squares_lsqr_conlim', 'least_squares_lsqr_iter_lim',
          'least_squares_lsqr_show',
          sid_ignore=('least_squares_lsmr_show', 'least_squares_lsqr_show'))
def solver_options(bicgstab_tol=1e-15,
                   bicgstab_maxiter=None,
                   spilu_drop_tol=1e-4,
                   spilu_fill_factor=10,
                   spilu_drop_rule=None,
                   spilu_permc_spec='COLAMD',
                   spsolve_permc_spec='COLAMD',
                   spsolve_keep_factorization=True,
                   lgmres_tol=1e-5,
                   lgmres_maxiter=1000,
                   lgmres_inner_m=39,
                   lgmres_outer_k=3,
                   least_squares_lsmr_damp=0.0,
                   least_squares_lsmr_atol=1e-6,
                   least_squares_lsmr_btol=1e-6,
                   least_squares_lsmr_conlim=1e8,
                   least_squares_lsmr_maxiter=None,
                   least_squares_lsmr_show=False,
                   least_squares_lsqr_damp=0.0,
                   least_squares_lsqr_atol=1e-6,
                   least_squares_lsqr_btol=1e-6,
                   least_squares_lsqr_conlim=1e8,
                   least_squares_lsqr_iter_lim=None,
                   least_squares_lsqr_show=False):
    """Returns available solvers with default |solver_options| for the SciPy backend.

    Parameters
    ----------
    bicgstab_tol
        See :func:`scipy.sparse.linalg.bicgstab`.
    bicgstab_maxiter
        See :func:`scipy.sparse.linalg.bicgstab`.
    spilu_drop_tol
        See :func:`scipy.sparse.linalg.spilu`.
    spilu_fill_factor
        See :func:`scipy.sparse.linalg.spilu`.
    spilu_drop_rule
        See :func:`scipy.sparse.linalg.spilu`.
    spilu_permc_spec
        See :func:`scipy.sparse.linalg.spilu`.
    spsolve_permc_spec
        See :func:`scipy.sparse.linalg.spsolve`.
    spsolve_keep_factorization
        See :func:`scipy.sparse.linalg.spsolve`.
    lgmres_tol
        See :func:`scipy.sparse.linalg.lgmres`.
    lgmres_maxiter
        See :func:`scipy.sparse.linalg.lgmres`.
    lgmres_inner_m
        See :func:`scipy.sparse.linalg.lgmres`.
    lgmres_outer_k
        See :func:`scipy.sparse.linalg.lgmres`.
    least_squares_lsmr_damp
        See :func:`scipy.sparse.linalg.lsmr`.
    least_squares_lsmr_atol
        See :func:`scipy.sparse.linalg.lsmr`.
    least_squares_lsmr_btol
        See :func:`scipy.sparse.linalg.lsmr`.
    least_squares_lsmr_conlim
        See :func:`scipy.sparse.linalg.lsmr`.
    least_squares_lsmr_maxiter
        See :func:`scipy.sparse.linalg.lsmr`.
    least_squares_lsmr_show
        See :func:`scipy.sparse.linalg.lsmr`.
    least_squares_lsqr_damp
        See :func:`scipy.sparse.linalg.lsqr`.
    least_squares_lsqr_atol
        See :func:`scipy.sparse.linalg.lsqr`.
    least_squares_lsqr_btol
        See :func:`scipy.sparse.linalg.lsqr`.
    least_squares_lsqr_conlim
        See :func:`scipy.sparse.linalg.lsqr`.
    least_squares_lsqr_iter_lim
        See :func:`scipy.sparse.linalg.lsqr`.
    least_squares_lsqr_show
        See :func:`scipy.sparse.linalg.lsqr`.

    Returns
    -------
    A dict of available solvers with default |solver_options|.
    """

    opts = {'scipy_bicgstab_spilu':     {'type': 'scipy_bicgstab_spilu',
                                         'tol': bicgstab_tol,
                                         'maxiter': bicgstab_maxiter,
                                         'spilu_drop_tol': spilu_drop_tol,
                                         'spilu_fill_factor': spilu_fill_factor,
                                         'spilu_drop_rule': spilu_drop_rule,
                                         'spilu_permc_spec': spilu_permc_spec},
            'scipy_bicgstab':           {'type': 'scipy_bicgstab',
                                         'tol': bicgstab_tol,
                                         'maxiter': bicgstab_maxiter},
            'scipy_spsolve':            {'type': 'scipy_spsolve',
                                         'permc_spec': spsolve_permc_spec,
                                         'keep_factorization': spsolve_keep_factorization},
            'scipy_lgmres':             {'type': 'scipy_lgmres',
                                         'tol': lgmres_tol,
                                         'maxiter': lgmres_maxiter,
                                         'inner_m': lgmres_inner_m,
                                         'outer_k': lgmres_outer_k},
            'scipy_least_squares_lsqr': {'type': 'scipy_least_squares_lsqr',
                                         'damp': least_squares_lsqr_damp,
                                         'atol': least_squares_lsqr_atol,
                                         'btol': least_squares_lsqr_btol,
                                         'conlim': least_squares_lsqr_conlim,
                                         'iter_lim': least_squares_lsqr_iter_lim,
                                         'show': least_squares_lsqr_show}}

    if config.HAVE_SCIPY_LSMR:
        opts['scipy_least_squares_lsmr'] = {'type': 'scipy_least_squares_lsmr',
                                            'damp': least_squares_lsmr_damp,
                                            'atol': least_squares_lsmr_atol,
                                            'btol': least_squares_lsmr_btol,
                                            'conlim': least_squares_lsmr_conlim,
                                            'maxiter': least_squares_lsmr_maxiter,
                                            'show': least_squares_lsmr_show}

    return opts


@defaults('check_finite', 'default_solver', 'default_least_squares_solver')
def apply_inverse(op, V, options=None, least_squares=False, check_finite=True,
                  default_solver='scipy_spsolve', default_least_squares_solver='scipy_least_squares_lsmr'):
    """Solve linear equation system.

    Applies the inverse of `op` to the vectors in `rhs` using PyAMG.

    Parameters
    ----------
    op
        The linear, non-parametric |Operator| to invert.
    rhs
        |VectorArray| of right-hand sides for the equation system.
    options
        The |solver_options| to use (see :func:`solver_options`).
    check_finite
        Test if solution only containes finite values.
    default_solver
        Default solver to use (scipy_spsolve, scipy_bicgstab, scipy_bicgstab_spilu,
        scipy_lgmres, scipy_least_squares_lsmr, scipy_least_squares_lsqr).
    default_least_squares_solver
        Default solver to use for least squares problems (scipy_least_squares_lsmr,
        scipy_least_squares_lsqr).

    Returns
    -------
    |VectorArray| of the solution vectors.
    """

    assert V in op.range

    if isinstance(op, NumpyMatrixOperator):
        matrix = op._matrix
    else:
        from pymor.algorithms.to_matrix import to_matrix
        matrix = to_matrix(op)

    options = _parse_options(options, solver_options(), default_solver, default_least_squares_solver, least_squares)

    V = V.data
    promoted_type = np.promote_types(matrix.dtype, V.dtype)
    R = np.empty((len(V), matrix.shape[1]), dtype=promoted_type)

    if options['type'] == 'scipy_bicgstab':
        for i, VV in enumerate(V):
            R[i], info = bicgstab(matrix, VV, tol=options['tol'], maxiter=options['maxiter'])
            if info != 0:
                if info > 0:
                    raise InversionError('bicgstab failed to converge after {} iterations'.format(info))
                else:
                    raise InversionError('bicgstab failed with error code {} (illegal input or breakdown)'.
                                         format(info))
    elif options['type'] == 'scipy_bicgstab_spilu':
        if Version(scipy.version.version) >= Version('0.19'):
            ilu = spilu(matrix, drop_tol=options['spilu_drop_tol'], fill_factor=options['spilu_fill_factor'],
                        drop_rule=options['spilu_drop_rule'], permc_spec=options['spilu_permc_spec'])
        else:
            if options['spilu_drop_rule']:
                logger = getLogger('pymor.operators.numpy._apply_inverse')
                logger.error("ignoring drop_rule in ilu factorization due to old SciPy")
            ilu = spilu(matrix, drop_tol=options['spilu_drop_tol'], fill_factor=options['spilu_fill_factor'],
                        permc_spec=options['spilu_permc_spec'])
        precond = LinearOperator(matrix.shape, ilu.solve)
        for i, VV in enumerate(V):
            R[i], info = bicgstab(matrix, VV, tol=options['tol'], maxiter=options['maxiter'], M=precond)
            if info != 0:
                if info > 0:
                    raise InversionError('bicgstab failed to converge after {} iterations'.format(info))
                else:
                    raise InversionError('bicgstab failed with error code {} (illegal input or breakdown)'.
                                         format(info))
    elif options['type'] == 'scipy_spsolve':
        try:
            # maybe remove unusable factorization:
            if hasattr(matrix, 'factorization'):
                fdtype = matrix.factorizationdtype
                if not np.can_cast(V.dtype, fdtype, casting='safe'):
                    del matrix.factorization

            if Version(scipy.version.version) >= Version('0.14'):
                if hasattr(matrix, 'factorization'):
                    # we may use a complex factorization of a real matrix to
                    # apply it to a real vector. In that case, we downcast
                    # the result here, removing the imaginary part,
                    # which should be zero.
                    R = matrix.factorization.solve(V.T).T.astype(promoted_type, copy=False)
                elif options['keep_factorization']:
                    # the matrix is always converted to the promoted type.
                    # if matrix.dtype == promoted_type, this is a no_op
                    matrix.factorization = splu(matrix_astype_nocopy(matrix.tocsc(), promoted_type),
                                                permc_spec=options['permc_spec'])
                    matrix.factorizationdtype = promoted_type
                    R = matrix.factorization.solve(V.T).T
                else:
                    # the matrix is always converted to the promoted type.
                    # if matrix.dtype == promoted_type, this is a no_op
                    R = spsolve(matrix_astype_nocopy(matrix, promoted_type), V.T, permc_spec=options['permc_spec']).T
            else:
                # see if-part for documentation
                if hasattr(matrix, 'factorization'):
                    for i, VV in enumerate(V):
                        R[i] = matrix.factorization.solve(VV).astype(promoted_type, copy=False)
                elif options['keep_factorization']:
                    matrix.factorization = splu(matrix_astype_nocopy(matrix.tocsc(), promoted_type),
                                                permc_spec=options['permc_spec'])
                    matrix.factorizationdtype = promoted_type
                    for i, VV in enumerate(V):
                        R[i] = matrix.factorization.solve(VV)
                elif len(V) > 1:
                    factorization = splu(matrix_astype_nocopy(matrix.tocsc(), promoted_type),
                                         permc_spec=options['permc_spec'])
                    for i, VV in enumerate(V):
                        R[i] = factorization.solve(VV)
                else:
                    R = spsolve(matrix_astype_nocopy(matrix, promoted_type), V.T, permc_spec=options['permc_spec']).reshape((1, -1))
        except RuntimeError as e:
            raise InversionError(e)
    elif options['type'] == 'scipy_lgmres':
        for i, VV in enumerate(V):
            R[i], info = lgmres(matrix, VV,
                                tol=options['tol'],
                                maxiter=options['maxiter'],
                                inner_m=options['inner_m'],
                                outer_k=options['outer_k'])
            if info > 0:
                raise InversionError('lgmres failed to converge after {} iterations'.format(info))
            assert info == 0
    elif options['type'] == 'scipy_least_squares_lsmr':
        from scipy.sparse.linalg import lsmr
        for i, VV in enumerate(V):
            R[i], info, itn, _, _, _, _, _ = lsmr(matrix, VV,
                                                  damp=options['damp'],
                                                  atol=options['atol'],
                                                  btol=options['btol'],
                                                  conlim=options['conlim'],
                                                  maxiter=options['maxiter'],
                                                  show=options['show'])
            assert 0 <= info <= 7
            if info == 7:
                raise InversionError('lsmr failed to converge after {} iterations'.format(itn))
    elif options['type'] == 'scipy_least_squares_lsqr':
        for i, VV in enumerate(V):
            R[i], info, itn, _, _, _, _, _, _, _ = lsqr(matrix, VV,
                                                        damp=options['damp'],
                                                        atol=options['atol'],
                                                        btol=options['btol'],
                                                        conlim=options['conlim'],
                                                        iter_lim=options['iter_lim'],
                                                        show=options['show'])
            assert 0 <= info <= 7
            if info == 7:
                raise InversionError('lsmr failed to converge after {} iterations'.format(itn))
    else:
        raise ValueError('Unknown solver type')

    if check_finite:
        if not np.isfinite(np.sum(R)):
            raise InversionError('Result contains non-finite values')

    return op.source.from_data(R)


# unfortunately, this is necessary, as scipy does not
# forward the copy=False argument in its csc_matrix.astype function
def matrix_astype_nocopy(matrix, dtype):
    if matrix.dtype == dtype:
        return matrix
    else:
        return matrix.astype(dtype)
