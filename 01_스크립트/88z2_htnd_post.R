# 88z2_htnd_post — 17호 사후(88z_htnd 머리 복제)  고혈압성질환 사망(HTND) 사망진단 코딩 민감도(2026-11-08, 공변량 모형 적합 전 sets_HTND_std3.json note에 고정). 88z_alz 복제.
#  사용(01_스크립트/): TAG=HTND ST_VER=std3 ST_THREADS=1 ST_GRAPH=<593> Rscript 88z_htnd_coding.R
#  Z1 주모형 + 불명확 사인(R00-R99) 비율 / Z2 결과 = 순환계통 전체 I00-I99(E = 02_패널/CIRCB_Estd2.csv E_std2) / Z3 = Z2 + 불명확 사인 비율 / Z4 주모형 + 관외 외래 비율(접근성) / Z5 주모형 + 저염선호율(2011-2019 관측 연도만, Z5a = 같은 기간 주모형)
#  산출: results_std3/S45_coding_<an>.csv (공변량 IRR), S45_coding_area.csv (주모형·Z2 지역 공간 RR, 핫스팟 비교용)
#        5 = 같은 기간 비지연 비교 / 6 = 이원 분해(강건 집합)·변수 제외(DROPS)
suppressPackageStartupMessages({library(INLA);library(sf);library(spdep);library(jsonlite)})
TAG<-Sys.getenv("TAG");stopifnot(nzchar(TAG));VER<-Sys.getenv("ST_VER",unset="std");SUF<-if(nzchar(VER))paste0("_",VER) else ""
ROOT<-normalizePath(file.path(dirname(sub("--file=","",grep("--file=",commandArgs(),value=TRUE))),".."))
SHP<-Sys.getenv("ST_SHP",file.path(normalizePath(file.path(dirname(sub("--file=","",grep("--file=",commandArgs(),value=TRUE))),"..")),"data","boundary","final.shp"))
OUTD<-file.path(ROOT,"04_분석",TAG);RES<-file.path(OUTD,paste0("results",SUF))
inla.setOption(num.threads="1:1")
LOG<-function(...)cat(sprintf("[88g %s %s] ",TAG,format(Sys.time(),"%H:%M:%S")),sprintf(...),"\n",sep="")
S<-fromJSON(file.path(OUTD,sprintf("config_%s%s.json",TAG,SUF)),simplifyVector=TRUE)
INFO<-fromJSON(file.path(OUTD,sprintf("panel_INFO_%s%s.json",TAG,SUF)))
DD<-read.csv(file.path(OUTD,sprintf("panel_%s%s.csv",TAG,SUF)),fileEncoding="UTF-8-BOM",stringsAsFactors=FALSE);DD$fbd_region<-enc2utf8(DD$fbd_region)
HB<-readLines(file.path(OUTD,sprintf("HM_best_%s%s.txt",TAG,SUF)));kv<-function(k)sub(paste0("^",k,"="),"",grep(paste0("^",k,"="),HB,value=TRUE)[1])
MAINFAM<-kv("main_family");BEST<-kv("best_set");FORCED<-S$forced;SETS<-lapply(S$sets_after_vif,as.character);HYPV<-SETS[[BEST]];MAINV<-unique(c(HYPV,FORCED))
ROB<-read.csv(file.path(RES,"S7_multiverse_summary.csv"),stringsAsFactors=FALSE);ROBV<-ROB$cov[ROB$robust];NR<-length(ROBV)
M3<-read.csv(file.path(RES,"S3_main_IRR.csv"),stringsAsFactors=FALSE);msign<-setNames(sign(log(M3$IRR)),M3$cov)
FOCAL<-Sys.getenv("FOCAL",unset=if(NR)ROBV[1] else HYPV[1])
LOG("family %s, set %s (%d hyp + %d forced), robust %d (%s), focal %s",MAINFAM,BEST,length(HYPV),length(FORCED),NR,paste(ROBV,collapse=";"),FOCAL)

G<-st_read(SHP,quiet=TRUE);G$region<-enc2utf8(G$region);n<-nrow(G)
g<-inla.read.graph(file.path(RES,sprintf("nb_%s.graph",TAG)));stopifnot(g$n==n)
DD<-DD[order(DD$year,match(DD$fbd_region,G$region)),];DD$area<-match(DD$fbd_region,G$region);Y0<-min(DD$year);DD$time<-DD$year-Y0+1;DD$yiid<-DD$time;DD$id<-seq_len(nrow(DD))
pc<-list(prec=list(prior="pc.prec",param=c(0.5,0.01)),phi=list(prior="pc",param=c(0.5,2/3)));pcp<-list(prec=list(prior="pc.prec",param=c(0.5,0.01)))
CF<-list(mean=0,prec=4,mean.intercept=0,prec.intercept=0.001)
SPf<-function(gr="g")sprintf("f(area,model='bym2',graph=%s,scale.model=TRUE,constr=TRUE,hyper=pc)",gr)
TI<-"f(time,model='rw1',scale.model=TRUE,hyper=pcp)";IT<-"f(yiid,model='iid',hyper=pcp)"
bt<-function(v)sprintf("`%s`",v)
irr<-function(m,v){r<-m$summary.fixed[v,,drop=FALSE];pg<-1-inla.pmarginal(0,m$marginals.fixed[[v]])
  data.frame(cov=v,IRR=round(exp(r$mean),3),lo=round(exp(r$`0.025quant`),3),hi=round(exp(r$`0.975quant`),3),P_gt1=round(pg,3),cred=(r$`0.025quant`>0|r$`0.975quant`<0),stringsAsFactors=FALSE)}
