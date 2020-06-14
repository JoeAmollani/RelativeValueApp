# -*- coding: utf-8 -*-
"""
Created on Sun Feb 23 13:41:38 2020

@author: Joen
"""



import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.tsa.stattools as ts


# sns.set_style('whitegrid',{"axes.grid": False})
# plt.rc('figure', figsize=(15,10))
# plt.rc('savefig', transparent=True)
# plt.rc('xtick', labelsize=14) 
# plt.rc('ytick', labelsize=14)

# HGIGrey   = '#444E55'
# HGIRed    = '#951826'
# HGIOrange = '#ea7600'
# HGIYellow = '#ffcd00'
# HGIBlue   = '#007398'
# HGILgrey  = '#768692'
# HGIGreen  = '#92D050'
# HGIPurple  = '#B1A0C7'

# HGICycle = [HGIGrey, HGIRed, HGIOrange, HGIBlue, HGIYellow, HGILgrey,HGIGreen,HGIPurple]
# plt.rc('axes', prop_cycle=cycler('color', HGICycle))

# os.getcwd()
# os.chdir(r'C://Users//Joen//Desktop//Macroeconomic Data')

# TimeSeries = pd.ExcelFile('FX_USD.xlsx').parse(index_col=0) 
# Assets     = list(itertools.combinations(TimeSeries.columns,2))

# Asset_A = 'EURUSD curncy'
# Asset_B = 'GBPUSD curncy'

def Relative_Value_Backtest(TimeSeries, Asset_A, Asset_B, window, St_Dev_Ratio,Rebalance):
    
#    window = 90
#    St_Dev_Ratio = 2

    TimeSeries = TimeSeries[[Asset_A,Asset_B]]
    TimeSeries['Spread'] = TimeSeries[Asset_A] - TimeSeries[Asset_B]
    TimeSeries[Asset_A+str(' PnL')] = np.log(TimeSeries[Asset_A]) - np.log(TimeSeries[Asset_A].shift(1)).fillna(0)
    TimeSeries[Asset_B+str(' PnL')] = np.log(TimeSeries[Asset_B]) - np.log(TimeSeries[Asset_B].shift(1)).fillna(0)
    
    def bollinger_strat(data, window, no_of_std):
        rolling_mean = data['Spread'].rolling(window).mean()
        rolling_std = data['Spread'].rolling(window).std()
        data['Bollinger High'] = rolling_mean + (rolling_std * no_of_std)
        data['Bollinger Low'] = rolling_mean - (rolling_std * no_of_std) 
        data['Rolling Mean'] = data['Spread'].rolling(window).mean()   
        return(data)
    
    Beta = pd.DataFrame([])
    i=0
    for i in range(len(TimeSeries)-window):
        Backtest_Res = TimeSeries.iloc[i:i+window]
        slope, intercept, r_value, p_value, std_err = stats.linregress(Backtest_Res[Asset_A+str(' PnL')],Backtest_Res[Asset_B+str(' PnL')])
        Beta = Beta.append(pd.DataFrame([slope]))
        i+=1    
    
    Beta = Beta.set_index(TimeSeries.index[window:len(TimeSeries)])
    Beta.columns = ['Ratio']
    
    TimeSeries = bollinger_strat(TimeSeries,window,St_Dev_Ratio).dropna(0)
    TimeSeries = TimeSeries.join(Beta)
    
    row = TimeSeries
    i=0
    PnL = []
    Trades = []
    Ratio = 1
    if Rebalance == 'Fixed':
        try:
            while i < len(row):
                if row['Spread'][i] > row['Bollinger High'][i]:  
                    while row['Spread'][i] > row['Rolling Mean'][i]:
                        PnL.append(row[Asset_A+str(' PnL')][i] - Ratio * row[Asset_B+str(' PnL')][i])
                        Trades.append(str('Long'+ Asset_A + '- Short' +str(Asset_B)))
                        i+=1
                elif row['Spread'][i] < row['Bollinger Low'][i] :    
                    while row['Spread'][i] < row['Rolling Mean'][i]:
                        PnL.append(Ratio * row[Asset_B+str(' PnL')][i] - row[Asset_A+str(' PnL')][i])
                        Trades.append(str('Long'+ Asset_B + '- Short' +str(Asset_A)))                
                        i+=1            
                else:
                    PnL.append(0)
                    Trades.append(str('No trade'))
                    i+=1
        except:
            print('Run')

    elif Rebalance == 'Rolling':
        try:
            while i < len(row):
                if row['Spread'][i] > row['Bollinger High'][i]:  
                    while row['Spread'][i] > row['Rolling Mean'][i]:
                        PnL.append(row[Asset_A+str(' PnL')][i] - row['Ratio'][i] * row[Asset_B+str(' PnL')][i])
                        Trades.append(str('Long'+ Asset_A + '- Short' +str(Asset_B)))
                        i+=1
                elif row['Spread'][i] < row['Bollinger Low'][i] :    
                    while row['Spread'][i] < row['Rolling Mean'][i]:
                        PnL.append(row['Ratio'][i] * row[Asset_B+str(' PnL')][i] - row[Asset_A+str(' PnL')][i])
                        Trades.append(str('Long'+ Asset_B + '- Short' +str(Asset_A)))                
                        i+=1            
                else:
                    PnL.append(0)
                    Trades.append(str('No trade'))
                    i+=1
        except:
            print('Run')        
    else:
        pass
        
    Trades = pd.DataFrame(Trades,columns = ['Trade']).set_index(row.index)
    Strategy = pd.DataFrame(PnL,columns = ['Strategy PnL']).set_index(TimeSeries.index)
    Strategy = Strategy.join(Trades)
    
    
    Backtest_Results = row[[Asset_A, Asset_B,Asset_A+str(' PnL'),Asset_B+str(' PnL') ,'Spread','Bollinger High','Bollinger Low', 'Rolling Mean']].join(Strategy)
    
    Backtest_Results['Cummulative'] = Backtest_Results['Strategy PnL'].cumsum()*100

    return(Backtest_Results)

