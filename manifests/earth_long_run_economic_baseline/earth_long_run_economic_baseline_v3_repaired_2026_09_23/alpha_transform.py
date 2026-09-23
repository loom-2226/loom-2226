"""Universal boundary-continuous sector Cobb–Douglas alpha experiment."""
import math


def transform(A_original, alpha_original, capital, labor, alpha_ceiling):
    """Return (effective alpha, rebased A, capped, multiplicative A factor).

    The source runner uses Y = T*A*K**alpha*L**(1-alpha) at sector level.
    K and L are the *frozen 2060* sector capital and employment, before the
    2061 asset rollforward or labor reallocation. T cancels in this rebase.
    """
    if alpha_ceiling is None or alpha_original <= alpha_ceiling:
        return alpha_original, A_original, False, 1.0
    if not (math.isfinite(alpha_ceiling) and 0.0 < alpha_ceiling < 1.0):
        raise ValueError('alpha ceiling must be strictly between zero and one')
    if not (math.isfinite(capital) and math.isfinite(labor) and capital > 0 and labor > 0):
        raise ValueError('positive finite frozen sector capital and labor required')
    if not (math.isfinite(A_original) and A_original >= 0):
        raise ValueError('finite nonnegative sector A required')
    effective = alpha_ceiling
    factor = math.exp((alpha_original-effective)*(math.log(capital)-math.log(labor)))
    rebased = A_original*factor
    if not math.isfinite(factor) or not math.isfinite(rebased):
        raise ValueError('nonfinite alpha continuity rebase')
    return effective, rebased, True, factor
