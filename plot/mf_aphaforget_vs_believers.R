#creates a plot of number of believers (as mean-field results) as function of credibility and forgetting probability
#to create a tiff, unquote quoted lines (11 and 20)

beta=0.5
forg=seq(0,1,0.01)
a=c(0.01, seq(0.1,0.9,0.1),0.99)

fp=(1-a)**2/(1+a**2)

mycolors=rev(grey.colors(11, start=0.3, end = 0.9, gamma =2.2, alpha=NULL))
#tiff("mf_alphaforget_vs_believers.tiff", width=5.25, units='in', res=300)
dev.new(width=5.25, height=3, res=300, units='in')
matplot(forg, outer(forg, a, function(forg, a) beta*(forg*(a**2+1)-(1-a)**2)/(2*a*(forg+beta)*(1-a+a*forg))),
        type ="l", lwd=4, col = mycolors, xlim=c(0,1), ylim = c(0, 1), pch = "*", lty=1,
        xaxs = "i", yaxs = "i",xlab=expression( p["forget"]), ylab=expression(B[infinity]) )
par(ps=14, cex=1, cex.axis=1, cex.lab=1, cex.main=1)

legend(0.45, 1,a, col = mycolors, lty = par("lty"),lwd=4,ncol =3, bty="n", title=expression(paste(alpha," values")))

#dev.off()
