
#start iterations
it <- 1

#create counters for each tipology of vertices 
#(a matrix for all iterations where
#vba[it,t]=num of believer active nodes at time t in iteration it)
vba <- matrix(,nrow=num_iterations,ncol=time_end)
vfa <-matrix(,nrow=num_iterations,ncol=time_end)
vbi <- matrix(,nrow=num_iterations,ncol=time_end)
vfi <-matrix(,nrow=num_iterations,ncol=time_end)
vsus <- matrix(,nrow=num_iterations,ncol=time_end)

bi_max <- list()
t_maxbi <- list()
ba_max <- list()
t_maxba <- list()
fa_max <- list()
t_maxfa <- list()
fi_max <- list()
t_maxfi <- list()
sus_min <- list()
t_minsus <- list()

tot_inf <- list()
##
if(type=="communities"){
  vgba <- matrix(,nrow=num_iterations,ncol=time_end)
  vgfa <-matrix(,nrow=num_iterations,ncol=time_end)
  vgbi <- matrix(,nrow=num_iterations,ncol=time_end)
  vgfi <-matrix(,nrow=num_iterations,ncol=time_end)
  vgsus <- matrix(,nrow=num_iterations,ncol=time_end)
  ###
  vsba <- matrix(,nrow=num_iterations,ncol=time_end)
  vsfa <-matrix(,nrow=num_iterations,ncol=time_end)
  vsbi <- matrix(,nrow=num_iterations,ncol=time_end)
  vsfi <-matrix(,nrow=num_iterations,ncol=time_end)
  vssus <- matrix(,nrow=num_iterations,ncol=time_end)
  
  gbi_max <- list()
  t_maxgbi <- list()
  gba_max <- list()
  t_maxgba <- list()
  gfa_max <- list()
  t_maxgfa <- list()
  gfi_max <- list()
  t_maxgfi <- list()
  gsus_min <- list()
  t_mingsus <- list()
  
  sbi_max <- list()
  t_maxsbi <- list()
  sba_max <- list()
  t_maxsba <- list()
  sfa_max <- list()
  t_maxsfa <- list()
  sfi_max <- list()
  t_maxsfi <- list()
  ssus_min <- list()
  t_minssus <- list()
}


