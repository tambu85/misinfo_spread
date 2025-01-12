library(viridis)
library(reshape2)
library(ggplot2)
library(aqfig)
library(data.table)
library(dplyr)
library(plotly)

mypath=file.path(getwd(),"data")
files = list.files(path = mypath)
shift <- length(files)/2

for(j in 1:shift){
  setwd(mypath)
  print(j)
  print("reading files...")
  param_des <- sub("out_g_(.*?).txt","\\1",files[j])
  g_size <-as.numeric(sub(".*?size_(.*?)_pvsk_.*?.txt","\\1",files[j]))
  sk_size <- 1-(g_size)

  gul <- read.table(files[j], header = FALSE,
                    col.names = c("alpha","seg",
                                  "pba_g","pbi_g",
                                  "pfa_g","pfi_g",
                                  "psus_g"))
  skep <- read.table(files[j+shift], header = FALSE, 
                     col.names = c("alpha","seg",
                                   "pba_sk","pbi_sk",
                                   "pfa_sk","pfi_sk",
                                   "psus_sk"))
  #empty matrices
  alphas <- seq(0,1,0.005)
  segregations <- seq(0.5, 1,0.0025)
  
  temp <- matrix(NA, nrow = length(alphas), ncol= length(segregations))
  colnames(temp) <- segregations
  rownames(temp) <- alphas
  
  sus_mf <- temp
  ba_mf <- temp
  bi_mf <- temp
  fa_mf <- temp
  fi_mf <- temp
  
  gsus_mf <- temp
  gba_mf <- temp
  gbi_mf <- temp
  gfa_mf <- temp
  gfi_mf <- temp
  
  sksus_mf <- temp
  skba_mf <- temp
  skbi_mf <- temp
  skfa_mf <- temp
  skfi_mf <- temp

  
  print("loading data...")
  for(i in 1:nrow(gul)){
    if(i%%1000==0) print(i)
    gsus_mf[toString(gul[i,]$alpha),toString(gul[i,]$seg)]=round(gul[i,]$psus_g*g_size,5)
    gba_mf[toString(gul[i,]$alpha),toString(gul[i,]$seg)]=round(gul[i,]$pba_g*g_size,5)
    gbi_mf[toString(gul[i,]$alpha),toString(gul[i,]$seg)]=round(gul[i,]$pbi_g*g_size,5)
    gfa_mf[toString(gul[i,]$alpha),toString(gul[i,]$seg)]=round(gul[i,]$pfa_g*g_size,5)
    gfi_mf[toString(gul[i,]$alpha),toString(gul[i,]$seg)]=round(gul[i,]$pfi_g*g_size,5)
    
    sksus_mf[toString(skep[i,]$alpha),toString(skep[i,]$seg)]=round(skep[i,]$psus_sk*sk_size,5)
    skba_mf[toString(skep[i,]$alpha),toString(skep[i,]$seg)]=round(skep[i,]$pba_sk*sk_size,5)
    skbi_mf[toString(skep[i,]$alpha),toString(skep[i,]$seg)]=round(skep[i,]$pbi_sk*sk_size,5)
    skfa_mf[toString(skep[i,]$alpha),toString(skep[i,]$seg)]=round(skep[i,]$pfa_sk*sk_size,5)
    skfi_mf[toString(skep[i,]$alpha),toString(skep[i,]$seg)]=round(skep[i,]$pfi_sk*sk_size,5)
    
  }
  
  #compute total
  sus_mf=gsus_mf+sksus_mf
  ba_mf=gba_mf+skba_mf
  bi_mf=gbi_mf+skbi_mf
  fa_mf=gfa_mf+skfa_mf
  fi_mf=gfi_mf+skfi_mf

  mypal=rev(viridis(256,option="inferno"))
  path=file.path(getwd(),"heatmaps")

  #to change type (svg, png) just copy the commented lines below and substitute 
  
  svg(paste(path,"/",param_des,"_mfsus.svg",sep=""))
  image(segregations, alphas, t(sus_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,xlab="segregation", ylab="literacy")
  #vertical.image.legend(col=mypal, zlim=c(0,max(1, na.rm=TRUE)))
  #title("SUSCEPTIBLE MF", cex.main=1.5)
  dev.off()
  
  pdf(paste(path,"/",param_des,"_mfba.svg",sep=""))
  image(segregations, alphas, t(ba_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,xlab="segregation", ylab="literacy")
  #title("BELIEVERS ACTIVE  MF", cex.main=1.5)
  dev.off()
  
  svg(paste(path,"/",param_des,"_mfbi.svg",sep=""))
  image(segregations, alphas, t(bi_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,xlab="segregation", ylab="literacy")
  #title("BELIEVERS INACTIVE MF", cex.main=1.5)
  dev.off()
  
  svg(paste(path,"/",param_des,"_mffa.svg",sep=""))
  image(segregations, alphas, t(fa_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,xlab="segregation", ylab="literacy")
  #title("FACT-CHECKERS ACTIVE MF", cex.main=1.5)
  dev.off()
  
  svg(paste(path,"/",param_des,"_mffi.svg",sep=""))
  image(segregations, alphas, t(fi_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,xlab="segregation", ylab="literacy")
  #title("FACT-CHECKERS INACTIVE MF", cex.main=1.5)
  dev.off()
  
  #svg
  png(paste(path,"/",param_des,"_mfsus.png",sep=""))
  image(segregations, alphas, t(sus_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,
        xlab="", ylab="", yaxt='n', xaxt='n')
  #vertical.image.legend(col=mypal, zlim=c(0,max(1, na.rm=TRUE)))
  #title("SUSCEPTIBLE MF", cex.main=1.5)
  dev.off()

  png(paste(path,"/",param_des,"_mfba.png",sep=""))
  image(segregations, alphas, t(ba_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,
        xlab="", ylab="", yaxt='n', xaxt='n')
  #title("BELIEVERS ACTIVE  MF", cex.main=1.5)
  dev.off()

  png(paste(path,"/",param_des,"_mfbi.png",sep=""))
  image(segregations, alphas, t(bi_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,
        xlab="", ylab="", yaxt='n', xaxt='n')
  #title("BELIEVERS INACTIVE MF", cex.main=1.5)
  dev.off()

  png(paste(path,"/",param_des,"_mffa.png",sep=""))
  image(segregations, alphas, t(fa_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,
        xlab="", ylab="", yaxt='n', xaxt='n')
  #title("FACT-CHECKERS ACTIVE MF", cex.main=1.5)
  dev.off()

  png(paste(path,"/",param_des,"_mffi.png",sep=""))
  image(segregations, alphas, t(fi_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,
        xlab="", ylab="", yaxt='n', xaxt='n')
  #title("FACT-CHECKERS INACTIVE MF", cex.main=1.5)
  dev.off()
  
  ###pdf
  pdf(paste(path,"/",param_des,"_mfsus.pdf",sep=""))
  image(segregations, alphas, t(sus_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,xlab="segregation", ylab="literacy")
  dev.off()
  
  pdf(paste(path,"/",param_des,"_mfba.pdf",sep=""))
  image(segregations, alphas, t(ba_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,xlab="segregation", ylab="literacy")
  dev.off()
  
  pdf(paste(path,"/",param_des,"_mfbi.pdf",sep=""))
  image(segregations, alphas, t(bi_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,xlab="segregation", ylab="literacy")
  dev.off()
  
  pdf(paste(path,"/",param_des,"_mffa.pdf",sep=""))
  image(segregations, alphas, t(fa_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,xlab="segregation", ylab="literacy")
  dev.off()
  
  pdf(paste(path,"/",param_des,"_mffi.pdf",sep=""))
  image(segregations, alphas, t(fi_mf), zlim=c(0,1), col=mypal,
        cex.axis=1.5,  cex.lab=1.5,xlab="segregation", ylab="literacy")
  dev.off()

  ##FINE HEATMAPS

  contourdata <- melt(ba_mf)
  names(contourdata) <- c("cred", "seg", "AB")
  
  # Basic plot
  ba_cp <- ggplot() +
    geom_tile(data = contourdata,
              aes(x = seg, y = cred, fill = AB, colour = AB)) +
    geom_contour(data = contourdata,
                 aes(x = seg, y = cred, z = AB),
                 colour = "black", size = 0.4, alpha=0.5, binwidth = 0.02) +
    geom_raster()+
    scale_color_viridis(direction = -1,option = "inferno",limits=range(0,1))+
    scale_fill_viridis(direction = -1, option = "inferno",  limits=range(0,1))+
    #xlab("segregation")+
    #ylab("literacy")+
    xlab("")+
    ylab("")+
    scale_x_continuous(expand = c(0, 0)) +
    scale_y_continuous(expand = c(0, 0)) +
    theme_bw() + theme(panel.grid = element_blank(),
                       panel.border = element_rect(colour = "black", fill=NA, size=1),
                       text = element_text(size=20),
                       legend.position="none")
  
  print(ba_cp)
  
  # svg(paste(path,"/",param_des,"_contour.svg",sep=""))
  #   show(ba_cp)
  # dev.off()
  # 
  # png(paste(path,"/",param_des,"_contour.png",sep=""))
  #   show(ba_cp)
  # dev.off()
  #
  pdf(paste(path,"/",param_des,"_contour.png",sep=""))
   show(ba_cp)
   dev.off()


#********PLOTLY BA******
  mypal=rev(viridis(256,option="inferno"))
  maxc=max(ba_mf)*256
  p <- plotly(x=segregations, y=alphas,z = ba_mf, type = "heatmap", colors=mypal[1:maxc])%>%
      layout(title = paste0("ACTIVE BELIEVERS - ",param_des),
             scene = list(
               xaxis = list(title = "Segregation"), 
               yaxis = list(title = "literacy"), 
               zaxis = list(title = "AB")))
  show(p)

  p_contour <- plot_ly(contourdata, x = ~seg, y = ~cred, z = ~AB, 
                     type = "contour", colors=mypal[1:maxc])%>%
    layout(title = paste0("ACTIVE BELIEVERS - ",param_des))
  show(p_contour)



  p3d <- plot_ly(x=segregations, y=alphas,
               z = ba_mf, type = "surface",
               colors=mypal[1:maxc])%>%
    layout(title = paste0("ACTIVE BELIEVERS - ",param_des),
         scene = list(
           xaxis = list(title = "Segregation"), 
           yaxis = list(title = "literacy"), 
           zaxis = list(title = "AB")))

  show(p3d)

}
