import streamlit as st
import pandas as pd
from datetime import datetime
#import base64
import matplotlib.pyplot as plt
from pandas.plotting import lag_plot
from statsmodels.tsa.stattools import adfuller

#st.title('My Application')

# Streamlit UI setup
st.set_page_config(layout="wide")

st.markdown("<h1 style='text-align: center; color: black;'>Travel and Accommodation Budget Estimator</h1>", unsafe_allow_html=True)



 
# Create tabs


tab_titles = ['Best Deals', 'List of Events and Holidays', 'Flight Price Graphs']
tab1, tab2, tab3 = st.tabs(tab_titles)




 
# Add content to each tab
with tab1:
    #st.header('Topic A')
    st.markdown("<h2 style='text-align: left; color: black;'>Please Enter your Input on the Side Bar</h2>", unsafe_allow_html=True)
    st.markdown("<h2 style='text-align: left; color: black;'>Best Days to Travel and Price</h2>", unsafe_allow_html=True)
    
    #st.write('Please Give your Input on the Side Bar')
    st.sidebar.header("Trip Details")
    days_visit = st.sidebar.number_input('Number of Days in San Antonio:', min_value=2, value=3, step=1)
    month_visit = st.sidebar.selectbox('Month of Visit:', ('January', 'February', "March", 'April', 'May', 'June', "July", 'August', 'September', 'October', "November", 'December'))
    entry_airport = st.sidebar.selectbox('Departure Airport:', ('AUS', 'BOS', "DFW", 'FLL', 'IAH', 'JFK', "MIA", 'SEA', 'SFO', 'SLC'))

    # Convert month name to month number
    month_to_number = {month: index for index, month in enumerate(('January', 'February', "March", 'April', 'May', 'June', "July", 'August', 'September', 'October', "November", 'December'), start=1)}
    month_no = month_to_number[month_visit]
    flight_file_path = f"updated_flight_data_and_price_history_{entry_airport.lower()}_to_SAT.csv"
    hotel_file_path = "avg_price_by_date.csv"
    def read_data(flight_file, hotel_file):
        flight_df = pd.read_csv(flight_file)
        hotel_df = pd.read_csv(hotel_file)
    
    # Convert 'Date' in flight_df and 'check_in' in hotel_df to datetime
        flight_df['Date'] = pd.to_datetime(flight_df['Date']).dt.date
        hotel_df['check_in'] = pd.to_datetime(hotel_df['check_in']).dt.date
        hotel_df.rename(columns={'check_in': 'Date'}, inplace=True)
    
    # Ensure 'avg_price' in hotel_df is a float
        if 'avg_price' in hotel_df.columns:
            hotel_df['avg_price'] = hotel_df['avg_price'].astype(float)
    
        return flight_df, hotel_df

    # Function to find the top 5 cheapest stays with separate totals for flights and hotels
    def find_cheapest_stays_separate_totals(flight_df, hotel_df, month, n, top_k=5):
        combined_df = pd.merge(flight_df, hotel_df, on='Date')
        combined_df['Flight Total'] = combined_df['Price']
        combined_df['Hotel Total'] = combined_df['avg_price'] * n
        combined_df['Total Cost'] = combined_df['Flight Total'] + combined_df['Hotel Total']
    
        combined_df['Date'] = pd.to_datetime(combined_df['Date'])
        combined_df = combined_df[combined_df['Date'].dt.month == month]
    
        stays = []
        for i in range(len(combined_df) - n + 1):
            window = combined_df.iloc[i:i+n]
            flight_total = window['Price'].mean()
            hotel_total = window['avg_price'].mean() * n
            total_cost = flight_total + hotel_total
            stays.append((window['Date'].iloc[0], window['Date'].iloc[-1], flight_total, hotel_total, total_cost))
    
        stays.sort(key=lambda x: x[4])
        top_stays = stays[:top_k]
    
        formatted_stays = []
        for start_date, end_date, flight_total, hotel_total, cost in top_stays:
            formatted_stays.append(f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}: "
                               f"Flight total = ${flight_total:.2f}, Hotel total = ${hotel_total:.2f}, "
                               f"Total estimated cost = ${cost:.2f}")
    
        return formatted_stays
    flight_df, hotel_df = read_data(flight_file_path, hotel_file_path)
    top_stays = find_cheapest_stays_separate_totals(flight_df, hotel_df, month_no, days_visit)

# Display results
    st.markdown("<h2 style='text-align: left; color: black;'>Top 5 Cheapest Stays and Flights</h2>", unsafe_allow_html=True)
    #st.header("Top 5 Cheapest Stays")
    if top_stays:
        for stay in top_stays:
            st.text(stay)
    else:
        st.markdown("<h2 style='text-align: center; color: black;'>Please Select Future Months</h2>", unsafe_allow_html=True)
 
with tab2:
    st.markdown("<h2 style='text-align: center; color: black;'>List of Events Happening around San Antonio and National Holidays during the selected Month</h2>", unsafe_allow_html=True)
    #st.header('Topic B')
    #st.write('Graphs will be here')
    file_path = 'events.csv'
    df_events = pd.read_csv(file_path)
    df_events['Date'] = pd.to_datetime(df_events['Date'], format='%d-%m-%Y')


    df_selected_month = df_events[df_events['Date'].dt.month == month_no]

