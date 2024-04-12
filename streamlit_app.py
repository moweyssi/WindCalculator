from EST_tidy_data import makedf
import numpy as np
import pandas as pd
import altair as alt
from io import BytesIO
import pandas as pd
import streamlit as st
import pgeocode
from PIL import Image

country = pgeocode.Nominatim("gb")
MonthDict={ 1 : "January", 2 : "February", 3 : "March", 4 : "April", 5 : "May", 6 : "June", 7: "July",
            8 : "August", 9 : "September", 10 : "October", 11 : "November",12 : "December"}
invMonthDict = {v: k for k, v in MonthDict.items()}
PropertyDict={
    "g0":"General Business", "g1":"Weekday Business","g2":"Evening Business","g3":"Continuous Business",
    "g4":"Shop or Barber","g5":"Bakery","g6":"Weekend Business",
    "l0":"General Farm","l1":"Dairy or Livestock Farm", "l2":"Other Farm", "h0":"Household"}
invPropertyDict = {v: k for k, v in PropertyDict.items()}

start = 2013
end = 2016
st.set_page_config(layout="wide")

#hide_streamlit_style = """
#            <style>
#            #MainMenu {visibility: hidden;}
#            footer {visibility: hidden;}
#            </style>
#            """
#st.markdown(hide_streamlit_style, unsafe_allow_html=True) 

logo = Image.open('logo.png')
col1, col2, col3 = st.columns([4,12,1.1])
@st.cache
def to_the_shop_to_get_your_PVGIS_data(property_type,lat,lon,annual_consumption,turbine_height,land_cover_type):
    return makedf(invPropertyDict[property_type],lat, lon, annual_consumption,start, end, turbine_height,land_cover_type)

with col1:
    location = st.radio("How to imput location?",("Coordinates","Postcode"),horizontal=True,label_visibility='hidden')
    if location == "Coordinates":
        lat = float(st.text_input('Latitude', value=0))
        lon = float(st.text_input('Longitude',value=0))
    elif location == "Postcode":
        postcode = st.text_input('Postcode')
        if postcode!="":
            postcode_data = country.query_postal_code(postcode)
            lat = float(postcode_data["latitude"])
            lon = float(postcode_data["longitude"])
            st.code("Latitude  = "+str(lat)+"\nLongitude = "+str(lon))
        else:
            lat,lon=0,0
    with st.form(key="Input parameters"):
        property_type = st.selectbox('What is the property type?',PropertyDict.values())
        annual_consumption = st.number_input('Annual property consumption [kWh]',value=12000,step=1)
        PV_max_power = st.number_input('PV system peak power [kWp]',value=5,step=1)
        turbine_height = st.number_input('Wind turbine height [m]',value=5,step=1)
        land_cover_type = st.number_input('Land cover type',value=0,step=1)
        button = st.form_submit_button(label="Plot the plot!")
            
with col2:
    if (lon,lat) == (0,0):
        """
        # Welcome to the PVGIS-BDEW Tool!
        Made with :heart: by the Energy Saving Trust
        """
        st.markdown('<sub><sup>All errors are 95% confidence intervals (i.e. 1.96 x standard error on the mean)</sub></sup>',unsafe_allow_html=True)
        with col3:
            """##\n##"""
            st.image(logo)
    else:
        df, average,cloudy, sunny, bdew_demand, t, yearly_gen, yearly_use = to_the_shop_to_get_your_PVGIS_data(
                    property_type,lat,lon,annual_consumption,turbine_height,land_cover_type)
        month_slider = st.select_slider("Month", MonthDict.values(),label_visibility='hidden')
        month = invMonthDict[month_slider]
        day = st.radio("What day?",('workday','saturday','sunday'),horizontal=True,label_visibility='hidden')

        stats = ('Annual PV generation = ' + str(yearly_gen[0])+' ± '+str(yearly_gen[1])+' kWh             '+
                'PV energy used per year = '+str(yearly_use[0])+' ± '+str(yearly_use[1])+' kWh')
        st.code(stats)
        PV = alt.Chart(df[month-1]).mark_line(strokeWidth=6).encode(
        x='time',
        y=alt.Y('PV generation'))#,scale=alt.Scale(domain=(0,PV_max_power*2/3))))

        error = alt.Chart(df[month-1]).mark_area(opacity=0.2).encode(x='time',y='PV min',y2='PV max')
        if day == 'workday':
            BDEW = alt.Chart(df[month-1]).mark_line(strokeWidth=6,color='red').encode(x='time',y='BDEW workday')
        elif day == 'saturday':
            BDEW = alt.Chart(df[month-1]).mark_line(strokeWidth=6,color='red').encode(x='time',y='BDEW saturday')
        elif day == 'sunday':
            BDEW = alt.Chart(df[month-1]).mark_line(strokeWidth=6,color='red').encode(x='time',y='BDEW sunday')

        chart = PV+error +BDEW
        chart.height=530
        st.altair_chart(chart,use_container_width=True)

with col3:
    if (lon,lat)!=(0,0):
        """##\n##"""
        st.image(logo)
        def export_xlsx(df):
            output = BytesIO()
            year_df = pd.DataFrame(
                index = ['a','b','c'],
                columns = ['Annual \nDemand: ' + str(annual_consumption)+' kWh',
                 'Annual PV \ngeneration: ' + (str(yearly_gen[0])+' ± '+str(yearly_gen[1])+' kWh'),
                 ('Annual PV \n used: ' + str(yearly_use[0])+' ± '+str(yearly_use[1])+' kWh')])
            frames = [average,cloudy,sunny,bdew_demand,year_df]
            start_row = 1
            writer = pd.ExcelWriter(output, engine='xlsxwriter')
            sheet_name='Monthly Percentages'
            for df in frames:  # assuming they're already DataFrames
                df.to_excel(writer, sheet_name, startrow=start_row, startcol=0, index=False)
                start_row += len(df) + 2  # add a row for the column header?
                for column in df:
                    column_width = max(df[column].astype(str).map(len).max(), len(column))
                    col_idx = df.columns.get_loc(column)
                    writer.sheets[sheet_name].set_column(col_idx, col_idx, column_width)
            writer.close()
            processed_data = output.getvalue()
            return processed_data

        toexport = export_xlsx(df)
        """##\n##\n"""
        st.text("Download:\n")
        st.download_button(label='📥',
                                    data=toexport ,
                                    file_name= invPropertyDict[property_type]+"_"+str(annual_consumption)+"kWh_"+str(turbine_height)+"m_turbine.xlsx")
        

        




