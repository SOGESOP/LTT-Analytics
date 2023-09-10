import requests
import os
from bs4 import BeautifulSoup
from datetime import date
from datetime import timedelta


sample='yesterday at 19:15'

def main(sample):
    if 'yesterday' in sample:
        today=date.today()
        yesterday=(today-timedelta(days=1)).strftime("%B %d, %Y")
        print(today.strftime('%d'))

if __name__=='__main__':
    main(sample)