# Function to compile events and holidays
    def compile_events(df):
        national_holidays = []
        san_antonio_events = []
        six_flags_events = []
    
        for index, row in df.iterrows():
            if pd.notnull(row['National Holiday']):
                national_holidays.append(f"{row['National Holiday']} on {row['Date'].strftime('%m-%d-%Y')}")
            if pd.notnull(row['San Antonio Events']):
                san_antonio_events.append(f"{row['San Antonio Events']} on {row['Date'].strftime('%m-%d-%Y')}")
            if pd.notnull(row['Six Flags Events']):
                six_flags_events.append(f"{row['Six Flags Events']} on {row['Date'].strftime('%m-%d-%Y')}")
    
        return national_holidays, san_antonio_events, six_flags_events

    national_holidays_new, san_antonio_events_new, six_flags_events_new = compile_events(df_selected_month)

# Display events and holidays
    st.markdown("### National Holidays")
    for holiday in national_holidays_new:
        st.write(holiday)

    if san_antonio_events_new:
        st.markdown("<h2 style='text-align: center; color: black;'>San Antonio Events</h2>", unsafe_allow_html=True)
        for event in san_antonio_events_new:
            st.write(event)
    else:
        st.markdown("<h2 style='text-align: center; color: black;'>No San Antonio Events Happening this Month</h2>", unsafe_allow_html=True)

    if six_flags_events_new:
        st.markdown("<h2 style='text-align: center; color: black;'>Six Flags Events</h2>", unsafe_allow_html=True)
        for event in six_flags_events_new:
            st.write(event)
    else:
        st.markdown("<h2 style='text-align: center; color: black;'>No Six Flags Events happening in this month.</h2>", unsafe_allow_html=True)
        #st.write("")
 
with tab3:
    st.markdown("<h1 style='text-align: center; color: black;'>Graphs and Visaulizations that were used.</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: left; color: black;'>Daily Flight Prices Change Over Time</h3>", unsafe_allow_html=True)
    df = flight_df
    df['daily_change']=(df['Price'].pct_change())*100
    fig,ax=plt.subplots(figsize=(12,6))
    ax.spines[['top','right','left','bottom']].set_visible(False)
    plt.plot(df['daily_change'], label = 'Daily Returns')
    plt.legend(loc='best')
    plt.title('Price Daily Change Over Time')
    plt.show()
    st.pyplot(plt)
    st.markdown("<h3 style='text-align: left; color: black;'>Plotting Price Volatality of Flight Prices</h3>", unsafe_allow_html=True)
    def plot_price_volatility(price_df, window):
        daily_returns = price_df['Price'].pct_change()
    
        rolling_std = daily_returns.rolling(window=window).std()
    
        plt.figure(figsize=(12, 6))
        rolling_std.plot()
        plt.title(f'Volatility of Price (Rolling {window}-Day Std Dev)')
        plt.xlabel('Date')
        plt.ylabel('Volatility (Std Dev)')
        plt.grid(True)
        plt.show()
        st.pyplot(plt)

    plot_price_volatility(flight_df, 12)

    st.markdown("<h3 style='text-align: left; color: black;'>Autocorrelation Plaot</h3>", unsafe_allow_html=True)
    
    plt.figure()
    lag_plot(flight_df['Price'], lag=5)
    plt.title('Price - Autocorrelation plot with lag = 5')
    plt.show()
    st.pyplot(plt)

    #Test for staionarity
    def test_stationarity(timeseries):
        #Determing rolling statistics
        rolmean = timeseries.rolling(12).mean()
        rolstd = timeseries.rolling(12).std()
    #Plot rolling statistics:
        plt.plot(timeseries, color='blue',label='Original')
        plt.plot(rolmean, color='red', label='Rolling Mean')
        plt.plot(rolstd, color='black', label = 'Rolling Std')
        plt.legend(loc='best')
        plt.title('Rolling Mean and Standard Deviation')
        plt.show(block=False)
        print("Results of dickey fuller test")
        adft = adfuller(timeseries,autolag='AIC')
    # output for dft will give us without defining what the values are.
    #hence we manually write what values does it explains using a for loop
        output = pd.Series(adft[0:4],index=['Test Statistics','p-value','No. of lags used','Number of observations used'])
        for key,values in adft[4].items():
            output['critical value (%s)'%key] =  values
        #print(output)
        st.markdown("<h3 style='text-align: center; color: black;'>Statistic values of Dickey Fuller Test</h3>", unsafe_allow_html=True)
        st.dataframe(output)
        st.pyplot(plt)
    df_price = flight_df['Price']
    test_stationarity(df_price)
        ##st.pyplot(plt)
        ##st.write('Topic C content')
    


# Function to read flight and hotel data from CSV files




# File paths for flight and hotel data based on selected airport






# Read data and calculate cheapest stays



