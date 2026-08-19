"""Trava de regressão para a estatística implementada à mão.

Por que existe: formal_tests.py e robust_tests.py reimplementam Spearman,
Spearman parcial, Mann-Kendall, Wilcoxon, Mann-Whitney e Cliff's delta em
stdlib puro, sem dependência de scipy. Isso é bom para reprodutibilidade e
péssimo sem teste: uma mudança silenciosa passaria despercebida, e todas as
conclusões do paper saem dessas funções.

Roda: python -m pytest tests/ -q
"""
import math
import random

import pytest

scipy_stats = pytest.importorskip("scipy.stats")

from code.analysis.formal_tests import spearman, partial_spearman, mann_kendall  # noqa: E402
from code.analysis.robust_tests import wilcoxon, mannwhitney, cliffs_delta      # noqa: E402


def _sample(n, seed):
    rng = random.Random(seed)
    x = [rng.gauss(0, 1) for _ in range(n)]
    y = [0.6 * xi + rng.gauss(0, 0.8) for xi in x]
    return x, y


@pytest.mark.parametrize("seed", [1, 7, 42])
def test_spearman_matches_scipy(seed):
    x, y = _sample(40, seed)
    ours = spearman(x, y)
    theirs = scipy_stats.spearmanr(x, y).statistic
    assert abs(ours - theirs) < 1e-9


@pytest.mark.parametrize("seed", [3, 11])
def test_wilcoxon_matches_scipy(seed):
    rng = random.Random(seed)
    d = [rng.gauss(-0.2, 1) for _ in range(60)]
    _, p_ours, _ = wilcoxon(d)
    p_theirs = scipy_stats.wilcoxon(d).pvalue
    assert abs(p_ours - p_theirs) < 5e-3


@pytest.mark.parametrize("seed", [5, 13])
def test_mannwhitney_and_cliff_match_scipy(seed):
    a, _ = _sample(35, seed)
    b = [v + 0.5 for v in _sample(45, seed + 1)[0]]
    # mannwhitney() devolve (z, p) — duas saidas, nao tres.
    _, p_ours = mannwhitney(a, b)
    p_theirs = scipy_stats.mannwhitneyu(a, b, alternative="two-sided").pvalue
    assert abs(p_ours - p_theirs) < 5e-3
    # Cliff's delta a partir do U de scipy: delta = 1 - 2U/(na*nb), com U medido
    # sobre `a`. O sinal segue a convencao "a menor que b => delta negativo".
    u = scipy_stats.mannwhitneyu(a, b, alternative="two-sided").statistic
    delta_from_u = 2 * u / (len(a) * len(b)) - 1
    assert abs(cliffs_delta(a, b) - delta_from_u) < 1e-6


def test_partial_spearman_reduces_association_under_a_real_confounder():
    """Controle parcialmente correlacionado: a parcial encolhe, mas continua finita."""
    rng = random.Random(21)
    z = [rng.gauss(0, 1) for _ in range(60)]
    x = [0.7 * zi + rng.gauss(0, 0.7) for zi in z]
    y = [0.7 * zi + rng.gauss(0, 0.7) for zi in z]
    full = spearman(x, y)
    partial = partial_spearman(x, y, z)
    assert -1.0 <= partial <= 1.0
    assert abs(partial) < abs(full)


def test_partial_spearman_returns_nan_when_control_is_collinear():
    """Contrato defensivo: com controle colinear o denominador zera e a funcao
    devolve NaN em vez de um numero sem sentido. H4 depende disso: se algum dia
    um proxy virar colinear com HDI, o pipeline precisa falhar visivelmente."""
    x, y = _sample(50, 21)
    z = list(x)                     # colinearidade perfeita
    assert math.isnan(partial_spearman(x, y, z))


def test_mann_kendall_sign_matches_direction():
    up = list(range(30))
    noise = [v + 0.01 * ((-1) ** v) for v in up]
    s_stat = mann_kendall(noise)[0] if isinstance(mann_kendall(noise), tuple) else mann_kendall(noise)
    assert s_stat > 0
