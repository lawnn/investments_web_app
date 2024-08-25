import streamlit as st, yfinance as yf, datetime
from investment import calc_investment, plot

st.title('Invest')

with st.form(key='Settings'):
    symbol = st.sidebar.text_input('Symbol', 'nasdaq')
    monthly_investment = st.sidebar.number_input('Monthly Investment', min_value=5000, max_value=10000000, value=10000, step=10000)
    start_date = st.sidebar.date_input('Start Date', datetime.date(1996, 11, 1), min_value=datetime.date(1996, 11, 1))
    end_date = st.sidebar.date_input('End Date')
    # interval = st.sidebar.text_input('Interval')
    
    submit_btn = st.form_submit_button('送信')
    cancel_btn = st.form_submit_button('キャンセル')

    # data = yf.download (tickers = symbol, start = start_date, 
    #                         end = end_date, interval = interval)
    # data

    # 毎月の積立額を設定
    # monthly_investment = 20000
    # yfinanceのsymbol 
    symbol = "nasdaq"
    if symbol == "nasdaq":
        symbol = "^NDX"
    elif symbol == "sp500":
        symbol = "^GSPC"
    # 期間を指定
    start_date = start_date.strftime('%Y-%m-%d')
    end_date = end_date.strftime('%Y-%m-%d')

    if submit_btn:
        df, asset_balance, cumulative_investments = calc_investment(monthly_investment=monthly_investment, symbol=symbol, start_date=start_date, end_date=end_date)
        fig = plot(df, asset_balance, cumulative_investments, choice='', plot=False)
        st.plotly_chart(fig)
        st.write(df)