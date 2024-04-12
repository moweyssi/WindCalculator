from EST_BDEW import get_BDEW
from EST_PVGIS import PV_power
import numpy as np
import pandas as pd

MonthDict={ 1 : "January", 2 : "February", 3 : "March", 4 : "April", 5 : "May", 6 : "June", 7: "July",
            8 : "August", 9 : "September", 10 : "October", 11 : "November",12 : "December"}

PropertyDict={
    "g0":"General Business", "g1":"Weekday Business","g2":"Evening Business","g3":"Continuous Business",
    "g4":"Shop / Barber","g5":"Bakery",	 "g6":"Weekend Business","g7":"Mobile Phone Transmitter Station",
    "l0":"General Farm","l1":"Dairy / Livestock Farm", "l2":"Other Farm", "h0":"Household"}

def makedf(property_type, lat, lon, annual_consumption,start_year, end_year, turbine_height):

    generation_hourly, error_hourly, yearly_generation, yearly_used  = PV_power(
        start_year,end_year,lat,lon,property_type, annual_consumption, turbine_height
        )
    time_hourly = np.linspace(0,24,24)
    time = np.linspace(0,24,24*4)
    workday, saturday, sunday = get_BDEW(property_type,2022,annual_consumption)
    df_list = []
    bdew_demand = {
        "Workday\n Demand [kWh]": [],
        "Saturday\n Demand [kWh]": [],
        "Sunday\n Demand [kWh]": [],
    }
    average = {
        "PV\n Generation [kWh]": [],
        "Workday Demand\n Covered by PV": [],
        "Saturday Demand\n Covered by PV": [],
        "Sunday Demand\n Covered by PV": [],
        "Workday PV\n Used by Demand": [],
        "Saturday PV\n Used by Demand": [],
        "Sunday PV\n Used by Demand": [],
    }
    min = {
        "Cloudy\n PV\n Generation [kWh]": [],
        "Cloudy\n Workday Demand\n Covered by PV": [],
        "Cloudy\n Saturday Demand\n Covered by PV": [],
        "Cloudy\n Sunday Demand\n Covered by PV": [],
        "Cloudy\n Workday PV\n Used by Demand": [],
        "Cloudy\n Saturday PV\n Used by Demand": [],
        "Cloudy\n Sunday PV\n Used by Demand": [],
    }
    max = {
        "Sunny\n PV\n Generation [kWh]": [],
        "Sunny\n Workday Demand\n Covered by PV": [],
        "Sunny\n Saturday Demand\n Covered by PV": [],
        "Sunny\n Sunday Demand\n Covered by PV": [],
        "Sunny\n Workday PV\n Used by Demand": [],
        "Sunny\n Saturday PV\n Used by Demand": [],
        "Sunny\n Sunday PV\n Used by Demand": [],
    }

    for month in range(12):
        df=pd.DataFrame()

        """Convert PVGIS data to 15 minute resolution"""
        error = np.interp(time,time_hourly,error_hourly[month])
        generation = np.interp(time,time_hourly,generation_hourly[month])
        generation_min = generation-2*error
        generation_max = generation+2*error

        """Find % of demand covered by PV"""
        workday_intersection        = np.trapz(np.amin([workday[month],generation], axis=0),time)/4
        saturday_intersection       = np.trapz(np.amin([saturday[month],generation], axis=0),time)/4
        sunday_intersection         = np.trapz(np.amin([sunday[month],generation], axis=0),time)/4

        min_workday_intersection    = np.trapz(np.amin([workday[month],generation_min], axis=0),time)/4
        min_saturday_intersection   = np.trapz(np.amin([saturday[month],generation_min], axis=0),time)/4
        min_sunday_intersection     = np.trapz(np.amin([sunday[month],generation_min], axis=0),time)/4

        max_workday_intersection    = np.trapz(np.amin([workday[month],generation_max], axis=0),time)/4
        max_saturday_intersection   = np.trapz(np.amin([saturday[month],generation_max], axis=0),time)/4
        max_sunday_intersection     = np.trapz(np.amin([sunday[month],generation_max], axis=0),time)/4

        total_generation            = np.trapz(generation,time)/4
        total_min_generation        = np.trapz(generation_min,time)/4
        total_max_generation        = np.trapz(generation_max,time)/4

        workday_demand              = np.trapz(workday[month],time)/4
        saturday_demand             = np.trapz(saturday[month],time)/4
        sunday_demand               = np.trapz(sunday[month],time)/4

        workday_demand_covered      = 100*workday_intersection/workday_demand
        saturday_demand_covered     = 100*saturday_intersection/saturday_demand
        sunday_demand_covered       = 100*sunday_intersection/sunday_demand

        min_workday_demand_covered  = 100*min_workday_intersection/workday_demand
        min_saturday_demand_covered = 100*min_saturday_intersection/saturday_demand
        min_sunday_demand_covered   = 100*min_sunday_intersection/sunday_demand

        max_workday_demand_covered  = 100*max_workday_intersection/workday_demand
        max_saturday_demand_covered = 100*max_saturday_intersection/saturday_demand
        max_sunday_demand_covered   = 100*max_sunday_intersection/sunday_demand


        """Find % of PV output used"""
        workday_PV_used        = 100*workday_intersection/total_generation
        saturday_PV_used       = 100*saturday_intersection/total_generation
        sunday_PV_used         = 100*sunday_intersection/total_generation
    
        min_workday_PV_used    = 100*min_workday_intersection/total_min_generation
        min_saturday_PV_used   = 100*min_saturday_intersection/total_min_generation
        min_sunday_PV_used     = 100*min_sunday_intersection/total_min_generation

        max_workday_PV_used    = 100*max_workday_intersection/total_max_generation
        max_saturday_PV_used   = 100*max_saturday_intersection/total_max_generation
        max_sunday_PV_used     = 100*max_sunday_intersection/total_max_generation
        

        """Write time-data into Pandas data frame"""
        df = pd.DataFrame({
            'time'          : time,
            'PV generation' : generation,
            'PV min'        : generation_min,
            'PV max'        : generation_max,
            'BDEW workday'  : workday[month],
            'BDEW saturday' : saturday[month],
            'BDEW sunday'   : sunday[month]

        })

        """append monthly and yearly statistics"""
        bdew_demand['Workday\n Demand [kWh]'].append(str(int(workday_demand)))
        bdew_demand['Saturday\n Demand [kWh]'].append(str(int(saturday_demand)))
        bdew_demand['Sunday\n Demand [kWh]'].append(str(int(sunday_demand)))

        average['PV\n Generation [kWh]'].append(format((total_generation),'.2f'))
        average['Workday Demand\n Covered by PV'].append(str(int(workday_demand_covered))+'%')
        average['Workday PV\n Used by Demand'].append(str(int(workday_PV_used))+'%')
        average['Saturday Demand\n Covered by PV'].append(str(int(saturday_demand_covered))+'%')
        average['Saturday PV\n Used by Demand'].append(str(int(saturday_PV_used))+'%')
        average['Sunday Demand\n Covered by PV'].append(str(int(sunday_demand_covered))+'%')
        average['Sunday PV\n Used by Demand'].append(str(int(sunday_PV_used))+'%')

        min['Cloudy\n PV\n Generation [kWh]'].append(format((total_min_generation),'.2f'))
        min['Cloudy\n Workday Demand\n Covered by PV'].append(str(int(min_workday_demand_covered))+'%')
        min['Cloudy\n Saturday Demand\n Covered by PV'].append(str(int(min_saturday_demand_covered))+'%')
        min['Cloudy\n Sunday Demand\n Covered by PV'].append(str(int(min_sunday_demand_covered))+'%')
        min['Cloudy\n Workday PV\n Used by Demand'].append(str(int(min_workday_PV_used))+'%')
        min['Cloudy\n Saturday PV\n Used by Demand'].append(str(int(min_saturday_PV_used))+'%')
        min['Cloudy\n Sunday PV\n Used by Demand'].append(str(int(min_sunday_PV_used))+'%')

        max['Sunny\n PV\n Generation [kWh]'].append(format((total_max_generation),'.2f'))
        max['Sunny\n Workday Demand\n Covered by PV'].append(str(int(max_workday_demand_covered))+'%')
        max['Sunny\n Saturday Demand\n Covered by PV'].append(str(int(max_saturday_demand_covered))+'%')
        max['Sunny\n Sunday Demand\n Covered by PV'].append(str(int(max_sunday_demand_covered))+'%')
        max['Sunny\n Workday PV\n Used by Demand'].append(str(int(max_workday_PV_used))+'%')
        max['Sunny\n Saturday PV\n Used by Demand'].append(str(int(max_saturday_PV_used))+'%')
        max['Sunny\n Sunday PV\n Used by Demand'].append(str(int(max_sunday_PV_used))+'%')

        df_list.append(df)

    return (df_list,
            pd.DataFrame(average),
            pd.DataFrame(min),
            pd.DataFrame(max),
            pd.DataFrame(bdew_demand),
            time,
            yearly_generation,
            yearly_used)