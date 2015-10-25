###### SPREADING PROCESS ######

###function to create the network###
#spread_hoax <- function(type,N,M,time_init,time_end,tau,red_init, green_init,beta, num_iterations, gullible, segregation, p_forget, alpha_skeptical, alpha_gullible){

#start iterations
it <- 1

#create counter for red, green, blue vertices (a matrix for all iterations vred[it,t]=num of red nodes at time t in iteration it)
vred <- matrix(,nrow=num_iterations,ncol=time_end)
vgreen <-matrix(,nrow=num_iterations,ncol=time_end)
vblue <- matrix(,nrow=num_iterations,ncol=time_end)

if(type=="communities"){
gullible_green <- matrix(,nrow=num_iterations,ncol=time_end)
gullible_red <- matrix(,nrow=num_iterations,ncol=time_end)
gullible_blue <- matrix(,nrow=num_iterations,ncol=time_end)

skeptic_green <- matrix(,nrow=num_iterations,ncol=time_end)
skeptic_red <- matrix(,nrow=num_iterations,ncol=time_end)
skeptic_blue <- matrix(,nrow=num_iterations,ncol=time_end)
}

while(it <= num_iterations){
  
  print(it)
  
  #create the network
  #if there are skeptic/gullible set also the different gullibility
  if(type=="communities"){
    source("create_graph_communities.R")
    g <- create_network(N, M, segregation, gullible)
    for(i in 1:N){
      if (V(g)[i]$community==1){
        V(g)[i]$gullibility=alpha_skeptical
      }
      else{
        V(g)[i]$gullibility=alpha_gullible
      }
    }
  }
  else{
    if(type=="barabasi"){
      g <- barabasi.game(N, m=3, directed=FALSE) 
    }
    else if(type=="random"){
      g <- erdos.renyi.game(N, M , type="gnm", directed=FALSE)
    }   
    V(g)$gullibility=alpha_skeptical
  }

  
  #initialize all nodes as SUSCEPTIBLE (blue)
  #V(g)$color="blue"
  V(g)$red=0
  V(g)$green=0
  V(g)$blue=1
  
  #initialize FACT-CHECKERS (red) choosing them randomly
  if(red_init){
    for (ir in 1:red_init) {
      rv=round(runif(1,1,N))
      while(V(g)[rv]$red){  
        rv=round(runif(1,1,N))
      }
      #V(g)[rv]$color="red"
      V(g)[rv]$red=1
      V(g)[rv]$green=0
      V(g)[rv]$blue=0
    }
  }
  
  #initialize BELIEVERS (green) choosing them randomly
  if(green_init){
    for (ig in 1:green_init) {
      rv <- round(runif(1,1,N))  
      while(V(g)[rv]$green){  
        rv=round(runif(1,1,N))
      }
      #V(g)[rv]$color="green"
      V(g)[rv]$red=0
      V(g)[rv]$green=1
      V(g)[rv]$blue=0 #e infine colora
    }
  }
  

  #initialize time
  time <- time_init
  
  while(time <= time_end ){    
    print(time)
    
    #initialize counters for a new time iteration
    vred_counter= 0
    vblue_counter= 0
    vgreen_counter= 0  
    
    #create a copy of the graph
    g_aux <-g
    
    #for each vertex ... 
    for(i in 1:N){
      # ... compute the probabilities to move to another status and realize it
      
      if(V(g)[i]$green){   #BELIEVER
        #generate random number in (0,1)
        u1 <- runif(1,0,1)    
        if(u1 < p_forget){ #move to SUSCEPTIBLE
          #V(g_aux)[i]$color="blue"
          V(g_aux)[i]$red=0
          V(g_aux)[i]$green=0
          V(g_aux)[i]$blue=1
          vblue_counter <- vblue_counter + 1     
        }
        else{ 
          u2 <- runif(1,0,1)    
          if(u2 < 1-V(g)[i]$gullibility){ #move to FACT-CHECKER
            #V(g_aux)[i]$color="red"
            V(g_aux)[i]$red=1
            V(g_aux)[i]$green=0
            V(g_aux)[i]$blue=0
            vred_counter <- vred_counter + 1     
          }
          else{ #stay BELIEVER
            #V(g_aux)[i]$color="green"
            V(g_aux)[i]$red=0
            V(g_aux)[i]$green=1
            V(g_aux)[i]$blue=0
            vgreen_counter <- vgreen_counter + 1 
          }
        }
      }
      else if(V(g)[i]$red){ #FACT-CHECKER 
        u1 <- runif(1,0,1)    
        if(u1 < p_forget){ #move to SUSCEPTIBLE
          #V(g_aux)[i]$color="blue"
          V(g_aux)[i]$red=0
          V(g_aux)[i]$green=0
          V(g_aux)[i]$blue=1
          vblue_counter <- vblue_counter + 1     
        }
        else{ #stay FACT-CHECKER
          #V(g_aux)[i]$color="red"
          V(g_aux)[i]$red=1
          V(g_aux)[i]$green=0
          V(g_aux)[i]$blue=0
          vred_counter <- vred_counter + 1  
        }
      }
      else{ #SUSCEPTIBLE
        n_i = neighbors(g,V(g)[i])
        red_neighbors=sum(V(g)[n_i]$red)
        green_neighbors=sum(V(g)[n_i]$green)
        
        if(green_neighbors == 0 && red_neighbors == 0){ #if all neighors are susceptible, stay susceptible
          #V(g_aux)[i]$color="blue"
          V(g_aux)[i]$red=0
          V(g_aux)[i]$green=0
          V(g_aux)[i]$blue=1
          vblue_counter <- vblue_counter + 1
        }
        else{
          alpha=V(g)[i]$gullibility
          pb <- beta * ((green_neighbors * (1+alpha))/(green_neighbors * (1+alpha) + red_neighbors* (1-alpha)))
          pf <- beta * ((red_neighbors * (1-alpha))/(green_neighbors * (1+alpha) + red_neighbors* (1-alpha)))
          ps <- 1-beta
          
          #multirealization of the distribution given by (pb, pf, ps) for node i
          #generate random number in (0,1)
          u <- runif(1,0,1)    
          
          #select the corresponding probability and color the vertice with the respective color  
          if (u<pb) {
            #V(g_aux)[i]$color="green"
            V(g_aux)[i]$red=0
            V(g_aux)[i]$green=1
            V(g_aux)[i]$blue=0
            vgreen_counter <- vgreen_counter + 1 
          }
          else if(u<pb+pf){
            #V(g_aux)[i]$color="red"
            V(g_aux)[i]$red=1
            V(g_aux)[i]$green=0
            V(g_aux)[i]$blue=0
            vred_counter <- vred_counter + 1 
          }
          else{
            #V(g_aux)[i]$color="blue"
            V(g_aux)[i]$red=0
            V(g_aux)[i]$green=0
            V(g_aux)[i]$blue=1
            vblue_counter <- vblue_counter + 1
          }
        }
      }
    }
    
    
    #store the sizes of the compartments 
    vred[it,time]<-vred_counter
    vgreen[it,time]<-vgreen_counter
    vblue[it,time]<-vblue_counter
    
    #copy the new graph obtained
    g <- g_aux
    
    if(type=="communities"){
      gull <- V(g)[V(g)$community==2]
      skep <- V(g)[V(g)$community==1]
    
      gullible_green[it,time]=sum(gull$green)
      gullible_red[it,time]=sum(gull$red)
      gullible_blue[it,time]=sum(gull$blue)
    
      skeptic_green[it,time]=sum(skep$green)
      skeptic_red[it,time]=sum(skep$red)
      skeptic_blue[it,time]=sum(skep$blue)
    }
    
    #increase time  
    time <- time+tau    
  }
  
  #increase iterations
  it <- it +1
  
}


