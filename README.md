#misinfo_spread

Simulation of a hoax spreading process through a network

BEFORE RUNNING:
1.Set the working directory as the sources location directory 
2. Create 2 directorues in it: "plot" and "results"

>> FILE hoax_spread_main
Set the parameters 
"type" represents the chosen topology of network among the options:
a) "communities" : a network with two communities, gullible and skeptics >> in this case you have to set segregation, gullible (size), alpha_skeptical, alpha_gullible
b) "barabasi" : scale-free, barabasi-albert network (inside the file spreading_hoax it is possible to change the parameters of creation)
c) "random" : random network, given N and M

NOTE: when type="barabasi" or "random" there is a unique alpha for all the vertices, 
and it is the parameter "alpha_skeptical"

>> FILE spreading_hoax
realize the simulation on the chosen network with the given parameters
then ask if the user want to plot dynamics of the states BELIEVER, FACT-CHECKERS, SUSCEPTIBLE
finally save the data in a ".RData" file in the subfolder "results"

