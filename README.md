# misinfo_spread

Simulation model of a hoax-spreading process over a network.

## Instructions

1.  Set the working directory as the sources location directory 

2.  Create 2 directories in it: "plot" and "results"

3.  Set the parameters of the simulation in `launch_simulation`. In particular
   the `type` represents the topology of network. The following the options are
   available:
    
    * `communities`: a network with two communities, gullible and skeptics:
      in this case user has to set `segregation`, `gullible` (size),
      `alpha_skeptical`, and `alpha_gullible`.

    * `barabasi`: use scale-free, Barabási-Albert network (see file
      `spreading_hoax` for its creation parameters). In this case all agents
      share the same value of alpha (`alpha_skeptical`).

    * `random` : random network, given parameters `N` and `M`. The value of
      alpha is the same for all agents (`alpha_skeptical`).

4.  Run the script `launch_simulation`. It will perform the simulation on the
    chosen network with the given parameters and then ask if the user wants to
    plot the dynamics of the BELIEVER, FACT-CHECKERS, and SUSCEPTIBLE
    compartments. Finally it saves the data in a ".RData" file in the subfolder
    "results"