while(it <= num_iterations){
  print(it)

  #create the network
  #if there are skeptic/gullible set also the different gullibility
  if(type=="communities"){
    g <- create_network(N, M, segregation, gullible_size)
    V(g)[community==1]$verify=pv
    V(g)[community==2]$verify=0
  }
  else{
    if(type=="barabasi"){
      g <- barabasi.game(N, m=3, directed=FALSE) 
    }
    else if(type=="random"){
      g <- sample_gnm(N,M,directed=FALSE, loops=FALSE)
    }   
    V(g)$verify=pv
  }
  
  #initialize all nodes as SUSCEPTIBLE (blue)
  #V(g)$color="blue"
  V(g)$fa=0
  V(g)$ba=0
  V(g)$fi=0
  V(g)$bi=0
  V(g)$sus=1
  
  tot_infected <-0
  
  #initialize FACT-CHECKERS INACTIVE (orange) choosing them randomly
  if(fi_init){
    for (ir in 1:fi_init) {
      rv=round(runif(1,1,N))
      while(V(g)[rv]$fi){  
        rv=round(runif(1,1,N))
      }
      #V(g)[rv]$color="orange"
      V(g)[rv]$fi=1
      V(g)[rv]$sus=0
    }
  }
  
  #initialize BELIEVERS ACTIVE (green) choosing them randomly
  if(ba_init){
    for (ig in 1:ba_init) {
      rv <- round(runif(1,1,N))  
      while(V(g)[rv]$ba | V(g)[rv]$fi){  
        rv=round(runif(1,1,N))
      }
      #V(g)[rv]$color="forestgreen"
      V(g)[rv]$fi=0
      V(g)[rv]$ba=1
      V(g)[rv]$sus=0 
    }
  }
  
  
  #initialize time
  time <- time_init
  while(time <= time_end){    
    print(time)
    
    #create a copy of the graph
    g_aux <- g
    
    #random numbers
    V(g)$u1=runif(N,0,1)
    V(g)$u2=runif(N,0,1)
    
    #debate
    V(g)$neighbors=neighborhood.size(g,V(g))- 1 #number of neighbors
    V(g)$neighb_list=neighborhood(g,V(g)) #lists of neighbors
    V(g)$n_list <- lapply(V(g)$neighb_list, function(x) x[-1]) #remove node itself
    V(g)$ba_neighbors <- unlist(lapply(V(g)$n_list, function(x) sum(x$ba))) #count BA neighbors of a node
    V(g)$debate <- V(g)$ba_neighbors/V(g)$neighbors
    
    #spreading functions
    V(g)$f=alpha*V(g)$debate
    V(g)$g=(1-alpha)*V(g)$debate
    
    
    #BELIEVER ACTIVE
    ba_nodes= subset(V(g),V(g)$ba==1)
    
    #... TO BELIEVER INACTIVE
    ba_to_bi = subset(ba_nodes, (ba_nodes$u1<tau))
    #select the remaining ba nodes
    ba_nodes=subset(ba_nodes, (ba_nodes$u1)>=tau)
    #...TO FACT-CHECKER INACTIVE
    ba_to_fi = subset(ba_nodes, ba_nodes$u2 < ba_nodes$verify)
    #select the remaining ba nodes
    ba_nodes=subset(ba_nodes,ba_nodes$u2 >= ba_nodes$verify)
    #... stay BELIEVER ACTIVE
    ba_to_ba = ba_nodes
    
    
    #update in g_aux      
    V(g_aux)[ba_to_bi]$fa=0
    V(g_aux)[ba_to_bi]$ba=0
    V(g_aux)[ba_to_bi]$fi=0
    V(g_aux)[ba_to_bi]$bi=1
    V(g_aux)[ba_to_bi]$sus=0
    
    V(g_aux)[ba_to_fi]$fa=0
    V(g_aux)[ba_to_fi]$ba=0
    V(g_aux)[ba_to_fi]$fi=1
    V(g_aux)[ba_to_fi]$bi=0
    V(g_aux)[ba_to_fi]$sus=0
    
    V(g_aux)[ba_to_ba]$fa=0
    V(g_aux)[ba_to_ba]$ba=1
    V(g_aux)[ba_to_ba]$fi=0
    V(g_aux)[ba_to_ba]$bi=0
    V(g_aux)[ba_to_ba]$sus=0
    
    #FACT-CHECKER ACTIVE
    fa_nodes= subset(V(g),V(g)$fa==1)  
    
    #... TO FACT-CHECKER INACTIVE
    fa_to_fi = subset(fa_nodes, fa_nodes$u1<tau)
    #... stay FACT_CHECKER ACTIVE
    fa_to_fa = subset(fa_nodes, fa_nodes$u1>=tau)
    
    
    #update in g_aux      
    V(g_aux)[fa_to_fi]$fa=0
    V(g_aux)[fa_to_fi]$ba=0
    V(g_aux)[fa_to_fi]$fi=1
    V(g_aux)[fa_to_fi]$bi=0
    V(g_aux)[fa_to_fi]$sus=0
    
    V(g_aux)[fa_to_fa]$fa=1
    V(g_aux)[fa_to_fa]$ba=0
    V(g_aux)[fa_to_fa]$fi=0
    V(g_aux)[fa_to_fa]$bi=0
    V(g_aux)[fa_to_fa]$sus=0
    
    
    #BELIEVER INACTIVE
    bi_nodes= subset(V(g),V(g)$bi==1) 
    
    #... TO FACT-CHECKER INACTIVE
    bi_to_fi = subset(bi_nodes, bi_nodes$u1 < bi_nodes$verify)
    #select the remaining ba nodes
    bi_nodes=subset(bi_nodes, bi_nodes$u1 >= bi_nodes$verify)
    #...TO BELIEVER ACTIVE
    bi_to_ba = subset(bi_nodes, bi_nodes$u2 < bi_nodes$debate)
    #select the remaining ba nodes
    bi_nodes=subset(bi_nodes,bi_nodes$u2 >= bi_nodes$debate)   
    #... stay BELIEVER INACTIVE
    bi_to_bi = bi_nodes
    
    #update in g_aux      
    V(g_aux)[bi_to_fi]$fa=0
    V(g_aux)[bi_to_fi]$ba=0
    V(g_aux)[bi_to_fi]$fi=1
    V(g_aux)[bi_to_fi]$bi=0
    V(g_aux)[bi_to_fi]$sus=0
    
    V(g_aux)[bi_to_ba]$fa=0
    V(g_aux)[bi_to_ba]$ba=1
    V(g_aux)[bi_to_ba]$fi=0
    V(g_aux)[bi_to_ba]$bi=0
    V(g_aux)[bi_to_ba]$sus=0
    
    V(g_aux)[bi_to_bi]$fa=0
    V(g_aux)[bi_to_bi]$ba=0
    V(g_aux)[bi_to_bi]$fi=0
    V(g_aux)[bi_to_bi]$bi=1
    V(g_aux)[bi_to_bi]$sus=0
    
    #FACT-CHECKER INACTIVE
    fi_nodes= subset(V(g),V(g)$fi==1)
    
    #... TO FACT-CHECKER ACTIVE
    fi_to_fa = subset(fi_nodes, fi_nodes$u1 < fi_nodes$debate)
    #select the remaining ba nodes
    fi_nodes=subset(fi_nodes, fi_nodes$u1 >= fi_nodes$debate)
    #... stay FACT-CHECKER INACTIVE
    fi_to_fi = fi_nodes
    
    #update in g_aux      
    V(g_aux)[fi_to_fa]$fa=1
    V(g_aux)[fi_to_fa]$ba=0
    V(g_aux)[fi_to_fa]$fi=0
    V(g_aux)[fi_to_fa]$bi=0
    V(g_aux)[fi_to_fa]$sus=0
    
    V(g_aux)[fi_to_fi]$fa=0
    V(g_aux)[fi_to_fi]$ba=0
    V(g_aux)[fi_to_fi]$fi=1
    V(g_aux)[fi_to_fi]$bi=0
    V(g_aux)[fi_to_fi]$sus=0
    
    #SUSCEPTIBLE
    sus_nodes=subset(V(g),V(g)$sus==1)  
    
    # ... to BELIEVER INACTIVE
    sus_to_bi = subset(sus_nodes, sus_nodes$u1 < sus_nodes$f)
    #select the remaining ba nodes
    sus_nodes = subset(sus_nodes, sus_nodes$u1 >= sus_nodes$f)
    # ...to FACT-CHECKER INACTIVE
    sus_to_fi = subset(sus_nodes, sus_nodes$u1 < (sus_nodes$f + sus_nodes$g))
    #select the remaining ba nodes
    sus_nodes = subset(sus_nodes, sus_nodes$u1 >= (sus_nodes$f + sus_nodes$g))
    # ... stay SUSCEPTIBLE
    sus_to_sus = sus_nodes
    
    #update in g_aux  
    V(g_aux)[sus_to_bi]$fa=0
    V(g_aux)[sus_to_bi]$ba=0
    V(g_aux)[sus_to_bi]$fi=0
    V(g_aux)[sus_to_bi]$bi=1
    V(g_aux)[sus_to_bi]$sus=0
    
    V(g_aux)[sus_to_fi]$fa=0
    V(g_aux)[sus_to_fi]$ba=0
    V(g_aux)[sus_to_fi]$fi=1
    V(g_aux)[sus_to_fi]$bi=0
    V(g_aux)[sus_to_fi]$sus=0
    
    V(g_aux)[sus_to_sus]$fa=0
    V(g_aux)[sus_to_sus]$ba=0
    V(g_aux)[sus_to_sus]$fi=0
    V(g_aux)[sus_to_sus]$bi=0
    V(g_aux)[sus_to_sus]$sus=1
    
    
    #store the sizes of the compartments 
    
    vfa[it,time]<-sum(V(g_aux)$fa)
    vba[it,time]<-sum(V(g_aux)$ba)
    vfi[it, time]<-sum(V(g_aux)$fi)
    vbi[it,time]<-sum(V(g_aux)$bi)
    vsus[it, time]<-sum(V(g_aux)$sus)
    
    if(type=="communities"){
      gull <- V(g_aux)[community==2]
      skep <- V(g_aux)[community==1]
      
      vgba[it,time]=sum(gull$ba)
      vgfa[it,time]=sum(gull$fa)
      vgbi[it,time]=sum(gull$bi)
      vgfi[it,time]=sum(gull$fi)
      vgsus[it,time]=sum(gull$sus)
      
      vsba[it,time]=sum(skep$ba)
      vsfa[it,time]=sum(skep$fa)
      vsbi[it,time]=sum(skep$bi)
      vsfi[it,time]=sum(skep$fi)
      vssus[it,time]=sum(skep$sus)
    }
      
    #copy the new graph obtained
    g <- g_aux
    
    #increase time  
    time <- time+timestep    
  }
  
  bi_max[it] <- max(vbi[it, ])
  t_maxbi[it] <- which.max (vbi[it, ])
  ba_max[it] <- max(vba[it, ])
  t_maxba[it] <- which.max (vba[it, ])
  fa_max[it] <- max(vfa[it, ])
  t_maxfa[it] <- which.max (vfa[it, ])
  fi_max[it] <- max(vfi[it, ])
  t_maxfi[it] <- which.max (vfi[it, ])
  sus_min[it] <- min(vsus[it, ])
  t_minsus[it] <- which.min (vsus[it, ])
  
  if(type=="communities"){
    gbi_max[it] <- max(vgbi[it, ])
    t_maxgbi[it] <- which.max (vgbi[it, ])
    gba_max[it] <- max(vgba[it, ])
    t_maxgba[it] <- which.max (vgba[it, ])
    gfa_max[it] <- max(vgfa[it, ])
    t_maxgfa[it] <- which.max (vgfa[it, ])
    gfi_max[it] <- max(vgfi[it, ])
    t_maxgfi[it] <- which.max (vgfi[it, ])
    gsus_min[it] <- min(vgsus[it, ])
    t_mingsus[it] <- which.min (vgsus[it, ])
    
    sbi_max[it] <- max(vsbi[it, ])
    t_maxsbi[it] <- which.max (vsbi[it, ])
    sba_max[it] <- max(vsba[it, ])
    t_maxsba[it] <- which.max (vsba[it, ])
    sfa_max[it] <- max(vsfa[it, ])
    t_maxsfa[it] <- which.max (vsfa[it, ])
    sfi_max[it] <- max(vsfi[it, ])
    t_maxsfi [it] <- which.max (vsfi[it, ])
    ssus_min[it] <- min(vssus[it, ])
    t_minssus[it] <- which.min (vssus[it, ])
  }
  
  #increase iterations
  it <- it +1
  
}########---END OF SPREADING PROCESS---########


