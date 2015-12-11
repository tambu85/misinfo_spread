
#plot of the threshold condition on forgetting probability
#computed via mean-field

a=seq(0,1,0.001)

f=(1-a)**2/(1+a**2)

dev.new(width=5.25, res=300)
plot(a,f,type="l",col="black",xlab=expression(alpha),ylab=expression( p["forget"]),lwd=4)
par(ps=10, cex=1, cex.axis=1, cex.lab=1, cex.main=1)
cord.x=c(0, a, 1)
cord.y=c(0, f, 0)
polygon(cord.x, cord.y, col="gray")
