# AER-Project
Downloads AER PDFs, saves metadata, uploads to Google Drive, and finds citations

This script downloads all American Economic Review articles from selected months, saves metadata of each paper to csv, uploads each pdf to a Google Drive folder, and saves the title and author of papers that cite each article to csv. 

The script requires:
- Python
- Firefox and Chrome browsers
- Google Drive API Credentials
- Selenium, pandas, and Python Google client library
- internet connection with access to AER articles

To use the script:
1. Save the script to folder you would like to download PDFs
2. Get Google Drive API credentials
   - You can install required Google libraries using "pip install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib"
   - Go to https://console.cloud.google.com/apis/dashboard and create new project
   - Click "Enable APIs and Services" and enable Google Drive API
   - Go to credentials tab, click "Create Credentials", and select OAuth Client ID. Then, you will need to fill out OAuth Consent Screen.
   - Go back to credentials tab, click "Create Credentials", and select OAuth Client ID. Then, set application type as "Desktop App" and download client secret json.
   - Save this json as "credentials.json" in the same folder as the script.
3. Run the script, passing the desired Google Drive folder name and AER issues as arguments. For example, "python script.py 'AER Articles' 'November 2022' 'December 2022'"
4. While running, the program will open a browser for you to allow access to Google Drive. Also, the program will specify when you may need to submit CAPTCHA while the program accesses Google Scholar. 
