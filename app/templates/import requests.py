import requests
from bs4 import BeautifulSoup
import pandas as pd

# Website URL (Change to your target website)
url = "https://www.ddproperty.com/en/rent/pattaya/bang-lamung/apartment"

# Set headers to mimic a browser request
headers = {"User-Agent": "Mozilla/5.0"}

# Fetch the webpage
response = requests.get(url, headers=headers)
soup = BeautifulSoup(response.text, "html.parser")

# Find listings (change based on actual HTML structure)
listings = soup.find_all("div", class_="listing-card")

# Store extracted data
data = []
for listing in listings:
    try:
        price = listing.find("span", class_="listing-price").text.strip()
        title = listing.find("a", class_="listing-title").text.strip()
        details = listing.find("div", class_="listing-details").text.strip()
        data.append([title, price, details])
    except:
        continue

# Save data to DataFrame
df = pd.DataFrame(data, columns=["Title", "Price", "Details"])

# Save to CSV
df.to_csv("pattaya_apartments.csv", index=False)

print("Scraping completed! Data saved to 'pattaya_apartments.csv'")