#PLOT the averaged behavior of Believers, Fact-checkers and Susceptible over time
cat('Do you want to plot dynamic? ("y"=yes) >')
b <-  scan("", what="string",n=1)

if(b=='y'){
t <- seq(time_init, time_end, tau)

mean_vred <-list()
mean_vgreen <-list()
mean_vblue <-list()

for(k in t){
  mean_vred[k] <- mean(vred[,k],trim=0)
  mean_vgreen[k] <- mean(vgreen[,k],trim=0)
  mean_vblue[k] <- mean(vblue[,k],trim=0)
}

source("plot_dynamics_sbf.R")
xx<-"TOT"
plot_dynamics(xx, t, mean_vred, mean_vblue, mean_vgreen)

#if there are communities, plot averaged behaviors for gullible and skeptic groups
if(type=="communities"){
  cat('Do you want to plot dynamics for gullible and skeptic group? ("y"=yes) >')
  bb <- scan("", what="string",n=1)
  
  if(bb=='y'){
  
  mean_ggreen <-list()
  mean_gred <-list()
  mean_gblue <-list() 
  mean_sgreen <-list() 
  mean_sred  <-list()
  mean_sblue <-list()
  
  for(k in t){
    mean_gred[k] <- mean(gullible_red[,k],trim=0)
    mean_ggreen[k] <- mean(gullible_green[,k],trim=0)
    mean_gblue[k] <- mean(gullible_blue[,k],trim=0)
    mean_sred[k] <- mean(skeptic_red[,k],trim=0)
    mean_sgreen[k] <- mean(skeptic_green[,k],trim=0)
    mean_sblue[k] <- mean(skeptic_blue[,k],trim=0)
  }
  
  xx<-"GUL"
  plot_dynamics(xx, t, mean_gred, mean_gblue, mean_ggreen)
  xx<-"SK"
  plot_dynamics(xx, t, mean_sred, mean_sblue, mean_sgreen)
  }
}
}

#SAVE OUTPUT in a file
path=getwd()
if(type=="communities"){
  namefile=paste(path,"/results/beta",beta,"gullsize",gullible,"_gull",alpha_gullible,"_alphaskept",alpha_skeptical,"_seg",segregation,"_forget",p_forget,"_ave",num_iterations,"it.RData", sep="")
  save(t, num_iterations, N,M, gullible, beta, p_forget, alpha_gullible, alpha_skeptical, segregation, mean_vgreen, mean_vred, mean_vblue, vgreen, vred, vblue, mean_ggreen, mean_gred, mean_gblue, mean_sgreen, mean_sred, mean_sblue, gullible_green, gullible_red, gullible_blue, skeptic_green, skeptic_red, skeptic_blue, file = namefile, envir = parent.frame())
  save.image()
}else{
  namefile=paste(path,"/results/beta",beta,"alpha",alpha_skeptical,"_forget",p_forget,"_ave",num_iterations,"it.RData", sep="")
  save(t, num_iterations, N,M, beta, p_forget, alpha_skeptical, mean_vgreen, mean_vred, mean_vblue, vgreen, vred, vblue, file = namefile, envir = parent.frame())
  save.image()
}



#}