###---PLOT the averaged behavior over time ---###
cat('Do you want to plot dynamic? ("y"=yes) >')
b <-  scan("", what="string",n=1)

if(b=='y'){
  t <- seq(time_init, time_end, timestep)
  
  mean_vba <-list()
  mean_vfa <-list()
  mean_vbi <-list()
  mean_vfi <-list()
  mean_vsus <-list()
  
  for(k in t){
    mean_vba[k] <- mean(vba[,k],trim=0)
    mean_vfa[k] <- mean(vfa[,k],trim=0)
    mean_vbi[k] <- mean(vbi[,k],trim=0)
    mean_vfi[k] <- mean(vfi[,k],trim=0)
    mean_vsus[k] <- mean(vsus[,k],trim=0)
  }
  source("hoaxspread_plot_dynamics.R")
  xx<-"TOT"
  plot_dynamics(xx, t, mean_vba, mean_vfa, mean_vbi, mean_vfi, mean_vsus)
  
  #if there are communities
  #plot averaged behaviors for gullible and skeptic groups
  if(type=="communities"){
    cat('Do you want to plot dynamics for gullible and skeptic group? ("y"=yes) >')
    bb <- scan("", what="string",n=1)
    
    if(bb=='y'){
      
      mean_vgba <-list()
      mean_vgfa <-list()
      mean_vgbi <-list()
      mean_vgfi <-list()
      mean_vgsus <-list()
      
      mean_vsba <-list()
      mean_vsfa <-list()
      mean_vsbi <-list()
      mean_vsfi <-list()
      mean_vssus <-list()
      
      for(k in t){
        mean_vgba[k] <- mean(vgba[,k],trim=0)
        mean_vgfa[k] <- mean(vgfa[,k],trim=0)
        mean_vgbi[k] <- mean(vgbi[,k],trim=0)
        mean_vgfi[k] <- mean(vgfi[,k],trim=0)
        mean_vgsus[k] <- mean(vgsus[,k],trim=0)
        
        mean_vsba[k] <- mean(vsba[,k],trim=0)
        mean_vsfa[k] <- mean(vsfa[,k],trim=0)
        mean_vsbi[k] <- mean(vsbi[,k],trim=0)
        mean_vsfi[k] <- mean(vsfi[,k],trim=0)
        mean_vssus[k] <- mean(vssus[,k],trim=0)
      }
      
      xx<-"GUL"
      plot_dynamics(xx, t, mean_vgba, mean_vgfa, mean_vgbi, mean_vgfi, mean_vgsus)
      xx<-"SK"
      plot_dynamics(xx, t, mean_vsba, mean_vsfa, mean_vsbi, mean_vsfi, mean_vssus)
    }
  }
}

