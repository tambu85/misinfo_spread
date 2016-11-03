#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
from scipy.optimize import curve_fit
import scipy, scipy.integrate

#our model without segregation (random network)
def mf_noseg(T,tfact, a,netsize, ba_init,verify, dec):

    ba=[]
    fa=[]
    alpha=a
    pv=verify

    N=netsize
    tau=dec
    pBI0=0.0
    pBA0=ba_init
    pFI0=0.0
    pFA0=0.0
    pS0=1.-(pFA0+pFI0+pBA0+pBI0)

    T_sim = np.arange(min(T), max(T) + tfact, tfact)

    for j in range(0, len(T_sim)):
        T_sim[j] = round(T_sim[j], 5)

    T_sim = np.sort(np.append(T_sim, T))
    T_sim_sorted = np.unique(T_sim)

    ba_cum=0

    for i in T_sim_sorted:

        if (i in T):
            ab = int(float(pBA0) * N)
            print(ba_cum)
            ba_cum = ab + ba_cum
            ba.append(ba_cum)

        f = pBA0
        pBI1 = alpha * f * pS0 + (1. / tau) * pBA0 + (1. - pv) * (1. - f) * pBI0
        pBA1 = (1. - pv) * f  * pBI0 + (1. - (1. / tau)) * (1. - pv) * pBA0
        pFI1 = (1-alpha) * f * pS0 + (1. / tau) * pFA0 + pv * (pBI0 + (1. - 1. / tau) * pBA0) + (1 - f) * pFI0
        pFA1 = f * pFI0 + (1. - 1. / tau) * pFA0
        pS1 = (1. - f) * pS0

        #update
        pBI0 = pBI1
        pBA0 = pBA1
        pFI0 = pFI1
        pFA0 = pFA1
        pS0 = pS1

        if float(pBI0)<=0.0000000001:
            pBI0=0.0
        if float(pBA0)<=0.0000000001:
            pBA0=0.0
        if float(pFI0)<=0.0000000001:
            pFI0=0.0
        if float(pFA0)<=0.0000000001:
            pFA0=0.0
        if float(pS0)<=0.0000000001:
            pS0=0.0

    return (np.asarray(ba))

def mf_noseg_plot(T, a,netsize, ba_init,verify, dec):

    ba=[]
    alpha=a
    pv=verify
    N=netsize
    tau=dec

    pBI0=0.0
    pBA0=ba_init
    pFI0=0.0
    pFA0=0.0
    pS0=1.-(pFA0+pFI0+pBA0+pBI0)
    ba_cum=0

    for i in T:

        ab = int(float(pBA0) * N)
        ba_cum=ab+ba_cum
        ba.append(ba_cum)

        f = pBA0
        pBI1 = alpha * f * pS0 + (1. / tau) * pBA0 + (1. - pv) * (1. - f) * pBI0
        pBA1 = (1. - pv) * f  * pBI0 + (1. - (1. / tau)) * (1. - pv) * pBA0
        pFI1 = (1-alpha) * f * pS0 + (1. / tau) * pFA0 + pv * (pBI0 + (1. - 1. / tau) * pBA0) + (1 - f) * pFI0
        pFA1 = f * pFI0 + (1. - 1. / tau) * pFA0
        pS1 = (1. - f) * pS0

        #update
        pBI0 = pBI1
        pBA0 = pBA1
        pFI0 = pFI1
        pFA0 = pFA1
        pS0 = pS1

        if float(pBI0)<=0.0000000001:
            pBI0=0.0
        if float(pBA0)<=0.0000000001:
            pBA0=0.0
        if float(pFI0)<=0.0000000001:
            pFI0=0.0
        if float(pFA0)<=0.0000000001:
            pFA0=0.0
        if float(pS0)<=0.0000000001:
            pS0=0.0

    return (np.asarray(ba))


