from sqlalchemy import create_engine
import pandas as pd
import datetime
import re
import os
# abbv ipo year changed to 2013 . AWP.US.TXT deleted, AIC.US.TXT deleted, CIC.US.TXT deleted

engine = create_engine('sqlite:///stocks.db', echo=False)


def stock_info(starting_year, ending_year):

    print(starting_year,ending_year)

    symbols = get_symbols_ipo(starting_year, ending_year)
    # print("stocks length in stock_info", len(symbols))
    big_df = pd.DataFrame()

    for symbol in symbols:
        # df = pd.DataFrame(columns=['Date'])

        try:


            df = pd.read_csv(
                            "stock_data/{}.us.txt".format(symbol), parse_dates=True,
                            usecols=['Date','Close', 'Volume'], na_values=['nan']
                            )
            df['Date'] = pd.to_datetime(df['Date'])
            df.rename(columns={"Date":"Date",
                               "Close":symbol+"Close",
                               "Volume":symbol+"Volume"}, inplace=True)

            # x = datetime.datetime(int(starting_year), 1, 1)
            # strt_date = x
            start_date = datetime.datetime(int(starting_year), 1, 1)
            end_date = datetime.datetime(int(ending_year), 12, 31)

            mask =(df['Date'] > start_date) & (df['Date'] <= end_date)
            df = df.loc[mask]

            df.set_index(['Date'], inplace=True)

            big_df = pd.concat([big_df, df], axis=1)

        except ValueError:

            print("error happened while reading ", symbol)

    # big_df.to_csv('list.csv')
    ipo_dict = {}
    list_col = []
    list_ipo = []

    for symbol in symbols:
        column_name = symbol + "Close"
        list_col.append(column_name)

    try:
        for i in list_col:
            ipo_date = big_df[i].first_valid_index().date()
            date_col = ipo_date.strftime("%Y-%m-%d")
            ipo_price = big_df[i].loc[date_col]
            print(ipo_price)
            # ipo_price = big_df[ipo_date.strftime("%Y-%m-%d")][i]

            #  if ipo_date > datetime.date(2013,1,3):

            if ipo_date > datetime.date(int(starting_year),1,1):
                comp_name = str(i.split("Close")[0])
                df_dummy = pd.read_csv("companylist.csv", usecols=["Symbol", "Name"], na_values=['nan'],index_col=0)
                comp_name_upper = comp_name.upper()
                print(df_dummy.head())
                ipo_comp_name = df_dummy.loc[comp_name_upper,'Name']
                ipo_dict[comp_name] = [ipo_comp_name, ipo_date.strftime("%Y-%m-%d"), ipo_price]

    except AttributeError:
        print("Error while reading the stock ", i)


    for key in ipo_dict.keys():
        list_ipo.append(key + 'Close')
        list_ipo.append(key+'Volume')


    df_ipo = big_df[list_ipo]

    # Creating the table ipo_stocks

    create_table(df_ipo)
    sorted_ipo = dict(sorted(ipo_dict.items()))
    # print(sorted_ipo)
    return sorted_ipo






def create_table(df):

    # df.sort_values(by='Date', ascending=False, inplace=True)
    df.to_sql('ipo_stocks', con=engine, if_exists='replace')


def bokeh_plot(name):

    df = pd.read_sql_table('ipo_stocks', con=engine, index_col='Date')
    df.sort_values(by=['Date'], ascending=False, inplace=True)

    list1 = [name + 'Close', name + 'Volume']
    df1 = df[[list1[0],list1[1]]]
    # print(df1.index)
    '''
    starting_date = '2017-04-01'
    ending_date = '2018-03-29'

    mask = (df1['Date'] > starting_date) & (df1['Date'] <= ending_date)
    df1 = df1.loc[mask]
    '''
    return df1


def get_symbols_ipo(starting_year, ending_year):

    list_stocks = []
    stocks_nasdaq = []
    stocks_not_avlb = []
    path = "stock_data/"
    for filename in os.listdir(path):
        ticker_names = re.search(r'(^[a-zA-Z]+)', filename).group(0)
        list_stocks.append(ticker_names)

    df_ipo = pd.read_csv("companylist.csv", usecols=["Symbol", "IPOyear"], na_values=['nan'])
    df_ipo['IPOyear'] = pd.to_datetime(df_ipo['IPOyear'], format='%Y').dt.strftime('%Y')
    #print(df_ipo.head())
    start_year = starting_year # '2013'
    end_year = ending_year # '2018'

    mask = (df_ipo['IPOyear'] >= start_year) & (df_ipo['IPOyear'] <= end_year)
    df = df_ipo.loc[mask]

    dflist = list(df['Symbol'])

    dflist_lowercase = [v.lower() for v in dflist]
    print(len(dflist_lowercase))

    '''
    for stock in list_stocks:
        if stock in dflist_lowercase:
            stocks_nasdaq.append(stock)
    
            
    '''

    for stock in dflist_lowercase:
        if stock in list_stocks:
            stocks_nasdaq.append(stock)
        else:
            stocks_not_avlb.append(stock)

    #  print("BLAAHAHAHHAH",len(stocks_nasdaq))
    # print(start_year,end_year, len(stocks_nasdaq))
    # print(stocks_nasdaq[0:10])

    # print("STOCKS nt available", stocks_not_avlb)
    return stocks_nasdaq[0:25]













