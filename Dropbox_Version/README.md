The scripts included will scrape, upload, and search AER/AEJ PDFs. 

Downloading metadata and PDFs requires:
1. Python
2. The following Python packages: pandas, selenium, regex, and beautifulsoup4
3. An internet connection with access to AER and AEJ articles
    - Downloading all the files at once using 'download_fast.py' requires access to two wifi networks with access to AER/AEJ PDFs as well as the Windows operating system. The default networks in download_fast.py are 'uchicago-secure' and 'eduroam', but you can use any two networks with article access by changing the name of the networks in 'download_fast.py'. On MacOS, the commands to change networks won't work, so you have to use 'download_slow.py'. This script will download 99 PDFs at a time and requires you to wait a few hours or reset internet connection between downloads to avoid getting banned. 

Uploading to Dropbox and searching files in Dropbox requires pypdf (You can also use PyPDF2, but you have to change imports in scripts) and the Dropbox API client (can be installed using 'pip install dropbox'). You will also need to go to [this link](https://www.dropbox.com/developers/apps), set up a Dropbox app, and modify the upload.py and dropbox_search.py scripts with the app key and app secret. 

To use the scripts:
1. Save all the scripts to a new folder. This folder is where all the PDFs will be downloaded. 
2. Run the 'get_download_links.ipynb' Jupyter notebook to compile the download links. 
    - The Jupyter notebook will save a csv file with links to download each PDF to the current directory. You will need to pass the name of this csv file as an argument to the download script.
3. Open a terminal in the folder and run either 'download_fast.py' or 'download_slow.py', passing the csv file name as an argument. For example, 'python download_fast.py download_links.csv'. 
    - Again, download_fast.py requires two internet connections with access to the PDFs and the Windows operating system. 
    - It is ok if the download process is interrupted because the script tracks PDFs already in the folder and will not download them again. 
4. Check to see if there are 'crdownload' files in the PDF folder. If so, some of the PDFs didn't finish downloading. The easiest way to resolve this is to delete the 'crdownload' files and run the download script again. Only the missing PDFs will be downloaded. 
5. Before running upload.py, modify the app key and app secret lines at the top of the script with your app key and app secret. To run upload.py, pass the filename of the previous csv file and the root folder to upload PDFs as arguments. Example: 'python upload.py METADATA_FILE.csv /DROPBOX_ROOT_FOLDER/'. Note that the root folder must begin and end with a slash. 
    - Dropbox will display the entire path to a folder at the top when you have a folder open in Dropbox ('Dropbox/Journal_Search/AEJ_Applied'). Include the entire path to the root folder excluding 'Dropbox' at the beginning. For example, '/Journal_Search/AEJ_Applied/'. 
    - The script will print an authorization link and prompt you to enter a code. Enter the link in a browser, authorize the application, and enter the resulting code in the command prompt. 
    - The script will check for pre-existing folders/files, so interruptions to the upload process are ok. Just run the script again. 
    - The script will create new folders for each issue formatted as Month_Year and upload PDFs to their respective folders. 
6. Before running dropbox_search.py, you will need to save a csv file including at least 'folder' (not including root folder) and 'file_name' columns as 'metadata.csv' to the root folder. Run 'get_metadata.py', passing the download links csv name as an argument to get the metadata file ('python get_metadata.py 'download_links.csv''). This script will create 'metadata.csv' in the current folder which you should upload to the root folder on Dropbox. 
7. Then, modify 'app_key' and 'app_secret' at the top of dropbox_search.py with your app key and app secret. Modify the 'terms_raw' variable with the terms you would like to search for. Capitalization does not matter because the script will make all text lowercase. You can also include series of words separated by spaces (as one string) in the list. 
8. Run dropbox_search.py, passing the root folder and your desired output csv title as arguments ('python dropbox_search.py '/Journal_Search/AEJ_Policy/' 'aej_policy_results.csv''). Like upload.py, the script will prompt you to authenticate before searching the pdfs. This script will save a csv file with results to the current folder. 