#our model with segregation (two clusters gullible-skeptic)
def mf_seg(T,tfact,a,netsize, gulsize, ba_init,verify_sk,segregation, dec):

    b=[]
    fa=[]
    alpha=a
    s=segregation
    pvg=0.
    pvsk=verify_sk
    gullible_size=gulsize*netsize
    N=netsize
    skeptic_size=N-gullible_size
    tau=dec
    pBI0g=0.0
    pBA0g=ba_init
    pFI0g=0.0
    pFA0g=0.0
    pS0g=1.-(pFA0g+pFI0g+pBA0g+pBI0g)
    pBI0sk=0.0
    pBA0sk=ba_init
    pFI0sk=0.0
    pFA0sk=0.0
    pS0sk=1.-(pFA0sk+pFI0sk+pBA0sk+pBI0sk)

    T_sim=np.arange(min(T),max(T)+tfact,tfact)

    for j in range(0,len (T_sim)):
        T_sim[j]=round(T_sim[j],5)

    T_sim=np.sort(np.append(T_sim,T))
    T_sim_sorted=np.unique(T_sim)

    b_cum=0

    for i in T_sim_sorted:

        if(i in T):

            baG = int(float(pBA0g) * gullible_size)
            baSK = int(float(pBA0sk) * skeptic_size)
            b_tot = baG + baSK
            b_cum = b_cum + b_tot
            b.append(b_cum)


        fg=s*pBA0g+(1-s)*pBA0sk
        if(i>0):
            pFI1g=(1.-alpha)*fg*pS0g+(1./tau)*pFA0g+pvg*(pBI0g+(1.-1./tau)*pBA0g)+(1.-fg)*pFI0g
            pBI1g = alpha * fg * pS0g + (1. / tau) * pBA0g + (1. - pvg) * (1. - fg) * pBI0g
            pBA1g = (1. - pvg) * fg * pBI0g + (1. - (1. / tau)) * (1. - pvg) * pBA0g
        else:
            pFI1g = (1. - alpha) * fg * pS0g + (1. / tau) * pFA0g  + (1. - fg) * pFI0g
            pBI1g = alpha * fg * pS0g + (1. / tau) * pBA0g +  (1. - fg) * pBI0g
            pBA1g =  fg * pBI0g + (1. - (1. / tau)) * pBA0g
        pFA1g=fg*pFI0g+(1.-1./tau)*pFA0g
        pS1g=(1.-fg)*pS0g

        fsk=s*pBA0sk+(1-s)*pBA0g
        pBI1sk=alpha*fsk*pS0sk+(1./tau)*pBA0sk+(1.-pvsk)*(1.-fsk)*pBI0sk
        pBA1sk=(1.-pvsk)*fsk*pBI0sk+(1.-(1./tau))*(1.-pvsk)*pBA0sk
        pFI1sk=(1.-alpha)*fsk*pS0sk+(1./tau)*pFA0sk+pvsk*(pBI0sk+(1.-1./tau)*pBA0sk)+(1.-fsk)*pFI0sk
        pFA1sk=fsk*pFI0sk+(1.-1./tau)*pFA0sk
        pS1sk=(1.-fsk)*pS0sk

        #update
        pBI0g = pBI1g
        pBA0g = pBA1g
        pFI0g = pFI1g
        pFA0g = pFA1g
        pS0g = pS1g

        pBI0sk=pBI1sk
        pBA0sk=pBA1sk
        pFI0sk=pFI1sk
        pFA0sk=pFA1sk
        pS0sk=pS1sk

        if float(pBI0sk)<=0.0000000001:
            pBI0sk=0.0
        if float(pBA0sk)<=0.0000000001:
            pBA0sk=0.0
        if float(pFI0sk)<=0.0000000001:
            pFI0sk=0.0
        if float(pFA0sk)<=0.0000000001:
            pFA0sk=0.0
        if float(pS0sk)<=0.0000000001:
            pS0sk=0.0
        if float(pBI0g)<=0.0000000001:
	        pBI0g=0.0
		if float(pBA0g)<=0.0000000001:
			pBA0g=0.0
		if float(pFI0g)<=0.0000000001:
			pFI0g=0.0
		if float(pFA0g)<=0.0000000001:
			pFA0g=0.0
		if float(pS0g)<=0.0000000001:
			pS0g=0.0

    return (np.asarray(b))