def Rolling_Beta(Data, Asset_A, Asset_B,window):
    
    Beta = pd.DataFrame([])
    i=0
    for i in range(len(Data)-window):
        Backtest_Results = Data.iloc[i:i+window]
        slope, intercept, r_value, p_value, std_err = stats.linregress(Backtest_Results[Asset_A+str(' PnL')],Backtest_Results[Asset_B+str(' PnL')])
        Beta = Beta.append(pd.DataFrame([slope]))
        i+=0
    Beta.columns = [str(window)+'D Rolling Beta' ]
    Beta = Beta.set_index(Data.index[window:len(Data)])
    return(Beta)



def Cointegration_Test(Data, Asset_A, Asset_B,window):
    Pvalue = pd.DataFrame([])
    i=0
    for i in range(len(Data)-window):
        Backtest_Results = Data.iloc[i:i+window]
        coin_result = ts.coint(Backtest_Results[Asset_A+str(' PnL')],Backtest_Results[Asset_B+str(' PnL')])
        Pvalue = Pvalue.append(pd.DataFrame([coin_result[1]]))
        i+=0
    Pvalue.columns = [str(window)+'D Rolling Beta' ]
    Pvalue = Pvalue.set_index(Data.index[window:len(Data)])
    return(Pvalue)

def Graph_Results(Backtest_Results,Asset_A,Asset_B):
    
    fig, axes = plt.subplots(nrows=2, ncols=2,figsize=(25,10))
    pd.pivot_table(Backtest_Results, values='Cummulative', index=Backtest_Results.index,columns=['Trade']).plot(ax=axes[0,0],title = 'Strategy Cummulative Return')
    Backtest_Results[['Bollinger Low','Bollinger High','Rolling Mean','Spread']].plot(ax=axes[0,1],title = 'Signals')
    pd.pivot_table(Backtest_Results, values=Asset_A, index=Backtest_Results.index,columns=['Trade']).plot(ax=axes[1,0],title = Asset_A)
    pd.pivot_table(Backtest_Results, values=Asset_B, index=Backtest_Results.index,columns=['Trade']).plot(ax=axes[1,1],title = Asset_B)






