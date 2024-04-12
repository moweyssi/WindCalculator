"""
g0	        General trade/business/commerce	                                            Weighted average of profiles G1-G6
g1	        Business on weekdays 8 a.m. - 6 p.m.	                                    e.g. offices, doctors surgeries, workshops, administrative facilities
g2	        Businesses with heavy to predominant consumption in the evening hours	    e.g. sports clubs, fitness studios, evening restaurants
g3	        Continuous business	                                                        e.g. cold stores, pumps, sewage treatment plants
g4	        Shop/barber shop	 
g5	        Bakery with bakery	 
g6	        Weekend operation	                                                        e.g. cinemas
g7	        Mobile phone transmitter station	                                        continuous band load profile
l0	        General farms	                                                            Weighted average of profiles L1 and L2
l1	        Farms with dairy farming/part-time livestock farming	 
l2	        Other farms	 
h0/h0_dyn	Household/dynamic houshold
"""

import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)
from demandlib.bdew.elec_slp import ElecSlp
import demandlib.particular_profiles as profiles
from workalendar.europe import UnitedKingdom
from workalendar.core import MON, SAT, SUN


def get_BDEW(Property_Type, year, yearly_consumption):
    calendar = UnitedKingdom()
    holidays = dict(calendar.holidays(year))

    ann_el_demand_per_sector = {
        Property_Type:yearly_consumption
        }

    e_slp = ElecSlp(year,holidays=holidays)
    demand = e_slp.get_profile(ann_el_demand_per_sector)


    # Option to configure an industrial slp
    """
    ilp = profiles.IndustrialLoadProfile(e_slp.date_time_index, holidays=holidays)
    # Change scaling factors and day start
    demand["custom"] = ilp.simple_profile(
        ann_el_demand_per_sector["custom"], am=settime(9, 0, 0),
        profile_factors={
        "week": {"day": 3.0, "night": 0.8},
        "weekend": {"day": 0.8, "night": 0.6},
    },
    )
    """

    workday = []
    saturday = []
    sunday = []
    for month_number in range(1,13):
        last_monday = calendar.get_last_weekday_in_month(year, month_number, MON)
        while 1:
            if calendar.is_working_day(last_monday) is False:
                last_monday = calendar.add_working_days(last_monday,1)
            if calendar.is_working_day(last_monday) is True:
                break
        last_saturday = calendar.get_last_weekday_in_month(year, month_number, SAT)
        last_sunday = calendar.get_last_weekday_in_month(year, month_number, SUN)

        workday.append(demand[(demand.index.date==last_monday)].to_numpy().T[0])
        saturday.append(demand[(demand.index.date==last_saturday)].to_numpy().T[0])
        sunday.append(demand[(demand.index.date==last_sunday)].to_numpy().T[0])

    return workday, saturday, sunday

def yearly_BDEW(Property_Type, year, yearly_consumption):
    calendar = UnitedKingdom()
    holidays = dict(calendar.holidays(year))

    ann_el_demand_per_sector = {
        Property_Type:yearly_consumption
        }

    e_slp = ElecSlp(year,holidays=holidays)
    demand = e_slp.get_profile(ann_el_demand_per_sector)

    return demand