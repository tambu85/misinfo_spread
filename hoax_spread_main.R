

setwd(file.path("~","Desktop","Dropbox","bozze virus","mySimulation","codici"))
library("igraph")

# parameters
N <- 100 #net size
M <- 294 #number edges
type <- "communities" #parameter to set net type among ["communities","barabasi","random"]
time_init=1
time_end=20
tau=1 #time step 
red_init=0 #number of fact-checkers at t=0
green_init=2 #number of believers at t=0
beta <- 0.5 #spreading rate
num_iterations <-2 #number of iterations
gullible <- N/2 #size of gullible group
segregation <- 0.6 #segregation value in [0.5,1]
p_forget <- 0.1 #forgetting probability
alpha_skeptical=0.05 #alpha skeptic group (or alpha, in case of barabasi/random with no communities)
alpha_gullible=0.7 #alpha gullible group

#SPREADING PROCESS WITH COMMUNITIES
source("spreading_hoax.R")