M6<-read.csv(file.path(RES,"S6_spatial_RR.csv"),stringsAsFactors=FALSE);hot0<-M6$fbd_region[M6$class=="hotspot"]
rdp<-function(f){x<-read.csv(file.path(RES,f),fileEncoding="UTF-8",stringsAsFactors=FALSE);x$fbd_region<-enc2utf8(x$fbd_region);x}
mrg<-function(d,X,cols){d<-d[,setdiff(names(d),cols)];d<-merge(d,X[,c("year","fbd_region",cols)],by=c("year","fbd_region"),all.x=TRUE,sort=FALSE);d[order(d$id),]}
fitX<-function(vars,data,fam=MAINFAM,ti=TI,extra=character(0),sp=SPf(),cfg=FALSE){
  rhs<-c("1",bt(vars),extra,sp,ti,IT);rhs<-rhs[nzchar(rhs)];form<-as.formula(paste("cases ~",paste(rhs,collapse="+")))
  m<-tryCatch(inla(form,family=fam,data=data,E=E,control.fixed=CF,control.compute=list(waic=TRUE,config=cfg),control.predictor=list(compute=TRUE,link=1),
    control.inla=list(control.vb=list(emergency=50)),verbose=FALSE),error=function(e){message("fail: ",conditionMessage(e));NULL})
  if(is.null(m))m<-tryCatch(inla(form,family=fam,data=data,E=E,control.fixed=CF,control.compute=list(waic=TRUE,config=cfg),control.predictor=list(compute=TRUE,link=1),
    control.inla=list(control.vb=list(emergency=50),int.strategy="eb",strategy="gaussian"),verbose=FALSE),error=function(e){message("robust fail: ",conditionMessage(e));NULL})
  m}

summ<-function(an,item,m,note,vars){
  if(is.null(m)){LOG("%s FAILED",an);return(invisible())}
  r<-do.call(rbind,lapply(intersect(vars,rownames(m$summary.fixed)),function(v)irr(m,v)))
  out<-data.frame(analysis=an,item=item,r,WAIC=round(m$waic$waic,1),note=note,stringsAsFactors=FALSE)
  write.csv(out,file.path(RES,sprintf("S45_coding_%s.csv",an)),row.names=FALSE,fileEncoding="UTF-8")
  for(i in seq_len(nrow(out)))LOG("%-14s %-40s %.3f (%.3f-%.3f)%s",an,out$cov[i],out$IRR[i],out$lo[i],out$hi[i],if(out$cred[i])"*" else "")
  invisible(m)}
arear<-function(m,data){s<-m$summary.random$area[1:n,];data.frame(fbd_region=G$region,RR=exp(s$mean),P_gt1=sapply(m$marginals.random$area[1:n],function(x)1-inla.pmarginal(0,x)))}
ILL<-"ill_defined_death_share";OUTC<-"outside_care_share";stopifnot(ILL%in%names(DD),OUTC%in%names(DD))
# ── 88z2(2026-11-08, review 1회차 지적 → 결과를 본 뒤 추가한 사후 분석): P1 결과 = 고혈압성 제외 순환계(I00-I99 − I10-I13), E = E_circ − E_htnd(같은 연령 구간 간접표준화는 선형이라 차가 곧 비고혈압성 E)
#    P2 강제통제만 모형의 지역 공간 RR(공변량 12개 투입 전후 부산 잔차 비교). 산출 results_std3/S46_post_*.csv, S46_post_area.csv
B<-read.csv(file.path(OUTD,"..","CIRCB","panel_CIRCB.csv"),fileEncoding="UTF-8-BOM",stringsAsFactors=FALSE);B$fbd_region<-enc2utf8(B$fbd_region)
EB<-read.csv(file.path(ROOT,"02_패널","CIRCB_Estd2.csv"),fileEncoding="UTF-8-BOM",stringsAsFactors=FALSE);EB$fbd_region<-enc2utf8(EB$fbd_region)
X<-merge(B[,c("year","fbd_region","cases")],EB[,c("year","fbd_region","E_std2")],by=c("year","fbd_region"));names(X)[3:4]<-c("cases_circ","E_circ")
dn<-merge(DD,X,by=c("year","fbd_region"),all.x=TRUE,sort=FALSE);dn<-dn[order(dn$id),];stopifnot(!anyNA(dn$cases_circ),nrow(dn)==nrow(DD))
dn$cases<-dn$cases_circ-DD$cases;dn$E<-dn$E_circ-DD$E;stopifnot(all(dn$cases>=0),all(dn$E>0))
LOG("non-hypertensive circulatory cases %d (E sum %.1f)",sum(dn$cases),sum(dn$E))
m0<-fitX(MAINV,DD); m6<-summ("P1_nonhtn_circ","outcome_definition",fitX(MAINV,dn),"outcome = circulatory deaths excluding hypertensive diseases (I00-I99 minus I10-I13); E = E_circ - E_htnd",MAINV)
mf<-summ("P2_forced_only","reference",fitX(FORCED,DD),"forced controls only (residual geography before the 12 characteristics)",FORCED)
a<-merge(merge(arear(m0,DD),arear(m6,dn),by="fbd_region",suffixes=c("_main","_nonhtn")),setNames(arear(mf,DD),c("fbd_region","RR_forced","P_gt1_forced")),by="fbd_region")
write.csv(a,file.path(RES,"S46_post_area.csv"),row.names=FALSE,fileEncoding="UTF-8")
bs<-a[grepl("^부산",a$fbd_region),];LOG("Busan n %d: RR main %.2f-%.2f, nonhtn %.2f-%.2f (hot %d), forced-only %.2f-%.2f",nrow(bs),min(bs$RR_main),max(bs$RR_main),min(bs$RR_nonhtn),max(bs$RR_nonhtn),sum(bs$P_gt1_nonhtn>0.95),min(bs$RR_forced),max(bs$RR_forced))
LOG("done")
