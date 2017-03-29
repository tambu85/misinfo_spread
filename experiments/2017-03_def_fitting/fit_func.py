from mod_func import mf_noseg,mf_seg
import numpy as np

def fit_mf_noseg(T_double, alpha, ONEoverN, ba_init, bi_init, fa_init, fi_init, pv, tau):
    #(T,alpha,ONEoverN, ba_init, bi_init, pv, tau)
    T = T_double[:len(T_double)/2]
    BA, FA = mf_noseg(T, alpha, ONEoverN, ba_init, bi_init, fa_init, fi_init, pv, tau)
    return np.append(BA, FA)


def fit_mf_seg(T_double, alpha, ONEoverN, ba_init, bi_init, fa_init, fi_init, pvg, pvs, tau, gulsize, seg):
    T = T_double[:len(T_double)/2]
    BA, FA = mf_seg(T, alpha, ONEoverN, ba_init, bi_init,fa_init, fi_init,pvg, pvs, tau, gulsize, seg)
    return np.append(BA, FA)
