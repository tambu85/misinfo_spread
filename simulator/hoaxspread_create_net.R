###function to create the network###
create_network <- function(num_nodes, num_edges, seg_value, gull_size){
  
  N <- num_nodes #size of graph
  M <- num_edges
  gullible_size <- gull_size #size of gullible group
  skeptic_size <- N - gullible_size
  theta <- 1-seg_value #segregation 
  
  #assign links
  e_inter_c=round(M*(1-theta)) #SK-SK or GUL-GUL
  e_intra_c=round(M*theta) #SK-GUL
  
  #possible links
  p_arc_gullible=gullible_size*(gullible_size-1)/2
  p_arc_skeptic=skeptic_size*(skeptic_size-1)/2
  
  #create random graph
  g<- sample_gnm(N,M,directed=FALSE, loops=FALSE)
  g<-simplify(g, remove.multiple=TRUE, remove.loops=TRUE) # Remove the self-loops
  
  gul_index=1:gullible_size
  sk_index=(gullible_size+1):N
  
  #initialize all skeptical
  V(g)$community= 1 #skeptical
  #initialize gullible community
  V(g)[gul_index]$community=2 #gullible
  
  #select weak
  weak <- E(g)[V(g)[V(g)$community==1] %->% V(g)[V(g)$community==2] ]
  gg <- E(g)[V(g)[V(g)$community==2] %->% V(g)[V(g)$community==2] ]
  ss <- E(g)[V(g)[V(g)$community==1] %->% V(g)[V(g)$community==1] ]
  weak_ties <- length(weak)
  inter_g  <- length(gg)
  inter_sk <- length(ss)
  
  if(weak_ties > e_intra_c){ #if too many links G-SK
    
    howmany_tomove <- length(weak) - e_intra_c #count how many have to be removed
    to_remove <- sample(weak, howmany_tomove, replace = FALSE) #select them randomly
    firsts <- ends(g,to_remove)[,1]
    seconds <- ends(g,to_remove)[,2]
    g <- delete_edges(g,to_remove) # remove them
    a <- get.adjacency(g)
    # for(i in 1:howmany_tomove){
    #   a[seconds[i],firsts[i]] <-0
    # }
    a[upper.tri(a)] <- 0
    
    
    zerodeg <- V(g)[degree(g,V(g))==0]
    z<-1
    
    while(sum(a)<M){
      if(z < length(zerodeg)){
        i=as.numeric(zerodeg[z])
        z<-z+1
      }
      else{
        i<-sample(1:N,1)
      }
      
      if(i <= gullible_size){ #if gullible
        j<-sample(gul_index[-i],1) #select gullible
      }
      else{
        j<-sample(sk_index[-(i-gullible_size)],1)
      }
      
      if(i<j) {a[j,i] <-1}
      else{ a[i,j] <-1}
      
    }
    
  }
  
  #weak <- sum(a[(gullible_size+1):N,1:gullible_size])
  #gg <-sum(a[1:gullible_size,1:gullible_size])
  #ss <- sum(a[(gullible_size+1):N,(gullible_size+1):N])
  
  
  else{ #if few links G-SK
    
    howmany_tomove <- e_intra_c - length(weak) #count how many have to be removed
    to_remove <- sample(union(gg,ss), howmany_tomove, replace = FALSE) #select them randomly
    #firsts <- ends(g,to_remove)[,1]
    #seconds <- ends(g,to_remove)[,2]
    g <- delete_edges(g,to_remove) # remove them
    a <- get.adjacency(g) #adj matrix
    a[upper.tri(a)] <- 0
    
    #add links G-SK
    
    zerodeg <- V(g)[degree(g,V(g))==0]
    z<-1
    
    while(sum(a)<M){
      
      if(z < length(zerodeg)){
        i=as.numeric(zerodeg[z])
        z<-z+1
      }
      else{
        i<-sample(1:N,1)
      }
      
      if(i <= gullible_size){ #if the first is gullible
        j<-sample(sk_index,1) #select a skeptic
      }
      else{ #if the first is skeptic
        j<-sample(gul_index,1) #select a gullible
      }
      
      if(i<j) {a[j,i] <-1}
      else{ a[i,j] <-1}
    }
  }
  
  g <- graph.adjacency(a, mode="undirected")
  V(g)$community= 1 #skeptical
  V(g)[gul_index]$community=2 #gullible
  
  #check components
  clust <- clusters(g)
  V(g)[gul_index]$color="blue"
  #plot(g,vertex.size=3,vertex.label=NA,vertex.color=V(g)$color)
  
  while((seg_value !=1 && clust$no >1) || (seg_value==1 && clust$no >2)){
    #print(clust$no)
    clu <- clust$membership
    clusize <- sort(clust$csize, decreasing=TRUE)
    #big_comp <- which(clusters(g)$csize==clusize[1])
    clusize=clusize[-1]
    clusize=unique(clusize)
    
    for(size_index in (1:length(clusize))){ #extract clusters with all the other dimensions
      
      iso_clu <- which(clust$csize==clusize[size_index])
      for(clu_index in (1:length(iso_clu))){ #for each isolated component of that size...
        
        iso_nodes <- which(clust$membership==iso_clu[clu_index])  #...extract nodes that are in these clusters
        i= iso_nodes[1] # ... consider the first node
        
        if ((V(g)[i]$community == 1)){ #if node i is skeptical
          j=sample(sk_index[-i],1) #select a skeptical in the sk giant component
        }
        
        if ((V(g)[i]$community == 2)){ #if node i is gullible
          j=sample(gul_index[-i],1)  #select a gullible in the giant gullible component
        }
        
        k=neighbors(g,j)[1] #select the first neighbor of the selected victim
        g[from=j, to=k] <- FALSE #remove the edge
        g[from=i, to=j] <- TRUE #add (i,j)
      }
      
    }
    clust <- clusters(g)
    
  }

  print("network created!")
  V(g)$color="orange"
  V(g)[gul_index]$color="blue"
  #plot(g,vertex.size=3,vertex.label=NA,vertex.color=V(g)$color)
  return(g)
}
