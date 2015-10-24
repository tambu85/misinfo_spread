plot_dynamics <- function(x,t,mean_vred, mean_vblue, mean_vgreen){

#create svg
path=getwd()
svg(paste(path,"/plot/DYN_",x,"alphas",alpha_skeptical,"_alphag",alpha_gullible,"_sizegull",gullible,"_seg",segregation,"_ave",num_iterations,"it",".svg",sep=""))
plot(t,mean_vred,type="l",col="darkred",ylim=c(1,N), ylab="nodes", lwd=3)
lines(t,mean_vgreen,type="l",col="yellowgreen", lwd=3)
lines(t,mean_vblue, type="l",col="blue", lwd=3)
dev.off()


}