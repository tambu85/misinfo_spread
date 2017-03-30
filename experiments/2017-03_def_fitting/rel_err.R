library(reshape2)
library(ggplot2)
library(plotly)

setwd("~/Desktop/fit/fitting_data")
files=list.files("~/Desktop/fit/fitting_data")

# Function that returns Relative Error
rel_err <- function(data, model)
{ 
  idx = which(data == 0)
  if(length(idx)>0){
    #print(idx)
    data=data[-idx]
    model=model[-idx]
  }
  abs_er=abs(model-data)
  rel_er=abs_er/data
  re <- mean(rel_er)
  return(re)
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
  print(i)
  print(hoax[i])
  
  #seg
  seg <- read.table(files[j], header = TRUE, sep=",")
  seg_for =seg$For_empirico
  seg_against=seg$Against_empirico
  seg_ba = seg$For_BA
  seg_fa = seg$Against_FA
  
  seg_b_nre[i] = rel_err(seg_for, seg_ba)
  print(paste0("nre FOR:",seg_b_nre[i]))
  seg_f_nre[i] = rel_err(seg_against, seg_fa)
  print(paste0("nre AGAINST:",seg_f_nre[i]))
  
  #noseg
  noseg <- read.table(files[j+1], header = TRUE, sep=",")
  noseg_for =noseg$For_empirico
  noseg_against=noseg$Against_empirico
  noseg_ba = noseg$For_BA
  noseg_fa = noseg$Against_FA
  
  noseg_b_nre[i] = rel_err(noseg_for, noseg_ba)
  print(paste0("nre FOR:",noseg_b_nre[i]))

  noseg_f_nre[i] = rel_err(noseg_against, noseg_fa)
  print(paste0("nre AGAINST:",noseg_f_nre[i]))
  
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

#old plot
ave_df <- data.frame(ave_noseg_b_nre, ave_noseg_f_nre, ave_seg_b_nre, ave_seg_f_nre)
colnames(ave_df) <-c("noseg_b","noseg_f","seg_b","seg_f")
m_ave <- melt(ave_df)

ap <- ggplot(data=m_ave, aes(x=variable, y=value, fill=variable))+
  geom_bar(stat="identity",position=position_dodge())+
  scale_fill_manual(values=c("blue", "red", "cadetblue1","gold"))+
  #scale_fill_brewer(palette="Spectral")+
  #ylim(c(0,0.003))+
  xlab("model compartment")+
  #scale_x_discrete(labels=c("","","",""))+
  theme(axis.text.x =element_text(size=12))+
  ggtitle("Relative Error")
ap <- ggplotly(ap)
show(ap)

#stacked plot
colnames(m_ave) <- c("model", "value")
m_ave$model<- as.character(m_ave$model)
m_ave$state <- m_ave$model

m_ave$model[m_ave$model == "noseg_b"] <- "noseg"
m_ave$model[m_ave$model == "noseg_f"] <- "noseg"
m_ave$model[m_ave$model == "seg_f"] <- "seg"
m_ave$model[m_ave$model == "seg_b"] <- "seg"
m_ave$state[m_ave$state == "noseg_b"] <- "believers"
m_ave$state[m_ave$state == "noseg_f"] <- "fact-checkers"
m_ave$state[m_ave$state == "seg_b"] <- "believers"
m_ave$state[m_ave$state == "seg_f"] <- "fact-checkers"

ap2 <- ggplot(data=m_ave, aes(x=model, y=value, fill=state))+
  geom_bar(stat="identity")+
  scale_fill_manual(values=c("blue", "red", "cadetblue1","gold"))+
  #scale_fill_brewer(palette="Spectral")+
  #ylim(c(0,0.003))+
  xlab("model compartment")+
  #scale_x_discrete(labels=c("","","",""))+
  theme(axis.text.x =element_text(size=12))+
  theme_minimal()+
  ggtitle("Relative Error")
ap2 <- ggplotly(ap2)
show(ap2)

#old totale plot
plot_df <- data.frame(hoax,
                       noseg_b_nre, noseg_f_nre,
                       seg_b_nre, seg_f_nre)                      
colnames(plot_df) <-c("hoax","noseg_b","noseg_f", "seg_b","seg_f")
m <- melt(plot_df)

p <- ggplot(data=m, aes(x=hoax, y=value, fill=variable))+
  geom_bar(stat="identity", position=position_dodge())+
  scale_fill_manual(values=c("blue", "red", "cadetblue1","gold"))+
  theme(axis.text.x =element_text(size=8, angle=90))+
  #scale_fill_brewer(palette="Spectral")+
  scale_x_discrete(labels=c(1:31))+
  #theme_minimal()+
  ggtitle("Relative Error")

p <- ggplotly(p)
show(p)

#separate plots for entire dataset
#noseg
plot_df_noseg <- data.frame(hoax,
                      noseg_b_nre, noseg_f_nre)                      
colnames(plot_df_noseg) <-c("hoax","noseg_b","noseg_f")
mns <- melt(plot_df_noseg)

pns <- ggplot(data=mns, aes(x=hoax, y=value, fill=variable))+
  geom_bar(stat="identity", position=position_dodge())+
  scale_fill_manual(values=c("blue", "red"))+
  #theme(axis.text.x =element_text(size=8, angle=90))+
  scale_x_discrete(labels=c(1:31))+ theme(axis.text.x =element_text(size=8))+
  #theme_minimal()+
  ggtitle("NOSEG - Relative Error")

pns <- ggplotly(pns)
show(pns)

#seg
plot_df_seg <- data.frame(hoax,
                            seg_b_nre, seg_f_nre)                      
colnames(plot_df_seg) <-c("hoax","seg_b","seg_f")
ms <- melt(plot_df_seg)

ps <- ggplot(data=ms, aes(x=hoax, y=value, fill=variable))+
  geom_bar(stat="identity", position=position_dodge())+
  scale_fill_manual(values=c("blue", "red"))+
  #theme(axis.text.x =element_text(size=8, angle=90))+
  scale_x_discrete(labels=c(1:31))+ theme(axis.text.x =element_text(size=8))+
  #theme_minimal()+
  labs(fill="")+
  ggtitle("SEG - Relative Error")

ps <- ggplotly(ps)
show(ps)



