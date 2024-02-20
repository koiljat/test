import requests
from bs4 import BeautifulSoup
import pandas as pd
import csv
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def append_to_csv(data, filename, headers, first_page):
    df = pd.DataFrame(data)
    if first_page:  # If it's the first page, write headers
        df.to_csv(filename, mode='w', index=False, header=headers)
        logging.info("CSV headers written.")
    else:  # Otherwise, append without headers
        df.to_csv(filename, mode='a', index=False, header=False)

def extract_data(soup):
    # Extracting the data as per your original logic
    location_post_tag = soup.findAll("div", class_=["ast-col-lg-2","ast-col-lg-1"])
    location_post_text = [x.text.strip() for x in location_post_tag][2:]
    company_role_period_div = soup.findAll("div", class_=["ast-col-lg-3"])
    company_role_period_text = [x.text.strip() for x in company_role_period_div][3:]
    web_type_div = [div.findAll("span", class_="text-monospace") for div in company_role_period_div]
    web_type_text = [x[0].text.strip() for x in web_type_div if x != []]

    # Converting them to their columns
    location = location_post_text[::2]
    post_date = location_post_text[1::2]
    company = company_role_period_text[::3]
    role = company_role_period_text[1::3]
    period = company_role_period_text[2::3]
    web = web_type_text[::2]
    job_type = web_type_text[1::2]

    # Packing data into a list of dictionaries
    data = []
    for i in range(len(company)):
        data.append({
            'Company Name': company[i],
            'Role': role[i],
            'Commitment Period': period[i],
            'Location': location[i],
            'Job Type': job_type[i] if i < len(job_type) else '',  # Handling potential index out of range
            'Date Posted': post_date[i],
            'Website': web[i] if i < len(web) else ''  # Handling potential index out of range
        })
    return data

if __name__ == '__main__':
    csv_file = "data.csv"
    headers = ['Company Name', 'Role', 'Commitment Period', 'Location', 'Job Type', 'Date Posted', 'Website']

    logging.info("Starting CSV file creation.")

    with requests.Session() as session:
        for page in range(1, 121):
            url = f"https://www.internsg.com/jobs/{page}/#isg-top"
            response = session.get(url)
            
            if response.status_code != 200:
                logging.error(f"Failed to retrieve page {page}. Status code: {response.status_code}")
                continue
            
            soup = BeautifulSoup(response.content, "html.parser")
            data = extract_data(soup)
            
            if not data:
                logging.info(f"No data found on page {page}. Stopping.")
                break

            append_to_csv(data, csv_file, headers, page == 1)
            logging.info(f"Data appended to CSV for page {page}.")

    logging.info("CSV file creation completed successfully.")
