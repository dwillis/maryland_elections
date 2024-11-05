import requests
from bs4 import BeautifulSoup
import pandas as pd
import os

# URL of the election results page
url = "https://results.elections.maryland.gov/elections/2024/General_Results/gen_results_2024_by_county_11.html"

# Send a request to fetch the HTML content of the page
response = requests.get(url)
response.raise_for_status()

# Parse the HTML content using BeautifulSoup
soup = BeautifulSoup(response.content, 'html.parser')

def clean_votes(vote_str):
    vote_str = vote_str.replace(',', '').strip()
    return int(vote_str) if vote_str.isdigit() else 0

def extract_race_results(soup):
    results = []
    current_office = None

    for element in soup.find_all(['h2', 'h3', 'h4', 'table']):
        if element.name == 'h2':
            current_office = element.get_text(strip=True)
            print(f"Found new office: {current_office}")
        elif element.name == 'table' and current_office:
            rows = element.find_all('tr')
            if not rows:
                continue

            headers = [header.get_text(strip=True) for header in rows[0].find_all('th')] if len(rows) > 0 else []

            data = []
            for row in rows[1:]:
                cols = [col.get_text(strip=True) for col in row.find_all('td')]
                data.append(cols)

            if headers and data:
                df = pd.DataFrame(data, columns=headers)
                results.append((current_office, df))
                print(f"Extracted data for office: {current_office}")

    return results

# Extract all race results
races = extract_race_results(soup)

# Ensure the output directory exists
os.makedirs('data', exist_ok=True)

# Process and save each race to a CSV file
for office, df in races:
    if df.empty:
        continue

    # Separate the Totals row
    totals_row = df[df.iloc[:, 0].str.contains('Totals', na=False)]
    df = df[~df.iloc[:, 0].str.contains('Totals', na=False)]

    # Clean and process vote columns
    if 'Total' in df.columns:
        df.loc[:, 'Total'] = df['Total'].apply(clean_votes)
    else:
        df.loc[:, 'Total'] = df.iloc[:, -2].apply(clean_votes)  # Assuming the second last column is the 'Total' column if not named

    # Sort by Total and append Totals row at the bottom
    df = df.sort_values(by='Total', ascending=False)
    df = pd.concat([df, totals_row], ignore_index=True)

    # Save results based on Party
    office_name = office.replace(' ', '_') if office else 'Unknown_Office'
    filename = f"data/{office_name}_Frederick.csv"
    df.to_csv(filename, index=False)

# Confirmation message
print("Scraping and CSV creation completed.")
