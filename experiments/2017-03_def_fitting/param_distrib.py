import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

list_of_files=listdir("/Users/marcella/PycharmProjects/hoaxy/data/")

path_file = "/Users/marcella/PycharmProjects/untitled/fit/fit_param_results/"

alphas = []
Nsizes = []
ab_init = []
ib_init = []
af_init = []
if_init = []
pv_guls = []
pv_skps = []
taus = []
gulsizes =[]
segs = []

for item in list_of_files:

    print(item)
    name_noseg = path_file + item + '_without_segregation_param.out'
    name_seg = path_file + item + '_with_segregation_param.out'

    lines=(line.rstrip('\n') for line in open(name_seg))
    alpha, ONEoverN, ba_init, bi_init, fa_init, fi_init, pvg, pvs, tau, gulsize, seg = lines

    print(round(float(seg),6))
    print(round(float(ba_init),6))

    alphas.append(round(float(alpha),6))
    Nsizes.append(round(1/float(ONEoverN),0))
    ab_init.append(round(float(ba_init),6))
    ib_init.append(round(float(bi_init), 6))
    af_init.append(round(float(fa_init), 6))
    if_init.append(round(float(fi_init), 6))
    pv_guls.append(round(float(pvg),6))
    pv_skps.append(round(float(pvs),6))
    taus.append(round(float(tau),6))
    gulsizes.append(round(float(gulsize),6))
    segs.append(round(float(seg),6))

plt.figure()
plt.hist(alphas)
plt.title("Credibility")
plt.xlabel("Alpha")
plt.ylabel("Frequency")
plt.savefig("PAR_alpha")

plt.figure()
plt.hist(ab_init)
plt.title("Active Believers (init)")
plt.xlabel("ab_init")
plt.ylabel("Frequency")
plt.savefig("PAR_abinit")

plt.figure()
plt.hist(ib_init)
plt.title("Inactive Believers (init)")
plt.xlabel("ib_init")
plt.ylabel("Frequency")
plt.savefig("PAR_ibinit")

plt.figure()
plt.hist(af_init)
plt.title("Active Fact-Checkers (init)")
plt.xlabel("af_init")
plt.ylabel("Frequency")
plt.savefig("PAR_afinit")

plt.figure()
plt.hist(if_init)
plt.title("Inactive Fact-Checkers (init)")
plt.xlabel("if_init")
plt.ylabel("Frequency")
plt.savefig("PAR_ifinit")

plt.figure()
plt.hist(pv_guls)
plt.title("Verify Prob GULLIBLE")
plt.xlabel("pv_gul")
plt.ylabel("Frequency")
plt.savefig("PAR_pvg")

plt.figure()
plt.hist(pv_skps)
plt.title("Verify Prob SKEPTIC")
plt.xlabel("pv_sk")
plt.ylabel("Frequency")
plt.savefig("PAR_pvsk")

plt.figure()
plt.hist(segs)
plt.title("Segregation")
plt.xlabel("seg")
plt.ylabel("Frequency")
plt.savefig("PAR_seg")

plt.figure()
plt.hist(Nsizes)
plt.title("Network Size")
plt.xlabel("Size")
plt.ylabel("Frequency")
plt.savefig("PAR_netsize")

plt.figure()
plt.hist(taus)
plt.title("Tau (deactivation)")
plt.xlabel("tau")
plt.ylabel("Frequency")
plt.savefig("PAR_tau")

plt.figure()
plt.hist(gulsizes)
plt.title("Gullible Size")
plt.xlabel("gsize")
plt.ylabel("Frequency")
plt.savefig("PAR_gsize")



