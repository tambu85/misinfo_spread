#plot 3 graphs with different segregation values
#for a better visualization plot separetly the three graphs

library(igraph)
source("create_graph_communities.R")
N <- 1000
M <- 2994
gullible_size=500

#create graphs with segregation 0.6, 0.8 and 0.95
g1 <- create_network(N,M, 0.6, gullible_size)
g2 <- create_network(N,M, 0.8, gullible_size)
g3 <- create_network(N,M, 0.95, gullible_size)

#set size and resolution
dev.new(width=5.25, res=300)

#set layout (3 subplots in 1 row)
par( mfrow = c( 1, 3 ) )

l=layout.fruchterman.reingold(g1, niter=1000, area=50*N^2)
l=layout.norm(l,ymin=-1,ymax=1,xmin=-1, xmax=1)
plot(g1, vertex.color=V(g1)$color, vertex.label=NA, vertex.size=5, rescale=F, layout=l*1, vertex.frame.color="black", edge.color="gray80", main="(a)")
par(ps=14)

l=layout.fruchterman.reingold(g2, niter=1000, area=50*N^2)
l=layout.norm(l,ymin=-1,ymax=1,xmin=-1, xmax=1)
plot(g2, vertex.color=V(g2)$color, vertex.label=NA, vertex.size=5, rescale=F, layout=l*1, vertex.frame.color="black", edge.color="gray80", main="(b)")
par(ps=14)

l=layout.fruchterman.reingold(g3, niter=1000, area=50*N^2)
l=layout.norm(l,ymin=-1,ymax=1,xmin=-1, xmax=1)
plot(g3, vertex.color=V(g3)$color, vertex.label=NA, vertex.size=5, rescale=F, layout=l*1, vertex.frame.color="black", edge.color="gray80", main="(c)")
par(ps=14)



