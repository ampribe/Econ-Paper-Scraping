import pandas as pd
import regex as re
import sys

args = sys.argv
csv_title = args[1]

df = pd.read_csv(csv_title)

df['file_name'] = df['article_link'].apply((lambda x: re.search('(?<=\/)[a-z\.\d]+$', x).group()+'.pdf'))

df['folder'] = df['issue'].apply(lambda x: re.match('[A-Za-z]+\s\d+', x).group().replace(' ', '_'))

df.to_csv('metadata.csv')