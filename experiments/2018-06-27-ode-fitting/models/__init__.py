"""
Rumor diffusion models

Contents
========

1. Hoax model by Tambuscio et al. (2018). See `hoaxmodel`.

2. Segregated Hoax model by Tambuscio et al. (2018). See `hoaxmodelseg`.

3. SIR (Susceptible-Infected-Recovered). See `sir`.

4. Double SIR (i.e., two independent SIR processes). See `sir`.

5. SEIZ (Susceptible-Exposed-Infected-Skeptic) by Jin et al. (2013). See
`seiz`.
"""

# TODO implement modules for the following:
#  1. The model by Bettencourt et al.
#  2. The DK model by Daley and Kendall (see review by Vespignani et al.)
#  3. The MT model by Maki and Thompson
#  4. The model by Nekovee et al. ("Theory of rumor spreading in complex social
#     networks")
#  5. The "Higgs rumor" model by De Domenico et al. (2013).
#  6. The "unified" spreading model by Ferraz de Arruda et al. (2016)

from models.base import *
from models.hoaxmodel import *
from models.seghoaxmodel import *
from models.sir import *
from models.seiz import *
from models.probhoaxmodel import *