#SAVE OUTPUT in a file
path=getwd()
if(type=="communities"){
  path=getwd()
  namefile=paste(path,"/SEG_N",N,"alpha",alpha,"_verifySK",pv,"_seg",
                 segregation,"_gulsize",gullible_size,"_tau",tau,
                 "_bainit",ba_init,"_fiinit",fi_init,"_ave",
                 num_iterations,"it.RData", sep="")
  save(g, t, num_iterations, N,M, alpha, tau, pv,
       segregation, gullible_size,ba_init,fi_init, 
       mean_vba, mean_vfa, mean_vbi, mean_vfi, mean_vsus, 
       vba, vfa, vbi, vfi, vsus, 
       mean_vgba, mean_vgfa, mean_vgbi, mean_vgfi, mean_vgsus, 
       vgba, vgfa, vgbi, vgfi, vgsus, 
       mean_vsba, mean_vsfa, mean_vsbi, mean_vsfi, mean_vssus, 
       vsba, vsfa, vsbi, vsfi, vssus, 
       tot_inf, 
       bi_max, t_maxbi, ba_max, t_maxba, fi_max, t_maxfi, fa_max, t_maxfa, sus_min, t_minsus,
       gbi_max, t_maxgbi, gba_max, t_maxgba, gfi_max, t_maxgfi, gfa_max, t_maxgfa, gsus_min, t_mingsus,
       sbi_max, t_maxsbi, sba_max, t_maxsba, sfi_max, t_maxsfi, sfa_max, t_maxsfa, ssus_min, t_minssus,
       file = namefile, envir = parent.frame())
  save.image()
}else{
  path=getwd()
  namefile=paste(path,"/NOSEG_N",N,"alpha",alpha,"_verify",pv,"_tau",tau,
                 "_bainit",ba_init,"_fiinit",fi_init,"_ave",num_iterations,"it.RData", sep="")
  save(g, t, num_iterations, N,M, alpha, tau, pv, 
       mean_vba, mean_vfa, mean_vbi, mean_vfi, mean_vsus, 
       vba, vfa, vbi, vfi, vsus, 
       tot_inf, 
       bi_max, t_maxbi, ba_max, t_maxba, fi_max, t_maxfi, fa_max, t_maxfa, sus_min, t_minsus,
       file = namefile, envir = parent.frame())
  save.image()
}








