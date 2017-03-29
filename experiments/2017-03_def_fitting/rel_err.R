library(reshape2)
library(ggplot2)
library(plotly)

setwd("~/Desktop/fit/fitting_data")
files=list.files("~/Desktop/fit/fitting_data")

# Function that returns Root Mean Squared Error
rel_err <- function(data, model)
{ 
  abs_er=abs(model-data)
  for(t in 1:length(abs_er)){
    if(data[t]!=0){
      abs_er[t]/data[t]
    }
  }
  re <- mean(abs_er)
}


seg_b_nre <- vector()
seg_f_nre <- vector()
noseg_b_nre <- vector()
noseg_f_nre <- vector()

hoax <- vector()

i=1
for(j in seq(1,length(files),2)){
  
  name=strsplit(files[j],"*_with_segregation.csv")
  #name1=strsplit(name[[1]],"hoaxy_*")
  hoax[i]= name[[1]][1]
  print(hoax[i])
  
  #seg
  seg <- read.table(files[j], header = TRUE, sep=",")
  seg_for =seg$For_empirico
  seg_against=seg$Against_empirico
  seg_ba = seg$For_BA
  seg_fa = seg$Against_FA
  
  seg_b_nre[i] = rel_err(seg_for, seg_ba)
  print(paste0("nre FOR:",seg_b_nre))
 
  seg_f_nre[i] = rel_err(seg_against, seg_fa)
  print(paste0("nre AGAINST:",seg_f_nre))
  
  #noseg
  noseg <- read.table(files[j+1], header = TRUE, sep=",")
  noseg_for =noseg$For_empirico
  noseg_against=noseg$Against_empirico
  noseg_ba = noseg$For_BA
  noseg_fa = noseg$Against_FA
  
  noseg_b_nre[i] = rel_err(noseg_for, noseg_ba)
  print(paste0("nre FOR:",noseg_b_nre))

  noseg_f_nre[i] = rel_err(noseg_against, noseg_fa)
  print(paste0("nre AGAINST:",noseg_f_nre))
  
  i <-i+1
}

#rmse
ave_seg_b_nre <- mean(seg_b_nre)
ave_seg_f_nre <- mean(seg_f_nre)
ave_noseg_b_nre  <- mean(noseg_b_nre)
ave_noseg_f_nre <- mean(noseg_f_nre)

print("====RMSE====")
print(paste0("noseg_AB:",ave_noseg_b_nre))
print(paste0("noseg_AF:",ave_noseg_f_nre))
print(paste0("seg_AB:",ave_seg_b_nre))
print(paste0("seg_AF:",ave_seg_f_nre))


ave_df <- data.frame(ave_noseg_b_nre, ave_noseg_f_nre, ave_seg_b_nre, ave_seg_f_nre)
colnames(ave_df) <-c("noseg_b","noseg_f","seg_b","seg_f")
m_ave <- melt(ave_df)
ap <- ggplot(data=m_ave, aes(x=variable, y=value, fill=variable))+
  geom_bar(stat="identity",position=position_dodge())+
  scale_fill_brewer(palette="Spectral")+
  #ylim(c(0,0.003))+
  xlab("model compartment")+
  #scale_x_discrete(labels=c("","","",""))+
  theme(axis.text.x =element_text(size=12))+
  ggtitle("Relative Error")
ap <- ggplotly(ap)
show(ap)

plot_df <- data.frame(hoax,
                       noseg_b_nre, noseg_f_nre,
                       seg_b_nre, seg_f_nre)                      
colnames(plot_df) <-c("hoax","noseg_b","noseg_f", "seg_b","seg_f")
m <- melt(plot_df)

p <- ggplot(data=m, aes(x=hoax, y=value, fill=variable))+
  geom_bar(stat="identity", position=position_dodge())+
  theme(axis.text.x =element_text(size=8, angle=90))+
  scale_fill_brewer(palette="Spectral")+
  scale_x_discrete(labels=c(1:31))+
  ggtitle("Relative Error")

p <- ggplotly(p)
show(p)



