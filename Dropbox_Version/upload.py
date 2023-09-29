import dropbox
import requests
import sys
import pandas as pd
import regex as re

## python upload.py METADATA_FILE.csv /DROPBOX_ROOT_FOLDER/
## Root folder must begin and end with /
## Root folder example: '/Journal_Search/AEJ_Applied/' 




# https://stackoverflow.com/questions/56381357/implementing-oauth-on-dropbox-api-python
app_key = 'ENTER_APP_KEY'
app_secret = 'ENTER_APP_SECRET'

# build the authorization URL:
authorization_url = "https://www.dropbox.com/oauth2/authorize?client_id=%s&response_type=code" % app_key

# send the user to the authorization URL:
print('Go to the following URL and allow access:')
print(authorization_url)

# get the authorization code from the user:
authorization_code = input('Enter the code:\n')

# exchange the authorization code for an access token:
token_url = "https://api.dropboxapi.com/oauth2/token"
params = {
    "code": authorization_code,
    "grant_type": "authorization_code",
    "client_id": app_key,
    "client_secret": app_secret
}
r = requests.post(token_url, data=params)
access_token = r.json()['access_token']

dbx = dropbox.Dropbox(access_token)


## Load list of articles
args = sys.argv
csv_title = args[1]
metadata_df = pd.read_csv(csv_title)
metadata = list(metadata_df.itertuples(index=False, name=None))

## Associate each article with folder based on issue
file_folder_list = []
for article_link, _, _, issue in metadata:
    # filenames (automatically determined when downloaded) come from article link
    filename = re.search('(?<=\/)[a-z\.\d]+$', article_link).group()+'.pdf'
    # Each issue gets its own folder -- Formatted as Month_Year ex. April_2020
    folder = re.match('[A-Za-z]+\s\d+', issue).group().replace(' ', '_')
    file_folder_list.append((filename, folder))

## Stores folders/articles as dictionary, key = folder, value = list of articles in folder
folder_dict = {}
for filename, folder in file_folder_list:
    if folder in folder_dict:
        folder_dict[folder].add(filename)
    else:
        folder_dict[folder] = {filename}


root_folder = args[2]
tot_folders = len(folder_dict)

# checks for subfolders that have already been made (if script has already been partially run)
current_folders = set([entry.name for entry in dbx.files_list_folder(root_folder).entries 
              if type(entry) == dropbox.files.FolderMetadata])


# loops through folders and uploads all PDFs associated with that folder
for i, (folder, file_set) in enumerate(folder_dict.items()):
    # only creates folders that have not already been made
    if folder not in current_folders:
        dbx.files_create_folder(root_folder+folder)

    print(f'Uploading files to {folder}, {i+1}/{tot_folders}')
    
    # checks what pdfs have already been uploaded to folder 
    current_pdfs = {entry.name for entry in dbx.files_list_folder(root_folder+folder).entries if entry.name[-4:] == '.pdf'}
    
    # only upload files not already uploaded
    files_to_upload = file_set.difference(current_pdfs)

    # upload all files for this folder
    for file in files_to_upload:
        upload_path = root_folder+folder+'/'+file
        with open(file, 'rb') as f:
            dbx.files_upload(f.read(), upload_path)
