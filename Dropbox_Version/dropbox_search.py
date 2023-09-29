import dropbox
from pypdf import PdfReader
import pandas as pd
import io
import requests
import sys

"""
To run, enter root folder and desired output title as arguments

Example: python dropbox_search.py '/Journal_Search/AEJ_Policy/' 'aej_policy_results.csv'
"""
# assumes parent directory has same format as that created by upload.py script -- /Root/Month_Year/file.pdf



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


args = sys.argv
parent_directory = args[1]
result_name = args[2]

# metadata must be saved as 'metadata.csv' in parent directory and include 'folder' and 'file_name' columns
metadata_path = parent_directory+'metadata.csv'
_, response = dbx.files_download(metadata_path)
metadata_df = pd.read_csv(io.BytesIO(response.content))
response.close()

# enter search terms as list in terms_raw -- capitalization doesn't matter (everything will be made lowercase) -- phrases (separated by space) are ok
terms_raw = ['markets', 'equilibriate', 'experiment']

# terms made lowercase
terms = list(map(lambda x: x.lower(), terms_raw))
# space replaced with underscore in column name
columns = list(map(lambda x: x.replace(' ', '_'), terms))

# searches pdf file for terms
def f(folder, file_name, parent_directory, dbx, terms):
    path = f'{parent_directory}{folder}/{file_name}'
    _, response = dbx.files_download(path)
    # records pdf as bytes
    pdf_bytes = io.BytesIO(response.content)
    response.close()
    pdf = PdfReader(pdf_bytes)
    text = " ".join([page.extract_text() for page in pdf.pages]).lower()
    # count occurences for each term
    term_occurences = tuple(text.count(term) for term in terms)
    tot = sum(term_occurences)
    # derive dropbox link from folder and filename
    dbx_preview = f'https://dropbox.com/home{parent_directory}{folder}?preview={file_name}'
    return (dbx_preview,) + term_occurences + (tot,)

# results saved as list of tuples
results_list = []
tot = len(metadata_df)

# iterate through all PDFs in metadata csv file
for i, (folder, file_name) in enumerate(metadata_df[['folder', 'file_name']].itertuples(index=False, name=None)):
    print(f'{i+1}/{tot}')
    results_list.append(f(folder, file_name, parent_directory, dbx, terms))

results_df = pd.DataFrame(results_list, columns=['dropbox_link']+columns+['tot'])
result = metadata_df.join(results_df)
# output results to csv
result.to_csv(result_name)