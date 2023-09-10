from MiscToolsMain import MiscTools
import logging
import requests
import pandas
import os
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

    
# i could use classes to include multiple web scrapers in one section?

# functions that will get data from the ltt forum
class GetData:        
    # sets up the selenium driver
    def setup_driver():
        logging.info("Driver setup started")
        global driver
        # selects chrome as driver
        options=Options()
        options.add_argument('--headless=new')
        driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        
    # used to collect all the hrefs of the topics on the forum discover page
    def collect_href():
        logging.info('Topic page collection initiated')
        # forum discover page url 
        main_url='https://linustechtips.com/discover/'
        # gets the page and collects the contents of the page
        driver.get(main_url)
        response=requests.get(main_url)
        # creates a variable with the html content of the page
        soup=BeautifulSoup(response.content, 'html.parser')
        # a list to store all the links that we find
        external_references=[]
        # goes through the page content and chekcs for hrefs (links)
        for link in soup.find_all('a'):
            current=link.get('href')
            # this just ensures that a nonetype has not been grabbed and breaks the code
            if current:
                # checks if the item found in the soup is a reference and if so it includes it in the list
                if 'https' in current:
                    logging.info(f"Unfiltered page added with href: {current}")
                    external_references.append(current)
        # removes any possible identical duplicates from the list
        external_references=set(external_references)
        
        # formats the hrefs to remove any unnecesary specific information, like linking to particular 
        #~ comments, and just has them direct straight to the topic main page
        external_references_main_page=[]
        for href in list(external_references):
            # starts searching for forwardslashes after the topic name in the url, as any info after
            #~ the forwardslash at the end of the topic name is extranious
            if 'https://linustechtips.com/topic/' in href:
                formatted_href=MiscTools.string_splicer_symbolic(href, 0, 32, '/', True)
                external_references_main_page.append(formatted_href)
                        
        # returns a list of all the topic urls found from the 'main_url' page
        return external_references_main_page
    
    # checks for the href topic title, and the length parameter corresponds
    #~ to the number of href in the tp dataframe
    def check_href_topic_title(length:int):
        title_dict_with_id={}
        for i in range(0,length):
            # acceses the urls from the tp dataframe
            current_url=tp.iloc[i, 0]
            # adds to the logging file what page is being accesssed
            logging.info(f"Connecting to page: {current_url}")
            # accesses the url from the dataframe 
            driver.get(current_url)
            # collects the elements that are in the title section on the page
            elements=driver.find_elements(By.XPATH,
                                          '//*[@id="ipsLayout_mainArea"]/div[1]/div[1]/div/h1/span')
            # goes through the title elements and extracts the text, and adds it to a list
            for entry in elements:
                # finds the topic number in the current_irl
                topic_number=MiscTools.string_splicer_symbolic(current_url, 32, 32, '-', False)
                title_dict_with_id[int(topic_number)]=entry.text
                
        return title_dict_with_id

    # this will get all the comment information from the page that is passed, and create a dict where
    #~ the first entry is the href:topic number and the other entreis are the index: comment content   
    def get_comment_content_and_date(href:str):
        driver.get(href)
        elements=driver.find_elements(By.CSS_SELECTOR, 'div.cPost_contentWrap > div.ipsType_normal.ipsType_richText.ipsPadding_bottom.ipsContained')
        comment_content=[]    
        # adds to dictionary the comment text and an index of where it was found on the page
        for comment in elements:
            comment_content.append(comment.text)
        # returns the dict
        date=driver.find_element(By.CSS_SELECTOR, '#ipsLayout_mainArea > div.ipsPageHeader.ipsResponsive_pull.ipsBox.sm\:ipsPadding\:half.ipsMargin_bottom > div.ipsPageHeader__meta.ipsFlex.ipsFlex-jc\:between.ipsFlex-ai\:center.ipsFlex-fw\:wrap.ipsGap\:3.ipsGap_row\:0.ipsSpacer_top.ipsSpacer_half > div.ipsFlex-flex\:11.cTopicHeader_userInfo > div > div > div > span > span > time')
        date_posted=date.text  
        for idx, x in enumerate(tp['href']):
            if x==href:
                tp.loc[idx,'Date Posted']=date_posted
        return comment_content
        
