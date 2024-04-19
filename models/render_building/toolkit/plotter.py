import os

import matplotlib.pyplot as plt
import pandas as pd
from Melodie import Config


def plot_hist(
    values,
    bins,
    x_label,
    y_label,
    fig_path: str
):
    plt.figure(figsize=(10, 6), dpi=200)
    plt.hist(values, bins=bins, color='skyblue', edgecolor='black')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    plt.grid(True)
    plt.savefig(fig_path)
    plt.close()


def plot_hist_heating_demand_per_m2(
    cfg: "Config",
    year: int,
    input_table: str = "building_stock.csv",
):
    building_stock = pd.read_csv(os.path.join(cfg.output_folder, input_table))
    building_stock = building_stock.loc[(building_stock["year"] == year) & (building_stock["exists"] == 1)]
    heating_demand_per_m2 = []
    total_heating_per_m2 = []
    building_efficiency_class = []
    for index, row in building_stock.iterrows():
        heating_demand_per_m2 += [row["heating_demand_per_m2"] for i in range(0, round(row["building_number"]))]
        total_heating_per_m2 += [row["total_heating_per_m2"] for i in range(0, round(row["building_number"]))]
        building_efficiency_class += [row["id_building_efficiency_class"] for i in range(0, round(row["building_number"]))]
    plot_hist(
        values=heating_demand_per_m2,
        bins=25,
        x_label="heating demand per m2",
        y_label="count",
        fig_path=os.path.join(cfg.output_folder, f"plot_hist_heating_demand_per_m2_{year}.png")
    )
    plot_hist(
        values=total_heating_per_m2,
        bins=25,
        x_label="total heating demand per m2",
        y_label="count",
        fig_path=os.path.join(cfg.output_folder, f"plot_hist_total_heating_demand_per_m2_{year}.png")
    )
    plot_hist(
        values=building_efficiency_class,
        bins=12,
        x_label="building efficiency class",
        y_label="count",
        fig_path=os.path.join(cfg.output_folder, f"plot_hist_building_efficiency_class_{year}.png")
    )
