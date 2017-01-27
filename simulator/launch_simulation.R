
#IMPORTANT set the working directory as the sources location directory!
#setwd("****")
#and then create two subfolders, "plot" and "results"

library("igraph")

#set parameters
N <- 100 #net size
M <- 294 #number edges
type <- "communities" #parameter to set net type among ["communities","barabasi","random"]
time_init <- 1
time_end <- 100
timestep <- 1 #time step 
fi_init <- 0 #number of fact-checkers at t=0
ba_init <- 0.1*N #number of believers at t=0
num_iterations <-3 #number of iterations
gullible_size <- N/2 #size of gullible group
segregation <- 0.6 #segregation value in [0.5,1]
tau <- 0.1 #activity decay
alpha <- 0.6 #credibility
pv <- 0.05 #verifying probability (global or for skeptic group when type=communities, since for gullible it is set to 0)
#SPREADING PROCESS WITH COMMUNITIES
source("hoaxspread_create_net.R")
source("hoaxspread_process.R")
