import pandas as pd
import numpy as np
from numpy import *
import matplotlib.pyplot as plt

import statsmodels as sm
from statsmodels import api
from statsmodels import tsa

#更改最大的递归栈限至
import sys
sm.sys.setrecursionlimit(10000)



class timeSeries(object):
    pass


#把每个样本组的元素做成一个新的区间
#一个基本单位是一个样本组的一个工作日数据
def sampleIntervalModcChoice(pd.core.series.Series):
    arma_mod = sm.api.tsa.ARMA(pd.core.series.Series,order=(1,1),missing='drop')
    arma_res = arma_mod.fit()
    arma_aic = arma_res.aic

    ar_mod = sm.api.tsa.ARMA(pd.core.series.Series,order=(0,1),missing='drop')
    ar_res = self.ar_mod.fit()
    ar_aic = self.ar_res.aic

    ma_mod = sm.api.tsa.ARMA(pd.core.series.Series,order=(1,0),missing='drop')
    ma_res = self.ma_mod.fit()
    ma_aic = self.ma_res.aic

    min_aic = min(ma_aic,arma_aic,ar_aic)
    for i in [ma_mod,arma_mod,ar_mod]:
        if (min_aic == i.fit().aic):
             print('best mod is:' + str(i))
             best_mod = i
    best_res = best_mod.fit()
    best_params = best_res.params
    return(best_res.summary())
    

class stock(timeSeries):

    def __init__(self,path,name,code,data=None,price=None,rateLog=None):
        self.__path  = path
        self.__name  = name
        self.__code  = code

        self.data    = pd.read_excel(self.__path) #数据整理
        self.data.index = self.data['交易日期']
        self.price   =    self.data['收盘点位']
        self.price   =    self.price.sort_index(ascending=True)  #这里特别提一下，我们需要把数据处理为升序排列

#创建空的DataFrame和index，便于数据的转运，同时把2007-01-01之前的所有数据裁掉
        self.voidDataFrame = pd.DataFrame(columns=['MON','TUE','WEN','THU','FRI'])
        self.indexCalendar  = pd.date_range(start='2007-01-01',end='2018-12-31',freq='D')
        self.priceCalendar  = self.price.reindex(self.indexCalendar)
        self.indexTradeDays = pd.date_range(start='2007-01-01',end='2018-12-31',freq='B')
        self.priceTradeDays = self.price.reindex(self.indexTradeDays)
        
        
#给出了每周5个不同工作日的交易信息的序列然后给出一个数组
        self.priceMon =pd.Series(self.price,pd.date_range(start='2007-01-01',end='2018-12-31',freq='W-MON'))
        self.priceTue =pd.Series(self.price,pd.date_range(start='2007-01-01',end='2018-12-31',freq='W-TUE'))
        self.priceWed =pd.Series(self.price,pd.date_range(start='2007-01-01',end='2018-12-31',freq='W-WED'))
        self.priceThu =pd.Series(self.price,pd.date_range(start='2007-01-01',end='2018-12-31',freq='W-THU'))
        self.priceFri =pd.Series(self.price,pd.date_range(start='2007-01-01',end='2018-12-31',freq='W-FRI'))
        self.priceWD  = [self.priceMon,self.priceTue,self.priceWed,self.priceThu,self.priceFri]

        #确定第一个交易日，待补充一个根据日期确定模型选择范围的语句，然后写回报率序列
#并且根据第一个交易日的相关信息，写出后面的样本分组
        from math import isnan
        for i in range(0,200):                                       #一年的日期，如果超过了这个数字，那么肯定就不再我们的考虑范围之内了
            if isnan(self.priceFri[i])==False:                            #找到第一个不是nan的周五
                self.firstTradeDay = self.priceFri.index[i]                    #取得相应的日期,timeStamp
                for j in range(1,5):                                 #定义1：5的序列
                    if isnan(self.priceTradeDays[self.firstTradeDay+j])==True: #带回到交易日数据下面五个都是非交易日则确定
                        i = i+1
                        continue
                    else:
                        pass
            break
#根据给出的第一交易日判定方法，把“第一交易日”之前数据全部截取出去，并且给出回报率的五个序列
        self.priceCalendar  = self.priceCalendar[self.firstTradeDay:]
        self.priceCorrected = self.price[self.firstTradeDay:]                      #把第一交易日后面的完全剔除
        self.rateLog   = pd.Series(np.log(tuple(self.priceCorrected/self.priceCorrected.shift(1))),
                                   index=self.priceCorrected.index)           #取对数收益率，日期是从第一交易日到18年末
        self.rateLog   =  self.rateLog[1:]                                    #顺便裁除掉前面的收益率
        self.rateLogCalendar = self.rateLog.reindex(self.priceCalendar.index)[3:]  #第一个应该是周一
        self.rateLogCalendarStore = self.rateLogCalendar
    
