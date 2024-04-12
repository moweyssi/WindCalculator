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

def makedf(property_type, lat, lon, annual_consumption,start_year, end_year, turbine_height,land_cover_type, turbine_nominal_power = 10, turbine_rotor_diameter = 10.2, cutin_speed = 3, cutoff_speed = 25):

    generation_hourly, error_hourly, yearly_generation, yearly_used  = PV_power(
        start_year,end_year,lat,lon,property_type, annual_consumption, turbine_height,land_cover_type, turbine_nominal_power = 10, turbine_rotor_diameter = 10.2, cutin_speed = 3, cutoff_speed = 25
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
        "Wind\n Generation [kWh]": [],
        "Workday Demand\n Covered by Wind": [],
        "Saturday Demand\n Covered by Wind": [],
        "Sunday Demand\n Covered by Wind": [],
        "Workday Wind\n Used by Demand": [],
        "Saturday Wind\n Used by Demand": [],
        "Sunday Wind\n Used by Demand": [],
    }
    min = {
        "Still\n Wind\n Generation [kWh]": [],
        "Still\n Workday Demand\n Covered by Wind": [],
        "Still\n Saturday Demand\n Covered by Wind": [],
        "Still\n Sunday Demand\n Covered by Wind": [],
        "Still\n Workday Wind\n Used by Demand": [],
        "Still\n Saturday Wind\n Used by Demand": [],
        "Still\n Sunday Wind\n Used by Demand": [],
    }
    max = {
        "Windy\n Wind\n Generation [kWh]": [],
        "Windy\n Workday Demand\n Covered by Wind": [],
        "Windy\n Saturday Demand\n Covered by Wind": [],
        "Windy\n Sunday Demand\n Covered by Wind": [],
        "Windy\n Workday Wind\n Used by Demand": [],
        "Windy\n Saturday Wind\n Used by Demand": [],
        "Windy\n Sunday Wind\n Used by Demand": [],
    }

    for month in range(12):
        df=pd.DataFrame()

        """Convert PVGIS data to 15 minute resolution"""
        error = np.interp(time,time_hourly,error_hourly[month])
        generation = np.interp(time,time_hourly,generation_hourly[month])
        generation_min = generation-2*error
        generation_max = generation+2*error

        """Find % of demand covered by Wind"""
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


        """Find % of Wind output used"""
        workday_Wind_used        = 100*workday_intersection/total_generation
        saturday_Wind_used       = 100*saturday_intersection/total_generation
        sunday_Wind_used         = 100*sunday_intersection/total_generation
    
        min_workday_Wind_used    = 100*min_workday_intersection/total_min_generation
        min_saturday_Wind_used   = 100*min_saturday_intersection/total_min_generation
        min_sunday_Wind_used     = 100*min_sunday_intersection/total_min_generation

        max_workday_Wind_used    = 100*max_workday_intersection/total_max_generation
        max_saturday_Wind_used   = 100*max_saturday_intersection/total_max_generation
        max_sunday_Wind_used     = 100*max_sunday_intersection/total_max_generation
        

        """Write time-data into Pandas data frame"""
        df = pd.DataFrame({
            'time'          : time,
            'Wind generation' : generation,
            'Wind min'        : generation_min,
            'Wind max'        : generation_max,
            'BDEW workday'  : workday[month],
            'BDEW saturday' : saturday[month],
            'BDEW sunday'   : sunday[month]

        })

        """append monthly and yearly statistics"""
        bdew_demand['Workday\n Demand [kWh]'].append(str(int(workday_demand)))
        bdew_demand['Saturday\n Demand [kWh]'].append(str(int(saturday_demand)))
        bdew_demand['Sunday\n Demand [kWh]'].append(str(int(sunday_demand)))

        average['Wind\n Generation [kWh]'].append(format((total_generation),'.2f'))
        average['Workday Demand\n Covered by Wind'].append(str(int(workday_demand_covered))+'%')
        average['Workday Wind\n Used by Demand'].append(str(int(workday_Wind_used))+'%')
        average['Saturday Demand\n Covered by Wind'].append(str(int(saturday_demand_covered))+'%')
        average['Saturday Wind\n Used by Demand'].append(str(int(saturday_Wind_used))+'%')
        average['Sunday Demand\n Covered by Wind'].append(str(int(sunday_demand_covered))+'%')
        average['Sunday Wind\n Used by Demand'].append(str(int(sunday_Wind_used))+'%')

        min['Still\n Wind\n Generation [kWh]'].append(format((total_min_generation),'.2f'))
        min['Still\n Workday Demand\n Covered by Wind'].append(str(int(min_workday_demand_covered))+'%')
        min['Still\n Saturday Demand\n Covered by Wind'].append(str(int(min_saturday_demand_covered))+'%')
        min['Still\n Sunday Demand\n Covered by Wind'].append(str(int(min_sunday_demand_covered))+'%')
        min['Still\n Workday Wind\n Used by Demand'].append(str(int(min_workday_Wind_used))+'%')
        min['Still\n Saturday Wind\n Used by Demand'].append(str(int(min_saturday_Wind_used))+'%')
        min['Still\n Sunday Wind\n Used by Demand'].append(str(int(min_sunday_Wind_used))+'%')

        max['Windy\n Wind\n Generation [kWh]'].append(format((total_max_generation),'.2f'))
        max['Windy\n Workday Demand\n Covered by Wind'].append(str(int(max_workday_demand_covered))+'%')
        max['Windy\n Saturday Demand\n Covered by Wind'].append(str(int(max_saturday_demand_covered))+'%')
        max['Windy\n Sunday Demand\n Covered by Wind'].append(str(int(max_sunday_demand_covered))+'%')
        max['Windy\n Workday Wind\n Used by Demand'].append(str(int(max_workday_Wind_used))+'%')
        max['Windy\n Saturday Wind\n Used by Demand'].append(str(int(max_saturday_Wind_used))+'%')
        max['Windy\n Sunday Wind\n Used by Demand'].append(str(int(max_sunday_Wind_used))+'%')

        df_list.append(df)

    return (df_list,
            pd.DataFrame(average),
            pd.DataFrame(min),
            pd.DataFrame(max),
            pd.DataFrame(bdew_demand),
            time,
            yearly_generation,
            yearly_used)