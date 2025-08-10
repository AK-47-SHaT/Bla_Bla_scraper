import streamlit as st
import requests
from bs4 import BeautifulSoup
import pandas as pd

# --- Headers for request ---
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8"
}

# --- Streamlit UI ---
st.set_page_config(page_title="BlaBlaCar Ride Finder", layout="wide")
st.title("🚗 BlaBlaCar Ride Availability Checker")

# Input date from user
date = st.date_input("Select Ride Date", pd.Timestamp.today()).strftime("%Y-%m-%d")

# URL with the chosen date
HN_URL = f"https://www.blablacar.in/search?fn=108%2C+108%2C+Block+D%2C+SGM+Nagar%2C+New+Industrial+Township%2C+Faridabad%2C+Haryana&tn=JAYPEE+INSTITUTE+OF+INFORMATION+TECHNOLOGY%2C+A+10%2C+A+Block%2C+Block+A%2C+Industrial+Area%2C+Sector+62%2C+Noida%2C+Uttar+Pradesh&db={date}&seats=1&search_origin=SEARCH&from_place_id=eyJpIjoiQ2hJSkItejZhZGZkRERrUkMzYWZTb0EyMXZvIiwicCI6MSwidiI6MSwidCI6WzJdfQ%3D%3D&to_place_id=eyJpIjoiQ2hJSjV6d2JTVkhsRERrUnNKMU5fZnpaTlhNIiwicCI6MSwidiI6MSwidCI6WzEsMl19&sort=dep_time%3Aasc&dep_6_12=true&verified_id=true&2_max_back=true"

# --- Function to fetch rides ---
def fetch_rides():
    try:
        response = requests.get(HN_URL, timeout=10, headers=headers)
        response.raise_for_status()
    except requests.RequestException as e:
        st.error(f"Network error: {e}")
        return pd.DataFrame()

    soup = BeautifulSoup(response.text, "html.parser")

    names = soup.select('span[data-testid="e2e-tripcard-driver-name"]')
    times = soup.select('p[data-testid="e2e-itinerary-departure-time"]')
    price_containers = soup.select('span[data-testid="e2e-tripcard-price-price-value"]')

    rides = []
    for name, time_tag, price_container in zip(names, times, price_containers):
        p_tag = price_container.find("p", attrs={"data-testid": "e2e-trip-card-not-available"})
        if p_tag:
            price = p_tag.get_text(strip=True)  # Full / Not available
        else:
            spans = price_container.find_all("span")
            if len(spans) >= 2:
                price = spans[1].get_text(strip=True)
            elif spans:
                price = spans[0].get_text(strip=True)
            else:
                price = "N/A"

        rides.append({
            "Driver": name.get_text(strip=True),
            "Time": time_tag.get_text(strip=True),
            "Price / Status": price
        })

    return pd.DataFrame(rides)

# --- UI button ---
if st.button("Search Rides"):
    with st.spinner("Fetching ride data..."):
        rides_df = fetch_rides()
        if rides_df.empty:
            st.warning("No rides found for the selected date.")
        else:
            st.success(f"Found {len(rides_df)} rides")
            st.dataframe(rides_df)

           
