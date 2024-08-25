import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import warnings
warnings.filterwarnings('ignore')

def calc_investment(monthly_investment, symbol, start_date, end_date, interval="1mo"):
    # yfinanceからドル円のデータを取得(1996-11-01 以降から取得可能)
    usdjpy = yf.download (tickers = "JPY=X", start = start_date, 
                            end = end_date, interval = interval)

    # 月ごとのリターン率を計算
    usdjpy['MonthlyReturnRate_usdjpy'] = (usdjpy['Close'] - usdjpy['Open']) / usdjpy['Open']
    # 期間を指定
    usdjpy = usdjpy[start_date:end_date]

    # yfinanceからデータを読み込む
    df = yf.download (tickers = symbol, start = start_date, 
                        end = end_date, interval = interval)

    # 期間を指定
    df = df[start_date:end_date]

    # 月ごとのリターン率を計算
    # df['MonthlyReturnRate'] = (df['Close'] - df['Open']) / df['Open']
    df.loc[:, 'MonthlyReturnRate'] = (df.loc[:, 'Close'] - df.loc[:, 'Open']) / df.loc[:, 'Open']


    # 結合
    df = pd.concat([df, usdjpy['MonthlyReturnRate_usdjpy']], axis=1)

    # 初期設定
    df['CumulativeReturn'] = 1
    df['MonthlyInvestment'] = monthly_investment
    df['CumulativeInvestments'] = df['MonthlyInvestment'].shift().cumsum()
    df['Asset_Balance'] = 0

    # シミュレーション
    for i in range(len(df)):
        if i > 0:
            df.iloc[i, df.columns.get_loc('CumulativeReturn')] = df.iloc[i-1, df.columns.get_loc('CumulativeReturn')] * (1 + df.iloc[i, df.columns.get_loc('MonthlyReturnRate')] + df.iloc[i, df.columns.get_loc('MonthlyReturnRate_usdjpy')])
        df.iloc[i, df.columns.get_loc('Asset_Balance')] = df.iloc[i, df.columns.get_loc('CumulativeInvestments')] * df.iloc[i, df.columns.get_loc('CumulativeReturn')]
        
        # 決算日に再投資 ニセナスは9/20日
        if df.index[i].month == 9 and df.index[i].day == 20:
            df.iloc[i, df.columns.get_loc('Asset_Balance')] += df.iloc[i, df.columns.get_loc('Asset_Balance')] * df.iloc[i, df.columns.get_loc('MonthlyReturnRate')]

    df.fillna(monthly_investment, inplace=True)
    asset_balance = df['Asset_Balance'].iloc[-1].astype(int)
    cumulative_investments = df['CumulativeInvestments'].iloc[-1].astype(int)
    
    return df, asset_balance, cumulative_investments

def plot(df, asset_balance, cumulative_investments, choice='matplotlib', plot=True):
    if choice == 'matplotlib':
        # グラフを描画
        plt.figure(figsize=(14, 7))
        plt.plot(df.index, df['Asset_Balance'], label='Future Value', color='green', marker='.')
        plt.plot(df.index, df['CumulativeInvestments'], label='Cumulative Investment', color='blue')
        plt.fill_between(df.index, 0, df['CumulativeInvestments'], color='skyblue', alpha=0.4)
        plt.title(f'Asset Balance: {asset_balance:,}\nInvestment principal:  {cumulative_investments:,}\nValuation gain/loss: {asset_balance - cumulative_investments:,}')
        plt.xlabel('Months from Start')
        plt.ylabel('Value (JPY)')
        plt.legend()
        plt.grid(True)
        plt.gcf().autofmt_xdate()  # x軸のラベルを斜めにして読みやすくする
        if not plot:
            return plt
        plt.show()
    else:
        # グラフを作成
        fig = go.Figure()

        # Future Valueの折れ線グラフを追加
        fig.add_trace(go.Scatter(x=df.index, y=df['Asset_Balance'], mode='lines+markers', name='Future Value', line=dict(color='green')))

        # Cumulative Investmentの折れ線グラフを追加
        fig.add_trace(go.Scatter(x=df.index, y=df['CumulativeInvestments'], mode='lines', name='Cumulative Investment', line=dict(color='blue')))

        # Cumulative Investmentの領域を塗りつぶす
        fig.add_trace(go.Scatter(x=df.index, y=df['CumulativeInvestments'], fill='tozeroy', fillcolor='skyblue', line=dict(color='rgba(0,0,0,0)'), showlegend=False))

        # レイアウト設定
        fig.update_layout(
            title=f'Asset Balance: {asset_balance:,}\nInvestment principal: {cumulative_investments:,}\nValuation gain/loss: {asset_balance - cumulative_investments:,}',
            xaxis_title='Months from Start',
            yaxis_title='Value (JPY)',
            legend=dict(x=0.02, y=0.98),
            grid=dict(),
            xaxis=dict(showline=True, showgrid=False),
            yaxis=dict(showline=True, showgrid=False),
            xaxis_tickangle=-45
        )

        # グラフを表示
        if not plot:
            return fig
        fig.show()

if __name__ == '__main__':
    # 毎月の積立額を設定
    monthly_investment = 20000
    # yfinanceのsymbol 
    symbol = "nasdaq"
    if symbol == "nasdaq":
        symbol = "^NDX"
    elif symbol == "sp500":
        symbol = "^GSPC"
    # 期間を指定
    start_date = "1998-01-01"
    end_date = "2024-07-01"
    df, asset_balance, cumulative_investments = calc_investment(monthly_investment=monthly_investment, symbol=symbol, start_date=start_date, end_date=end_date)
    plot(df, asset_balance, cumulative_investments, choice='', plot=True)