#五个对数收益率序列已经出来了
        self.rateLogMon =pd.Series(self.rateLog,pd.date_range(start=self.firstTradeDay,end='2018-12-31',freq='W-MON'))
        self.rateLogTue =pd.Series(self.rateLog,pd.date_range(start=self.firstTradeDay,end='2018-12-31',freq='W-TUE'))
        self.rateLogWed =pd.Series(self.rateLog,pd.date_range(start=self.firstTradeDay,end='2018-12-31',freq='W-WED'))
        self.rateLogThu =pd.Series(self.rateLog,pd.date_range(start=self.firstTradeDay,end='2018-12-31',freq='W-THU'))
        self.rateLogFri =pd.Series(self.rateLog,pd.date_range(start=self.firstTradeDay,end='2018-12-31',freq='W-FRI'))
        self.rateLogWD  = [self.rateLogMon,self.rateLogTue,self.rateLogWed,self.rateLogThu,self.rateLogFri]
#某个样本组必须第一周和最后一周均为完整交易周，而且时间间隔大于52周
#（第一个样本数据以及后面四个为交易日，以及52周*7天=364天之后同样，如果没有这个数据就加5再尝试）
        self.sampleInterval = [] #建立一个数组
        intervalBool = 1
        while(bool(intervalBool)):
            judgeNum = 364
            if(len(self.rateLogCalendar)<=judgeNum):
                intervalBool = 0
                if (len(self.rateLogCalendar)==0):
                    print('样本数少于364，目前不做分析')        
            else:
                for i in range(0,len(self.rateLogCalendar)-judgeNum-5):      #因为采用日历日，所以根本不用考虑周几
                    if(len(self.rateLogCalendar)<=judgeNum):
                        intervalBool = 0
                        break                 
                    for j in range(1,5):                                     #只要今天之后五天都是交易日，那么今天肯定是周日
                        if(isnan(self.rateLogCalendar[judgeNum+j])==True):   #我们需要一个周日
                            i = i+1
                            continue
                    judgeNum = judgeNum+i+5                                       #一直到下个周的周五，都划入本组
                    print(judgeNum)
                    self.sampleInterval.append(self.rateLogCalendar[:judgeNum])   #构建一个样本区间分组，新添加元素作为第一个区间
                    self.rateLogCalendar = self.rateLogCalendar[judgeNum+3:]      #原来的数组去掉已经被添加到样本区间的部分继续判定

        self.finalStart = self.sampleInterval[-1].index[0]
        self.finalEnd   = self.rateLogCalendar.index[-1]
        self.sampleInterval[-1] = self.rateLogCalendarStore[self.finalStart:self.finalEnd ]
        
#这里已经给出了分组的方法，进行分组模拟
        self.sampleIntervalMon = []
        self.sampleIntervalTue = []
        self.sampleIntervalWed = []
        self.sampleIntervalThu = []
        self.sampleIntervalFri = []
        for i in range(0,len(self.sampleInterval)-1):
            self.sampleIntervalMon.append( pd.Series(self.sampleInterval[i],
                                                   pd.date_range(start=self.sampleInterval[i].index[0],
                                                                 end  =self.sampleInterval[i].index[-1],
                                                                 freq='W-MON')))
            self.sampleIntervalTue.append( pd.Series(self.sampleInterval[i],
                                                   pd.date_range(start=self.sampleInterval[i].index[0],
                                                                 end  =self.sampleInterval[i].index[-1],
                                                                 freq='W-TUE')))
            self.sampleIntervalWed.append( pd.Series(self.sampleInterval[i],
                                                   pd.date_range(start=self.sampleInterval[i].index[0],
                                                                 end  =self.sampleInterval[i].index[-1],
                                                                 freq='W-WED')))
            self.sampleIntervalThu.append( pd.Series(self.sampleInterval[i],
                                                   pd.date_range(start=self.sampleInterval[i].index[0],
                                                                 end  =self.sampleInterval[i].index[-1],
                                                                 freq='W-THU')))
            self.sampleIntervalFri.append( pd.Series(self.sampleInterval[i],
                                                   pd.date_range(start=self.sampleInterval[i].index[0],
                                                                 end  =self.sampleInterval[i].index[-1],
                                                                 freq='W-FRI')))
        
        self.sampleIntervalWD = [self.sampleIntervalMon,
                                 self.sampleIntervalTue,
                                 self.sampleIntervalWed,
                                 self.sampleIntervalThu,
                                 self.sampleIntervalFri]
        for i in self.sampleIntervalWD:
            i = sampleIntervalElement()

        
#分组已经完成，下面利用样本进行拟合

        

                
        def get_path(self):
            print(self.__path)
        def get_name(self):
            print(self.__name)
        def get_code(self):
            print(self.__code)
        
    
path_huaxian = r'C:\Users\dell\Desktop\huaxian\882570.xlsx'
huaxian = stock(path= path_huaxian,name='化纤指数',code=882570)

print(huaxian.sampleIntervalFri[0].best_mod)

#改写新的
    
#分组
    

    
                
            
        
        
        
                                   
    
