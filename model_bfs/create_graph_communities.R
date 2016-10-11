###function to create the network###
create_network <- function(num_nodes, num_edges, seg_value, gull_size){
  N <- num_nodes #size of graph
  M <- num_edges
  gullible_size <- gull_size #size of gullible group
  skeptic_size <- N - gullible_size
  theta <- 1-seg_value #segregation 
  g<- graph.empty(n=N, directed=FALSE)
  
  #initialize all skeptical
  V(g)$community= 1 #skeptical
  V(g)[i]$color="white"
  
  #initialize gullible community
  for(i in 1:gullible_size){  
    V(g)[i]$community=2 #gullible
    V(g)[i]$color="black"
  }
  
  #assign links
  e_inter_c=round(M*(1-theta))
  e_intra_c=round(M*theta)
  
  #possible links
  p_arc_gullible=gullible_size*(gullible_size-1)/2
  p_arc_skeptic=skeptic_size*(skeptic_size-1)/2
  
  
  #same community
  arc_inter_sk=0
  arc_inter_g=0
  for(arc in 1:e_inter_c){  
    
    i=round(runif(1,1,N)) #select randomly node
    
    #check if arc is <= number of possible arc in a community...
    #...for gullible
    if(V(g)[i]$community == 2 && arc_inter_g>= p_arc_gullible){
      i=round(runif(1,1,N)) #select randomly node
    }
    
    #...and for skeptic
    if(V(g)[i]$community == 1 && arc_inter_sk >= p_arc_skeptic){
      i=round(runif(1,1,N)) #select randomly node
    }
    
    
    if (V(g)[i]$community == 1){ #if node i is skeptical
      j=round(runif(1,(gullible_size+1),N)) #select a skeptical
      while(i==j || g[i, j, edges=TRUE]>0){ #check if (i,j) already exists
        j=round(runif(1,(gullible_size+1),N))
      }
      arc_inter_sk=arc_inter_sk+1
    }
    
    if (V(g)[i]$community == 2){ #if node i is gullible
      j=round(runif(1,1,(gullible_size))) #select a gullible
      while(i==j || g[i, j, edges=TRUE]>0){ #check if (i,j) already exists
        j=round(runif(1,1,(gullible_size))) 
      }
      arc_inter_g=arc_inter_g+1
    }
    g[from=i, to=j] <- TRUE #add (i,j) 
  }
  
  #if there are isolated nodes, connect them with their communities
  for(i in V(g)){
    if(degree(g)[i]==0){
      if (V(g)[i]$community == 1 && p_arc_skeptic>0){ #if node i is skeptical
        j=round(runif(1,(gullible_size+1),N)) #select a skeptical
        while(i==j || degree(g)[j]<=1){ #if I select the same node or an isolated node
          j=round(runif(1,(gullible_size+1),N)) #I select another skeptical
        }
      }
      
      if (V(g)[i]$community == 2 && p_arc_gullible>0){ #if node i is gullible
        j=round(runif(1,1,(gullible_size))) #select a gullible
        while(i==j|| degree(g)[j]<=1){ #if I select the same node or an isolated node
          j=round(runif(1,1,(gullible_size)))  #I select another gullible
        }
      }
      k=neighbors(g,j)[1] #select the first neighbor of the selected victim
      g[from=j, to=k] <- FALSE #remove the edge 
      g[from=i, to=j] <- TRUE #add (i,j)
    }
  }
  
  
  #different community
  if(e_intra_c){
    for(arc in 1:e_intra_c){  
      
      i=round(runif(1,1,N)) #select randomly a node
      
      if (V(g)[i]$community == 1){ #if node i skeptical
        j=round(runif(1,1,(gullible_size)))  #select a gullible    
        while(g[i, j, edges=TRUE]>0){ #check if (i,j) already exists
          if(degree(g)[i]>=(gullible_size)){
            i=round(runif(1,gullible_size+1,N))
          }
          else{
            j=round(runif(1,1,(gullible_size)))
          }
        }
      }
      
      if (V(g)[i]$community == 2){ #if node i is gullible
        j=round(runif(1,(gullible_size+1),N)) #select a skeptical
        while(g[i, j, edges=TRUE]>0){ #check if (i,j) already exists
          if(degree(g)[i]>=(skeptic_size)){
            i=round(runif(1,1,gullible_size))
          }
          else{
            j=round(runif(1,(gullible_size+1),N))
          }
        }
      }
      
      g[from=i, to=j] <- TRUE #add (i,j) 
    }}
  return(g)
}
