# misinfo_spread

Simulation model of a hoax-spreading process over a network.

## Instructions

1.  Set the working directory as the sources location directory 

2. Set the parameters of the simulation in `launch_simulation.R`. In particular
   the `type` represents the topology of network. The following the options are
   available:
    
    * `communities`: a network with two communities, gullible and skeptics:
      in this case user has to set `segregation`, `gullible_size` (size of the gullible group),
      and `pv`, that in this case is the verifying probability for the skeptic group, 
      since for the gullible it is set authomatically to 0.

    * `barabasi`: use scale-free, Barabási-Albert network (see file
      `hoaxspread_process`, line 76, for its creation parameters). In this case all agents
      share the same value of verifying probaility (`pv`).

    * `random` : random network, given parameters `N` and `M`(see file
      `hoaxspread_process`, line 79, for its creation parameters). In this case all agents
      share the same value of verifying probaility (`pv`).

4.  Run the script `launch_simulation.R`. It will perform the simulation on the
    chosen network with the given parameters and then ask if the user wants to
    plot the dynamics of the (ACTIVE/INACTIVE) BELIEVER, (ACTIVE/INACTIVE) FACT-CHECKERS, and SUSCEPTIBLE
    compartments. Finally it saves the data in a ".RData" file.
