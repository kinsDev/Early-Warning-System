import math as m

def INFORM_SEVERITY_INDEX(impact_of_the_crises, conditions_of_people_affected, complexity_of_the_crises):
    agg_impact = impact_of_the_crises * 33/100
    agg_conditions = conditions_of_people_affected *66/100
    agg_complexity = complexity_of_the_crises * 30/100

    geom_avg = m.sqrt(agg_impact*agg_conditions)

    agg_geom_avg = geom_avg * 70/100

    sum = agg_geom_avg + agg_complexity

    inform_severity_index = sum

    return inform_severity_index
