import numpy as np


def mf_noseg(T, alpha, ONEoverN, ba_init, bi_init, fa_init, fi_init,
             pv, tau):
    """ Mean-field model with no segregation """

    # Network size
    N = 1. / ONEoverN

    # Initial conditions
    pBI0, pBA0, pFI0, pFA0, pS0 = N * bi_init, N * ba_init, N * fi_init,\
        N * fa_init, N * (1. - ba_init - bi_init - fi_init - fa_init)

    N0 = pBI0 + pBA0 + pFI0 + pS0
    assert np.allclose(N0, N), "Total number of agents does not "\
        "match N: {}".format(N0)

    ba = []
    fa = []

    for i in T:
        # print(i)
        ba.append(pBA0)
        fa.append(pFA0)

        f = pBA0/N

        pBI1 = alpha * f * pS0 + tau * pBA0 + (1. - pv) * (1 - f) * pBI0
        pBA1 = (1.-pv) * f * pBI0 + (1. - tau) * (1. - pv) * pBA0
        pFI1 = (1 - alpha) * f * pS0 + tau * pFA0 + pv * \
            (pBI0 + (1. - tau) * pBA0) + (1 - f) * pFI0
        pFA1 = f * pFI0 + (1. - tau) * pFA0
        pS1 = (1 - f) * pS0

        N1 = pBI1 + pBA1 + pFI1 + pS1
        assert np.allclose(N0, N1), "iteration: {}: Number of agents is not "\
            "conserved after update: {}".format(i, N1)

        pBI0, pBA0, pFI0, pFA0, pS0 = pBI1, pBA1, pFI1, pFA1, pS1

        if float(pBI0) <= 0.0000000001:
            pBI0 = 0.0
        if float(pBA0) <= 0.0000000001:
            pBA0 = 0.0
        if float(pFI0) <= 0.0000000001:
            pFI0 = 0.0
        if float(pFA0) <= 0.0000000001:
            pFA0 = 0.0
        if float(pS0) <= 0.0000000001:
            pS0 = 0.0

    return np.cumsum(np.asarray(ba)), np.cumsum(np.asarray(fa))


def mf_seg(T, alpha, ONEoverN, ba_init, bi_init, fa_init, fi_init, pvg, pvs,
           tau, gulsize, seg):
    """ Mean-field model with segregation (two clusters gullible-skeptic) """

    # Network size
    N = 1. / ONEoverN

    # Relative community size
    N_gullible = N * gulsize
    N_skeptic = N - N_gullible

    # Initial conditions
    # Gullible
    pBI0g, pBA0g, pFI0g, pFA0g, pS0g = N_gullible * bi_init, N_gullible *\
        ba_init, N_gullible * fi_init, N_gullible * fa_init, N_gullible *\
        (1. - (ba_init + bi_init + fa_init + fi_init))
    # Skeptical
    pBI0s, pBA0s, pFI0s, pFA0s, pS0s = N_skeptic * bi_init, N_skeptic * \
        ba_init, 0.0, 0.0, N_skeptic * (1. - (ba_init + bi_init))

    N0 = pBI0g + pBA0g + pFI0g + pS0g + pBI0s + pBA0s + pFI0s + pS0s
    assert np.allclose(N0, N), "Total number of agents does not "\
        "match N: {}".format(N0)

    ba = []
    fa = []

    for i in T:

        # update
        totBA = pBA0g + pBA0s
        ba.append(totBA)
        totFA = pFA0g + pFA0s
        fa.append(totFA)

        fg = seg * pBA0g / N_gullible * gulsize + (1. - seg) * pBA0s /\
            N_skeptic * (1 - gulsize)
        fs = seg * pBA0s / N_skeptic * (1 - gulsize) + (1. - seg) *\
            pBA0g / N_gullible * gulsize

        pBI1g = alpha * fg * pS0g + tau * pBA0g + (1. - pvg) * (1. - fg)\
            * pBI0g
        pBA1g = (1. - pvg) * fg * pBI0g + (1. - tau) * (1. - pvg) * pBA0g
        pFI1g = (1 - alpha) * fg * pS0g + tau * pFA0g + pvg * \
            (pBI0g + (1. - tau) * pBA0g) + (1 - fg) * pFI0g
        pFA1g = fg * pFI0g + (1. - tau) * pFA0g
        pS1g = (1. - fg) * pS0g

        pBI1s = alpha * fs * pS0s + tau * pBA0s + (1. - pvs) * (1. - fs)\
            * pBI0s
        pBA1s = (1. - pvs) * fs * pBI0s + (1. - tau) * (1. - pvs) * pBA0s
        pFI1s = (1 - alpha) * fs * pS0s + tau * pFA0s + pvs *\
            (pBI0s + (1. - tau) * pBA0s) + (1 - fs) * pFI0s
        pFA1s = fs * pFI0s + (1. - tau) * pFA0s
        pS1s = (1. - fs) * pS0s

        pBI0g, pBA0g, pFI0g, pFA0g, pS0g = pBI1g, pBA1g, pFI1g, pFA1g, pS1g
        pBI0s, pBA0s, pFI0s, pFA0s, pS0s = pBI1s, pBA1s, pFI1s, pFA1s, pS1s

        if float(pBI0s) <= 0.0000000001:
            pBI0s = 0.0
        if float(pBA0s) <= 0.0000000001:
            pBA0s = 0.0
        if float(pFI0s) <= 0.0000000001:
            pFI0s = 0.0
        if float(pFA0s) <= 0.0000000001:
            pFA0s = 0.0
        if float(pS0s) <= 0.0000000001:
            pS0s = 0.0

        if float(pBI0g) <= 0.0000000001:
            pBI0g = 0.0
        if float(pBA0g) <= 0.0000000001:
            pBA0g = 0.0
        if float(pFI0g) <= 0.0000000001:
            pFI0g = 0.0
        if float(pFA0g) <= 0.0000000001:
            pFA0g = 0.0
        if float(pS0g) <= 0.0000000001:
            pS0g = 0.0

    return np.cumsum(np.asarray(ba)), np.cumsum(np.asarray(fa))
