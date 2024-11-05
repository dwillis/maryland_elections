import requests
from bs4 import BeautifulSoup
import pandas as pd

# URL of the election results page
url = "https://elections.maryland.gov/elections/2024/General_Results/gen_detail_results_2024_3_6_District%206.html"

# Send a request to fetch the HTML content of the page
response = requests.get(url)
response.raise_for_status()  # Ensure the request was successful

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

# Locate the table containing the election results
table = soup.find('table')

# Extract table headers
headers = ["Jurisdiction", "April McClain Delaney (D)", "Neil C. Parrott (R)", "Other Write-Ins"]
#headers = [header.get_text(strip=True) for header in table.find_all('th')]

# Extract table rows
rows = []
for row in table.find_all('tr')[1:]:  # Skip the header row
    cols = [col.get_text(strip=True) for col in row.find_all('td')]
    rows.append(cols)

# Create a DataFrame
df = pd.DataFrame(rows, columns=headers)

# Save the DataFrame to a CSV file
df.to_csv('data/Representative_in_Congress_District_6.csv', index=False)
