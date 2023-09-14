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
from selenium.webdriver.support.ui import WebDriverWait

    
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
        main_url='https://linustechtips.com/discover/'
        driver.get(main_url)
        response=requests.get(main_url)
        soup=BeautifulSoup(response.content, 'html.parser')
        external_references=[]
        for link in soup.find_all('a'):
            current=link.get('href')
            if current:
                if 'https' in current:
                    logging.info(f"Unfiltered page added with href: {current}")
                    external_references.append(current)
        external_references=set(external_references)
        # formats the href to direct straight to the topic page
        external_references_main_page=[]
        for href in list(external_references):
            if 'https://linustechtips.com/topic/' in href:
                formatted_href=MiscTools.string_splicer_symbolic(href, 0, 32, '/', True)
                external_references_main_page.append(formatted_href)
                        
        return external_references_main_page
    
    # checks for the href topic title, and the length parameter corresponds
    #~ to the number of href in the tp dataframe
    def check_href_topic_title_and_date(length:int):
        title_dict_with_id={}
        for i in range(0,length):
            # acceses the urls from the tp dataframe
            current_url=tp.loc[i, 'href']
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
                
            # collects the date that the post was made on
            date=driver.find_element(By.CSS_SELECTOR, '#ipsLayout_mainArea > div.ipsPageHeader.ipsResponsive_pull.ipsBox.sm\:ipsPadding\:half.ipsMargin_bottom > div.ipsPageHeader__meta.ipsFlex.ipsFlex-jc\:between.ipsFlex-ai\:center.ipsFlex-fw\:wrap.ipsGap\:3.ipsGap_row\:0.ipsSpacer_top.ipsSpacer_half > div.ipsFlex-flex\:11.cTopicHeader_userInfo > div > div > div > span > span > time')
            date_posted=date.accessible_name
            for idx, x in enumerate(tp['href']):
                if x==current_url:
                    tp.loc[idx,'Date Posted']=date_posted
            logging.info(f"Comment date collected for href: {current_url}")
        return title_dict_with_id

    def get_comment_content( href:str)->list[str]:
        logging.info(f'Comment content added for href: {href}')
        driver.get(href)
        # if element is missing fails through to except conditions
        comment_elements=driver.find_elements(By.CSS_SELECTOR, 'div.cPost_contentWrap > div.ipsType_normal.ipsType_richText.ipsPadding_bottom.ipsContained')
        comment_content=[]
        for comment in comment_elements:
            comment_content.append(comment.text)
            comment_content.append('COMMENT_BREAK')
        comment_interactions=GetData.get_comment_interactions(href)
        try:
            page_number_element=driver.find_element(By.CLASS_NAME, 'ipsPagination')
            element_text=(page_number_element.text).replace(' ', '')
            # last character of string is the total number of pages
            page_count=int(element_text[-1])
            comment_content_and_interactions=GetData.mutiple_comment_pages(href, page_count, comment_content)
            comment_interactions+=comment_content_and_interactions[1]
            
        except:    
            logging.debug(f'The following href only had one page of comments: {href}')

        # add comment interactions to dataframe
        for idx,entry in enumerate(tp['href']):
            if entry==href:
                tp.loc[idx, 'Total Interactions']=comment_interactions

        return comment_content
    
    # interactions are the likes, agree, etc posted on each comment
    def get_comment_interactions(href:str)->int:
        driver.get(href)
        logging.info(f'Collecting comment interactions for: {href}')
        interactions=driver.find_elements(By.CSS_SELECTOR, '[data-ipsdialog-title="See who reacted to this"]')
        total_comment_interactions=0
        for comment in interactions:
            if (comment.text).isnumeric():
                num_comment_interactions=int(comment.text)
                total_comment_interactions+=num_comment_interactions
        logging.info(f'{total_comment_interactions} comments interactions recorded')

        return total_comment_interactions


    def mutiple_comment_pages(href:str, page_count:int, comment_content:list[str])->tuple:
        comment_interactions_multiple_pages=0
        for page_num in range(2, int(page_count)+1):
            page_url=f"{href}/page/{page_num}"
            logging.info(f'Connecting to page {page_num} for href: {href}')
            driver.get(page_url)
            comment_elements=driver.find_elements(By.CSS_SELECTOR, 'div.cPost_contentWrap > div.ipsType_normal.ipsType_richText.ipsPadding_bottom.ipsContained')
            for comment in comment_elements:
                comment_content.append(comment.text)
                comment_content.append('COMMENT_BREAK')
            comment_interactions=GetData.get_comment_interactions(page_url)
            comment_interactions_multiple_pages+=comment_interactions
        return comment_content, comment_interactions_multiple_pages
        
        
class TopicDataframe:
    # this will filter the topic href as well as the topic number ID
    def filtering_topic_href(info:list)-> dict:
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

    def inital_form_tp(title_href_dict_with_id:dict)-> list:
        logging.info("Initial Dataframe formed")

        global tp
        tp=pandas.DataFrame(data=list(title_href_dict_with_id.values()))
        tp=tp.set_axis(['href'],axis=1)
        tp.insert(1, 'Topic ID', title_href_dict_with_id.keys())
        tp.insert(2, 'Date Posted', 'nan')
        tp.insert(3, 'Total Comments', 'nan')
        tp.insert(4, 'Total Interactions', 'nan')
        MiscTools.save_to_csv(tp,'collect_run')
        return list(title_href_dict_with_id.values())
            
            
    def add_title_names(title_dict:dict):
        logging.info("Title names being added to the Dataframe")
        ordered_title_dict={}
        for x in tp['Topic ID']:
        # changing the order of the dict so it matches the order of the tp dataframe
            if x in title_dict.keys():
                ordered_title_dict[x]=(title_dict.get(x))
        for idx,x, in enumerate(ordered_title_dict.values()):
            tp.loc[idx, 'Topic Title']=x
        MiscTools.save_to_csv(tp, 'collect_run')
        
    def add_comment_contents():
        for href, topic_id in zip(tp['href'], tp['Topic ID']):
            comment_content_list=GetData.get_comment_content(href)
            logging.info(f"Comment content found for: {topic_id}")
            comment_content_string=""
            for i in comment_content_list:
                comment_content_string+=f'\n {i}'
            # saves a file with the comment content to the topic id it was gained from
            parent_folder=os.path.normpath(os.getcwd()+ os.sep +os.pardir)
            path="{init_path}/page-contents/{filename}.txt".format(init_path=parent_folder, filename=topic_id)
            with open(path, 'w') as f:
                f.write(comment_content_string)    
        MiscTools.save_to_csv(tp, 'collect_run')            
        
def main():
    MiscTools.format_logging('collect.log')
    MiscTools.remove_csv('collect_run.csv')
    GetData.setup_driver()
    href_list=GetData.collect_href()
    filtered_href_dict=TopicDataframe.filtering_topic_href(href_list)
    filtered_list=TopicDataframe.inital_form_tp(filtered_href_dict)
    title_dict=GetData.check_href_topic_title_and_date(len((filtered_list)))
    TopicDataframe.add_title_names(title_dict)
    TopicDataframe.add_comment_contents()
    
    logging.error(f"{MiscTools.error_collection('Program_end')}")
    
if __name__=='__main__':
    main()
    
    