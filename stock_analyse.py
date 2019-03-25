from sqlalchemy import create_engine
import pandas as pd
import datetime
engine = create_engine('sqlite:///stocks.db', echo=False)


def stock_info(symbols):
    big_df = pd.DataFrame()

    for symbol in symbols:
        # df = pd.DataFrame(columns=['Date'])

        df = pd.read_csv("stock_data/{}.us.txt".format(symbol), parse_dates=True,
                          usecols=['Date','Close','Volume'], na_values=['nan'])
        #    print(" No such file")

        df['Date'] = pd.to_datetime(df['Date'])
        df.rename(columns={"Date":"Date",
                           "Close":symbol+"Close",
                           "Volume":symbol+"Volume"}, inplace=True)

        start_date = '2013-01-01'
        end_date = '2018-03-31'

        mask =(df['Date'] > start_date) & (df['Date'] <= end_date)
        df = df.loc[mask]

        df.set_index(['Date'], inplace=True)

        big_df = pd.concat([big_df, df], axis=1)

    print(big_df.head())

    ipo_dict = {}
    list_col = []
    list_ipo = []

    for symbol in symbols:
        column_name = symbol + "Close"
        list_col.append(column_name)

    # print('listcol is',list_col)

    for i in list_col:

        ipo_date = big_df[i].first_valid_index().date()

        if ipo_date > datetime.date(2013,1,3):
            comp_name = str(i.split("Close")[0])
            ipo_dict[comp_name] = ipo_date.strftime("%Y-%m-%d")

    for key in ipo_dict.keys():
        list_ipo.append(key + 'Close')
        list_ipo.append(key+'Volume')

    # print("ipo columns is", list_ipo)

    df_ipo = big_df[list_ipo]

    # Creating the table ipo_stocks

    create_table(df_ipo)


    return ipo_dict


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
    print(df1.head())
    return df1


    


#symbols=['zen','SNAP']
#dict1 = stock_info(symbols)
# print(dict1)
# perf_graph()
# print_table()
#df_dummy = bokeh_plot('zen')
#df_dummy = bokeh_plot('SNAP')



