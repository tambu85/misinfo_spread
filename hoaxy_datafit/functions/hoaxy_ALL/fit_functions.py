# ------------------------------------
# Mean-field model with no segregation
# ------------------------------------

def fit_mf_noseg(T_double, alpha, ONEoverN, ba_init, bi_init, fa_init, fi_init, pv, omega):
    T = T_double[:len(T_double)/2]
    BA, FA = mf_noseg(T, alpha, ONEoverN, ba_init, bi_init, fa_init, fi_init, pv, omega)
    return np.append(BA, FA)


# ---------------------------------
# Mean-field model with segregation
# ---------------------------------

def fit_mf_seg(T_double, alphag, alphas, ONEoverN, ba_init, bi_init, fa_init, fi_init, pvg, pvs, omega, gulsize, s):
    T = T_double[:len(T_double)/2]
    BA, FA = mf_seg(T, alphag, alphas, ONEoverN, ba_init, bi_init, fa_init, fi_init, pvg, pvs, omega, gulsize, s)
    return np.append(BA, FA)

# ------------------------------------------------------------------
# Mean-field model with segregation and no b_init in skeptic cluster
# ------------------------------------------------------------------

def fit_mf_seg_emptyskep(T_double, alphag, alphas, ONEoverN, ba_init_g, bi_init_g, pvg, pvs, omega, gulsize, s):
    T = T_double[:len(T_double)/2]
    BA, FA = mf_seg(T, alphag, alphas, ONEoverN, ba_init_g, bi_init_g, pvg, pvs, omega, gulsize, s)
    return np.append(BA, FA)


