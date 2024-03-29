import random

import pandas as pd


WEEKDAY_OCCUPANCY_PROFILE = [
    0, 0, 0, 0, 0, 0, 0.1, 0.2, 0.6, 0.8, 1, 1,
    1, 1, 1, 0.8, 0.6, 0.2, 0.1, 0, 0, 0, 0, 0
]

WEEKEND_OCCUPANCY_PROFILE = [
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
    0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
]


def gen_occupancy_profile_with_working_day(working_day: int):
    weekday_day_year = 52 * 5 + 1
    working_day_prob = working_day / weekday_day_year
    profile = []
    for day in range(1, 366):
        if working_day_prob <= 1:
            n = day % 7
            day_of_week = n if n != 0 else 7
            if day_of_week <= 5:
                if random.uniform(0, 1) <= working_day_prob:
                    profile += WEEKDAY_OCCUPANCY_PROFILE
                else:
                    profile += WEEKEND_OCCUPANCY_PROFILE
            else:
                profile += WEEKEND_OCCUPANCY_PROFILE
        else:
            if random.uniform(0, 1) <= working_day / 365:
                profile += WEEKDAY_OCCUPANCY_PROFILE
            else:
                profile += WEEKEND_OCCUPANCY_PROFILE
    return profile


def gen_tertiary_occupancy_profiles():
    d = {}
    df = pd.read_excel("working_day.xlsx")
    for index, row in df.iterrows():
        occupancy_profile = gen_occupancy_profile_with_working_day(int(row["value"]))
        print(f'id_subsector = {row["id_subsector"]}: working_day = {row["value"]}, total_hours = {sum(occupancy_profile)}')
        d[row["id_subsector"]] = occupancy_profile
    pd.DataFrame(d).to_csv("tertiary_occupancy_profiles.csv", index=False)


if __name__ == "__main__":
    gen_tertiary_occupancy_profiles()
