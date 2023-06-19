from __future__ import print_function
import regex as re
import os
import os.path
import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
from selenium.webdriver import ChromeOptions
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

def get_article_links(months):
    print('Getting article links...', end='')
    driver = webdriver.Firefox()
    driver.get('https://www.aeaweb.org/journals/aer/issues')
    issue_links = [driver.find_element(By.PARTIAL_LINK_TEXT, month).get_attribute('href') for month in months]
    article_links = []
    for issue_link in issue_links:
        driver.get(issue_link)
        article_links = (article_links + 
                         [element.get_attribute('href') for element in driver.find_elements(By.XPATH, "//a[contains(@href, '/articles?id=')]")])
    driver.close()
    print(' Done.')
    return article_links

def get_article_data(article_links):
    print('Getting article data...',end='')
    driver = webdriver.Firefox()
    # Title, Filename, Link, Authors, JEL, Issue, 
    article_data = dict()
    for article_link in article_links:
        driver.get(article_link)
        pdf_link = driver.find_element(By.XPATH, "//a[contains(@href, '/articles/pdf')]").get_attribute('href')
        doi = driver.find_element(By.CLASS_NAME, 'doi').text
        title = driver.find_element(By.CLASS_NAME, 'title').text
        file_name = doi[(doi.find('/')+1):]+'.pdf'
        journal = driver.find_element(By.CLASS_NAME, 'journal').text
        issue = driver.find_element(By.CLASS_NAME, 'vol').text
        
        author_elements = driver.find_elements(By.CLASS_NAME, 'author')
        jel_elements = driver.find_elements(By.CLASS_NAME, 'jel-codes')
        author = None if author_elements == [] else ', '.join([element.text for element in author_elements])
        jel = None if jel_elements == [] else ', '.join(re.findall('[A-Z]\d{2}', str([element.text for element in jel_elements])))
        article_data.update({doi: [title, article_link, pdf_link, author, journal, issue, jel, file_name]})
        
    driver.close()
    df = pd.DataFrame.from_dict(article_data, orient='index',
                       columns=['Title','Article Link', 'PDF Link', 'Authors', 'Journal', 'Issue', 'JEL', 'Filename'])
    print('Done')
    return df

def download_pdfs(pdf_links):
    print('Getting PDFs...',end='')
    # https://stackoverflow.com/questions/40279815/cant-download-pdf-with-selenium-webdriver-firefox?rq=3
    options = ChromeOptions()
    options.add_experimental_option('prefs',  {
          "download.default_directory": os.getcwd(),
          "download.prompt_for_download": False,
          "download.directory_upgrade": True,
          "plugins.always_open_pdf_externally": True
          }
      )
    driver = webdriver.Chrome(options=options)
    for pdf_link in pdf_links:
        driver.get(pdf_link)
    time.sleep(5)
    driver.close()
    print('Done')
    
    
def upload_pdfs(files_to_upload, folder_name='AER Articles'):
    
    file_links = []

    # https://developers.google.com/drive/api/quickstart/python
    # https://developers.google.com/drive/api/guides/folder

    print('Authenticating Google Drive...',end='')
    # If modifying these scopes, delete the file token.json.
    SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/drive.file', 'https://www.googleapis.com/auth/drive.metadata']
    
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())


    print('Done')
    print('Uploading PDFs',end='')
    try:
        # create drive api client
        service = build('drive', 'v3', credentials=creds)

        file_metadata = {
            'name': folder_name,
            'mimeType': 'application/vnd.google-apps.folder'
        }

        # pylint: disable=maybe-no-member
        file = service.files().create(body=file_metadata, fields='id'
                                      ).execute()
        print(F'Folder ID: "{file.get("id")}".')
        folder_id = file.get('id')

        for file_upload in files_to_upload:
            file_metadata = {'name': file_upload,
                            'parents': [folder_id]}
            media = MediaFileUpload(file_upload,
                                    mimetype='application/pdf')
            # pylint: disable=maybe-no-member
            file = service.files().create(body=file_metadata, media_body=media,
                                          fields='id').execute()
            file_id = file.get('id')
            file_links.append(f'https://drive.google.com/file/d/{file_id}/view')

    except HttpError as error:
        print(F'An error occurred: {error}')
        file = None
    print('Done')
    return file_links

def search_gs(doi_list):
    print('Searching Google Scholar...')
    driver = webdriver.Firefox()
    all_cites = []
    for doi in doi_list:
        driver.get(f'https://scholar.google.com/scholar?q={doi}')
        if 'Please show you\'re not a robot' in driver.find_element(By.TAG_NAME, "body").text:
            print('Must complete CAPTCHA to continue...')
            time.sleep(30)

        try:
            citations_link = driver.find_element(By.PARTIAL_LINK_TEXT, 'Cited by').get_attribute('href')
            driver.get(citations_link)
            titles = [element.text for element in driver.find_elements(By.CLASS_NAME, 'gs_rt')]
            authors = [element.text for element in driver.find_elements(By.CLASS_NAME, 'gs_a')]
            doi_cites = {doi+str(i): [doi, title, author] for i, (title, author) in enumerate(zip(titles,authors))}
        except:
            doi_cites = {1: [doi, None, None]}
        all_cites.append(doi_cites)
    driver.close()
    cites_df_list = [pd.DataFrame.from_dict(entry,orient='index') for entry in all_cites]
    merged_cites = pd.concat(cites_df_list)
    merged_cites = merged_cites.set_axis(['Source DOI', 'Cite Title', 'Cite Author'], axis=1)
    merged_cites['Cite Author'] = merged_cites['Cite Author'].apply(lambda string: string[:string.find('-')] if type(string)==str else None)
    print('Done')
    return merged_cites

args = sys.argv
drive_folder_name = sys.argv[1]
article_links = get_article_links(args[2:])
article_data = get_article_data(article_links)
download_pdfs(article_data['PDF Link'])
article_data.to_csv('AER_id.csv')
file_links = upload_pdfs(article_data['Filename'],folder_name=drive_folder_name)
article_data['Google Drive Link'] = file_links
article_data.to_csv('AER_id.csv')
cites = search_gs(list(article_data.index))
cites.to_csv('cites.csv')
