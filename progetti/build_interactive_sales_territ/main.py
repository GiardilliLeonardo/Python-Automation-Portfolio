# Task: Build interactive sales territory map from CRM data (Leaflet.js + Python automation pipeline)

import os
import sys
import pandas as pd
import folium
from folium.plugins import MarkerCluster, FeatureGroupSubGroup

CRM_DATA_FILE = "crm_sales_data.csv"
OUTPUT_MAP_FILE = "sales_territory_map.html"


def generate_mock_crm_data(filepath: str) -> None:
    data = """territory,sales_rep,account_name,latitude,longitude,deal_value,status
North,Alice Smith,Acme Corp,41.8781,-87.6298,125000,Closed Won
North,Alice Smith,Cyberdyne Systems,42.3314,-83.0458,85000,Negotiation
North,Alice Smith,Wayne Enterprises,41.4993,-81.6944,95000,Closed Won
South,Bob Jones,Initech,33.7490,-84.3880,150000,Closed Won
South,Bob Jones,Umbrella Corp,29.7604,-95.3698,210000,Closed Won
South,Bob Jones,Hooli,30.2672,-97.7431,60000,Prospect
East,Carol White,Stark Industries,40.7128,-74.0060,320000,Closed Won
East,Carol White,Massive Dynamic,39.9526,-75.1652,110000,Negotiation
East,Carol White,Oscorp,42.3601,-71.0589,75000,Prospect
West,David Brown,Soylent Corp,37.7749,-122.4194,180000,Closed Won
West,David Brown,Tyrell Corp,34.0522,-118.2437,290000,Closed Won
West,David Brown,Buy More,47.6062,-122.3321,45000,Prospect
"""
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(data.strip())


def get_status_color(status: str) -> str:
    color_map = {
        "Closed Won": "green",
        "Negotiation": "orange",
        "Prospect": "blue"
    }
    return color_map.get(status, "gray")


def build_map_pipeline(csv_path: str, output_html: str) -> None:
    if not os.path.exists(csv_path):
        generate_mock_crm_data(csv_path)

    df = pd.read_csv(csv_path)

    required_columns = {
        "territory", "sales_rep", "account_name", 
        "latitude", "longitude", "deal_value", "status"
    }
    if not required_columns.issubset(df.columns):
        raise ValueError(f"CSV missing required columns: {required_columns - set(df.columns)}")

    df["deal_value"] = pd.to_numeric(df["deal_value"], errors="coerce").fillna(0)
    df["latitude"] = pd.to_numeric(df["latitude"], errors="coerce")
    df["longitude"] = pd.to_numeric(df["longitude"], errors="coerce")
    df = df.dropna(subset=["latitude", "longitude"])

    center_lat = df["latitude"].mean()
    center_lon = df["longitude"].mean()

    sales_map = folium.Map(
        location=[center_lat, center_lon],
        zoom_start=5,
        tiles="CartoDB positron"
    )

    cluster_group = MarkerCluster(name="All Accounts (Clustered)").add_to(sales_map)

    territories = df["territory"].unique()

    for territory in territories:
        t_data = df[df["territory"] == territory]
        rep = t_data["sales_rep"].iloc[0]
        total_pipeline = t_data["deal_value"].sum()
        closed_won = t_data[t_data["status"] == "Closed Won"]["deal_value"].sum()
        win_rate = (closed_won / total_pipeline * 100) if total_pipeline > 0 else 0

        territory_group = FeatureGroupSubGroup(cluster_group, name=f"Territory: {territory}").add_to(sales_map)

        t_center_lat = t_data["latitude"].mean()
        t_center_lon = t_data["longitude"].mean()

        hub_html = f"""
        <div style="font-family: Arial; min-width: 180px;">
            <h4 style="margin-bottom: 5px;">Territory: {territory}</h4>
            <b>Rep:</b> {rep}<br>
            <b>Total Pipeline:</b> ${total_pipeline:,.2f}<br>
            <b>Closed Won:</b> ${closed_won:,.2f}<br>
            <b>Win Rate:</b> {win_rate:.1f}%
        </div>
        """
        folium.Marker(
            location=[t_center_lat, t_center_lon],
            popup=folium.Popup(hub_html, max_width=250),
            tooltip=f"{territory} Territory Hub",
            icon=folium.Icon(color="darkblue", icon="briefcase", prefix="fa")
        ).add_to(territory_group)

        for _, row in t_data.iterrows():
            marker_html = f"""
            <div style="font-family: Arial; min-width: 160px;">
                <h5 style="margin-bottom: 4px;">{row['account_name']}</h5>
                <b>Territory:</b> {row['territory']}<br>
                <b>Sales Rep:</b> {row['sales_rep']}<br>
                <b>Status:</b> {row['status']}<br>
                <b>Deal Value:</b> ${row['deal_value']:,.2f}
            </div>
            """
            folium.Marker(
                location=[row["latitude"], row["longitude"]],
                popup=folium.Popup(marker_html, max_width=250),
                tooltip=f"{row['account_name']} (${row['deal_value']:,.0f})",
                icon=folium.Icon(color=get_status_
