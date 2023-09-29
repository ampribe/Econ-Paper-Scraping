import sys
import pandas as pd
from selenium import webdriver
from selenium.webdriver import ChromeOptions
import time
import os
import regex as re

# requires filename of csv with download links as first argument
args = sys.argv
csv_title = args[1]
links_df = pd.read_csv(csv_title)
links = list(links_df.itertuples(index=False, name=None))

# removes PDFs that are already in the folder from list of PDFs to download
print('filtering pdfs...', end='')
files = [f for f in os.listdir('.') if os.path.isfile(f)]
pdfs = set(filter(lambda x: x[-3:] == 'pdf', files))

# regex derives filename from article link
links = ([(article_link, download_link, title, issue) for article_link, download_link, title, issue in links 
          if re.search('(?<=\/)[a-z\.\d]+$', article_link).group() + '.pdf' not in pdfs])

print('Done')



total = len(links)

# sets Selenium to download PDFs to current folder instead of opening them in browser
options = ChromeOptions()
options.add_experimental_option('prefs',  {
      "download.default_directory": os.getcwd(),
      "download.prompt_for_download": False,
      "download.directory_upgrade": True,
      "plugins.always_open_pdf_externally": True
      }
  )
# this option limits the amount of information Selenium prints to console
options.add_argument("--log-level=3")


# 0 = uchicago-secure, 1 = eduroam
last_connection = 0
# sets current network to uchicago-secure 
# the program will switch between uchicago-secure and eduroam to avoid getting banned
os.system('netsh wlan connect ssid=uchicago-secure name=uchicago-secure')
time.sleep(15)

driver = webdriver.Chrome(options=options)

for i, (article_link, download_link, title, issue) in enumerate(links):
    # Every 99 downloads, program will switch networks and reset browser to avoid getting banned
    if i%99 == 0 and i != 0:
        driver.close()
        print('resetting connection...')
        if last_connection == 0:
            os.system('netsh wlan connect ssid=eduroam name=eduroam')
            
            last_connection = 1
        else:
            os.system('netsh wlan connect ssid=uchicago-secure name=uchicago-secure')
            last_connection = 0

        # waits for new connection
        time.sleep(15)
        driver = webdriver.Chrome(options=options)
        
    # download pdf
    print(f'{i+1}/{total}')
    driver.get(download_link)

# must wait a little to allow final PDF to finish downloading
time.sleep(5)
driver.close()