# functions that will create the dataframe from the topic pages
class TopicDataframe:
    # this will filter the topic href as well as the topic number ID
    def filtering_topic_href(info:list):
        logging.info("href and topic ID being filtered")
        # creates a new dict for href and topic numbers
        title_href_dict_with_id={}
        # adds list of topics that are included so checks can be done to ensure no duplicates are added
        included_topics=[]
        for href in info:
            # finds the topic number in the href and adds its asociated href to a dict
            topic_number=MiscTools.string_splicer_symbolic(href, 32, 32, '-', False)
            if topic_number not in included_topics:
                included_topics.append(topic_number)
                title_href_dict_with_id[topic_number]=href
        # checks if any duplicate topics have been added and if so adds an error message 
        if len(included_topics)!=len(set(included_topics)):
            for i in included_topics:
                if i in set(included_topics):
                    included_topics.remove(i)
            error_1=f"All duplicates have not been removed, remaining are: {included_topics}"
            MiscTools.error_collection(error_1)
            logging.error(error_1)

        return title_href_dict_with_id

    def inital_form_tp(title_href_dict_with_id:dict):
        logging.info("Initial Dataframe formed")

        # sets up the database, (tp stands for title pages)
        global tp
        tp=pandas.DataFrame(data=list(title_href_dict_with_id.values()))
        tp=tp.set_axis(['href'],axis=1)
        tp.insert(1, 'Topic ID', title_href_dict_with_id.keys())
        tp.insert(2, 'Topic Title', 'nan')
        tp.insert(3, 'Date Posted', 'nan')
        tp.insert(4, 'Total Comments', 'nan')
        tp.insert(5, 'Total Likes', 'nan')
        # adds a csv of the dataframe
        MiscTools.save_to_csv(tp,'main')
        return list(title_href_dict_with_id.values())
            
            
    # adds the title_names to the associated title ids
    def add_title_names(title_dict:dict):
        logging.info("Title names being added to the Dataframe")
        ordered_title_dict={}
        for x in tp['Topic ID']:
        # changing the order of the dict so it matches the order of the tp dataframe
            if x in title_dict.keys():
                ordered_title_dict[x]=(title_dict.get(x))
        # adding in the changed information into the tp dataframe
        for idx,x, in enumerate(ordered_title_dict.values()):
            tp.loc[idx, 'Topic Title']=x
        # updates the csv used for easy viewing
        MiscTools.save_to_csv(tp, 'main')
        
    def add_comment_contents():
        index=0
        # gets the comment content 
        for href, title_id in zip(tp['href'], tp['Topic ID']):
            comment_content_list=GetData.get_comment_content_and_date(href)
            logging.info(f"Comment content found for: {title_id}")
            comment_content_string=""
            for i in comment_content_list:
                comment_content_string+=f'\n {i}'
            # saves a file with the comment content to the topic id it was gained from
            parent_folder=os.path.normpath(os.getcwd()+ os.sep +os.pardir)
            path="{init_path}/page-contents/{filename}.txt".format(init_path=parent_folder, filename=title_id)
            with open(path, 'w') as f:
                f.write(comment_content_string)    
        # saves the dataframe to include the addition of the dates
        MiscTools.save_to_csv(tp, 'main')
            
        
def main():
    MiscTools.format_logging('collect.log')
    MiscTools.remove_csv('main.csv')
    GetData.setup_driver()
    href_list=GetData.collect_href()
    filtered_href_dict=TopicDataframe.filtering_topic_href(href_list)
    filtered_list=TopicDataframe.inital_form_tp(filtered_href_dict)
    title_dict=GetData.check_href_topic_title(len((filtered_list)))
    TopicDataframe.add_title_names(title_dict)
    TopicDataframe.add_comment_contents()
    
    # TopicDataframe.add_page_contents()
    # next changes: add in more information in other columns
    
    
    
    # program end cap
    logging.error(f"{MiscTools.error_collection('Program_end')}")
    
if __name__=='__main__':
    main()