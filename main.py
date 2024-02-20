import requests
from bs4 import BeautifulSoup
import pandas as pd
from config import URL
import csv

if __name__ == '__main__':
    
    csv_file = "data.csv"

    with open(csv_file, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(['Company Name', 'Role', 'Commitment Period', 'Location', 'Job Type', 'Date Posted', 'Website'])
        
        

    print("Empty CSV file created successfully.")

    for page in range(1, 121):
        url = f"https://www.internsg.com/jobs/{page}/#isg-top"
        response = requests.get(url)
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        ##Obtaining the raw data
        location_post_tag = soup.findAll("div", class_=["ast-col-lg-2","ast-col-lg-1"])
        location_post_text = [x.text.strip() for x in location_post_tag][2:]
        company_role_period_div = soup.findAll("div", class_=["ast-col-lg-3"])
        company_role_period_text = [x.text.strip() for x in company_role_period_div][3:]
        web_type_div = [div.findAll("span", class_="text-monospace") for div in company_role_period_div]
        web_type_text = [x[0].text.strip() for x in web_type_div if x != []]

        ##Converting them to their columns.
        location = location_post_text[::2]
        post_date = location_post_text[1::2]
        company = company_role_period_text[::3]
        role = company_role_period_text[1::3]
        period = company_role_period_text[2::3]
        web = web_type_text[::2]
        job_type = web_type_text[1::2]

        ##Saving data
        df = pd.DataFrame({'Company Name': company,
                        'Role': role,
                        'Commitment Period': period,
                        'Location': location,
                        'Job Type': job_type,
                        'Date Posted': post_date,
                        'Website': web})
        
        df_existing = pd.read_csv(csv_file)
        df_combined = pd.concat([df_existing, df])
        df_combined.to_csv(csv_file, index=False)

        print(f"CSV file saved successfully for page {page}.")