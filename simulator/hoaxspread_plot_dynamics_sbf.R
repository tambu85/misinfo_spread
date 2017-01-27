plot_dynamics <- function(xx, t, mean_vba, mean_vfa, mean_vbi, mean_vfi, mean_vsus){

  #create svg
  path=getwd()
  mycolors=c("forestgreen","yellowgreen","red","orange","blue")
  if(type=="communities"){
    svg(paste(path,"/DYN_",xx,"_alpha",alpha,"_verifySK",pv,
              "_seg",segregation,"_gsize",gullible_size,
              "_tau",tau,"_ave",num_iterations,"it",".svg",sep=""))
    plot(t,mean_vba,type="l",col="forestgreen",ylim=c(1,N), ylab="nodes", lwd=3)
    lines(t,mean_vbi,type="l",col="yellowgreen", lwd=3)
    lines(t,mean_vfa,type="l",col="red", lwd=3)
    lines(t,mean_vfi,type="l",col="orange", lwd=3)
    lines(t,mean_vsus,type="l",col="blue", lwd=3)
    title(paste("alpha=",alpha," pv=",pv, "seg",segregation))
    legend(140, 800, c("bel active", "bel inactive", "fac active", "fac inactive", "susceptible"), 
           col = mycolors, lty = par("lty"),lwd=2,ncol =1,bty="n")
    dev.off()
  }
  else{
    svg(paste(path,"/DYN_",xx,"_alpha",alpha,"_verify",pv,
              "_tau",tau,"_ave",num_iterations,"it",".svg",sep=""))
    plot(t,mean_vba,type="l",col="forestgreen",ylim=c(1,N), ylab="nodes", lwd=3)
    lines(t,mean_vbi,type="l",col="yellowgreen", lwd=3)
    lines(t,mean_vfa,type="l",col="red", lwd=3)
    lines(t,mean_vfi,type="l",col="orange", lwd=3)
    lines(t,mean_vsus,type="l",col="blue", lwd=3)
    title(paste("alpha=",alpha," pv=",pv))
    legend(140, 800, c("bel active", "bel inactive", "fac active", "fac inactive", "susceptible"), 
           col = mycolors, lty = par("lty"),lwd=2,ncol =1,bty="n")
    dev.off()
  }
}