def mf_seg_plot(T,a,netsize, gulsize, ba_init,verify_sk,segregation, dec):

    b=[]
    alpha=a
    s=segregation
    pvg=0.
    pvsk=verify_sk
    gullible_size=gulsize*netsize
    N=netsize
    skeptic_size=N-gullible_size
    tau=dec

    pBI0g=0.0
    pBA0g=ba_init
    pFI0g=0.0
    pFA0g=0.0
    pS0g=1.-(pFA0g+pFI0g+pBA0g+pBI0g)
    pBI0sk=0.0
    pBA0sk=ba_init
    pFI0sk=0.0
    pFA0sk=0.0
    pS0sk=1.-(pFA0sk+pFI0sk+pBA0sk+pBI0sk)
    b_cum=0

    for i in T:

        baG = int(float(pBA0g) * gullible_size)
        baSK = int(float(pBA0sk) * skeptic_size)
        b_tot = baG + baSK
        print(b_tot)
        b_cum = b_cum + b_tot
        print(b_cum)
        b.append(b_cum)


        fg=s*pBA0g+(1-s)*pBA0sk
        pBI1g=alpha*fg*pS0g+(1./tau)*pBA0g+(1.-pvg)*(1.-fg)*pBI0g
        pBA1g=(1.-pvg)*fg*pBI0g+(1.-(1./tau))*(1.-pvg)*pBA0g
        pFI1g=(1.-alpha)*fg*pS0g+(1./tau)*pFA0g+pvg*(pBI0g+(1.-1./tau)*pBA0g)+(1.-fg)*pFI0g
        pFA1g=fg*pFI0g+(1.-1./tau)*pFA0g
        pS1g=(1.-fg)*pS0g

        fsk=s*pBA0sk+(1-s)*pBA0g
        pBI1sk=alpha*fsk*pS0sk+(1./tau)*pBA0sk+(1.-pvsk)*(1.-fsk)*pBI0sk
        pBA1sk=(1.-pvsk)*fsk*pBI0sk+(1.-(1./tau))*(1.-pvsk)*pBA0sk
        pFI1sk=(1.-alpha)*fsk*pS0sk+(1./tau)*pFA0sk+pvsk*(pBI0sk+(1.-1./tau)*pBA0sk)+(1.-fsk)*pFI0sk
        pFA1sk=fsk*pFI0sk+(1.-1./tau)*pFA0sk
        pS1sk=(1.-fsk)*pS0sk

        #update
        pBI0g = pBI1g
        pBA0g = pBA1g
        pFI0g = pFI1g
        pFA0g = pFA1g
        pS0g = pS1g

        pBI0sk=pBI1sk
        pBA0sk=pBA1sk
        pFI0sk=pFI1sk
        pFA0sk=pFA1sk
        pS0sk=pS1sk

        if float(pBI0sk)<=0.0000000001:
            pBI0sk=0.0
        if float(pBA0sk)<=0.0000000001:
            pBA0sk=0.0
        if float(pFI0sk)<=0.0000000001:
            pFI0sk=0.0
        if float(pFA0sk)<=0.0000000001:
            pFA0sk=0.0
        if float(pS0sk)<=0.0000000001:
            pS0sk=0.0
        if float(pBI0g)<=0.0000000001:
	        pBI0g=0.0
		if float(pBA0g)<=0.0000000001:
			pBA0g=0.0
		if float(pFI0g)<=0.0000000001:
			pFI0g=0.0
		if float(pFA0g)<=0.0000000001:
			pFA0g=0.0
		if float(pS0g)<=0.0000000001:
			pS0g=0.0

    return (np.asarray(b))

#SIR model
def rhs(Y, t, beta, mu):

    S = Y[0]
    I = Y[1]
    R = Y[2]

    N = S + I + R

    dS = - beta * I * S / N
    dI = beta * I * S / N - mu * I
    dR = mu * I

    dY = [ dS, dI, dR ]

    return dY

def sir(T, bainit, mybeta, mymu, net_size):
    # Parameters
    beta = mybeta
    mu = mymu
    N=net_size

    ba=[]
    fa=[]

    S0 = 1. - bainit
    I0 = bainit
    R0 = 0.00

    Y0 = [S0, I0, R0]

    solution = scipy.integrate.odeint(rhs,Y0, T, args = (beta, mu))

    S = solution[:, 0]
    I = solution[:, 1]
    R = solution[:, 2]

    for k in range(len(I)):
        I[k] = int(float(I[k]) * net_size)
        S[k] = int(float(S[k]) * net_size)
        R[k] = int(float(R[k]) * net_size)

    return (np.asarray(I))

