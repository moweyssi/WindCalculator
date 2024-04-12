from pvlib_parse import get_pvgis_hourly
import pandas as pd
import numpy as np
from EST_BDEW import yearly_BDEW


def PV_power(
    startyear,
    endyear,
    latitude,
    longitude,
    property_type,
    yearly_consumption,
    turbine_height,
    land_cover_type
):
    numyears = endyear - startyear + 1
    data, meta, inputs = get_pvgis_hourly(
        latitude,
        longitude,
        start=startyear,
        end=endyear
    )
    
    #Correct wind speed to height of turbine : https://wind-data.ch/tools/profile.php?lng=en
    data["wind_speed"] = data["wind_speed"] * np.ln(turbine_height/land_cover_type) / np.ln(10/land_cover_type)

    years = np.arange(startyear, endyear + 1, 1).tolist()
    all_years_daily_average = []
    all_years_daily_error = []
    yearly_gen = []
    yearly_use = []
    for year in years:

        """MONTHLY ANALYSIS"""
        monthsyear = []
        groupyear = data["wind_speed"][str(year)].groupby(pd.Grouper(freq="M"))
        for date, group in groupyear:
            monthsyear.append(np.array(group.to_numpy()))

        numdaysofmonth = [len(monthsyear[i]) / (24) for i in range(len(monthsyear))]
        one_year_average = [
            np.mean(np.hsplit(np.array(monthsyear[i]), numdaysofmonth[i]), axis=0)
            for i in range(len(numdaysofmonth))
        ]
        all_years_daily_average.append(one_year_average)
        one_year_error = [
            np.std(
                np.hsplit(np.array(monthsyear[i]), numdaysofmonth[i]), ddof=1, axis=0
            )
            / np.sqrt(numdaysofmonth[i])
            for i in range(len(numdaysofmonth))
        ]
        all_years_daily_error.append(one_year_error)

        """YEARLY ANALYSIS"""
        yearly_demand = (
            yearly_BDEW(property_type, year, yearly_consumption)
            .resample(rule="H")
            .sum()
            / 4
        )
        yearly_demand = yearly_demand[property_type]
        yearly_pv = data["wind_speed"][str(year)]
        intersection = np.amin([yearly_demand, yearly_pv], axis=0)
        yearly_gen.append(np.sum(yearly_pv).astype(int))
        yearly_use.append(np.sum(intersection).astype(int))

    daily_average = np.mean(all_years_daily_average, axis=0)
    daily_error = np.sqrt(np.sum(np.square(all_years_daily_error), axis=0)) / numyears

    gen_error = np.std(np.array(yearly_gen), ddof=1) / np.sqrt(len(yearly_gen))
    use_error = np.std(np.array(yearly_use), ddof=1) / np.sqrt(len(yearly_use))

    return (
        daily_average,
        daily_error,
        (int(np.mean(yearly_gen)), int(1.96 * gen_error)),
        (int(np.mean(yearly_use)), int(1.96 * use_error)),
    )  # convert into kWh
