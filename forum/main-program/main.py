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
from selenium.webdriver.support import expected_conditions as EC
from datetime import date
from datetime import timedelta
from datetime import datetime
from time import time

    
# i could use classes to include multiple web scrapers in one section?

# functions that will get data from the ltt forum
class GetData:        
    # sets up the selenium driver
    def setup_driver():
        logging.info("Driver setup started")
        global driver
        options=Options()
        options.add_argument('--headless=new')
        options.add_argument("--remote-allow-origins=*")
        driver=webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    

    def scroll_topic_page():
        main_url='https://linustechtips.com/discover/'
        driver.get(main_url)
        for i in range(0, 10):
            logging.info('Furhter topics have been loaded {i} times'.format(i=i))
            wait = WebDriverWait(driver, 4)  # Wait for a maximum of 10 seconds
            load_more_button=wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-action="loadMore"]')))
            load_more_button.click()

        logging.info('Topic page collection initiated')
        response=requests.get(main_url) 
        return response
        
        
    # used to collect all the hrefs of the topics on the forum discover page
    def collect_href():
        response=GetData.scroll_topic_page()
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
            path=f"{parent_folder}{os.sep}ltt-analytics{os.sep}forum{os.sep}page-contents{os.sep}{topic_id}.txt"
            with open(path, 'w', encoding="utf-8") as f:
                f.write(comment_content_string)    
        MiscTools.save_to_csv(tp, 'collect_run')            
        
    # imports the dataframe, only works with csv and excel at the moment as thats all im using 
    def import_dataframe(dataframe_name:str, file_format:str, seperator:str):
        parent_folder=os.path.normpath(os.getcwd()+ os.sep +os.pardir)
        path=f"{parent_folder}{os.sep}ltt-analytics{os.sep}forum{os.sep}dataframe{os.sep}{dataframe_name}.{file_format}"
        # tp is the name of the main topic dataframe, i cant remeber why that is the name but there was a good reason i promise
        global tp
        if file_format=='xlsx':
            tp=pandas.read_excel(path)
        if file_format=='csv':
            tp=pandas.read_csv(path, sep=seperator)
    # this adds the number of comments on the topic that have been recorded to the dataframe
    def add_comment_number(topic_number:str, page_comments:list[str]):
        number_of_comments=int(len(page_comments))
        # matche the topic number and then adds the number of comments in the right location
        for idx,entry in enumerate(tp['Topic ID']):
            if entry==topic_number:
                tp.loc[idx, 'Total Comments']=number_of_comments
        logging.info(f'{number_of_comments} found for topic {topic_number}')
    
    
    
    
    # the classes are used to provide a seperation between different function, some functions engage in activities that would fit in two classes, but generally
# they are seperated between reading the comment text files, interacting with the dataframe

# involves reading the comment info from plain text files and reformating it to be useful format
class TextFormatConversion:
    def reading_file_into_list(topic_id:str):
        inital_file_path=f"{os.path.normpath(os.getcwd()+os.sep+os.pardir)}{os.sep}ltt-analytics{os.sep}forum"        
        file_path="{initial}/page-contents/{name}.txt".format(initial=inital_file_path, name=topic_id)
        f=open(file_path, 'r', encoding="utf-8")
        logging.info('Contents for file {name} has been read'.format(name=topic_id))
        # Converts the file into a list of all the lines and then returns that list
        file_contents:list[str]=(f.read()).splitlines()
        return file_contents
    
    # seperates the list where each element is a line from the original file into a list where each element is a comment
    def seperating_comments(comment_content:list):
        seperated_comments=[]
        current_comment=str()
        for entry in comment_content:
            # this checks for the keyword at the end
            if 'COMMENT_BREAK' in entry:
                seperated_comments.append(current_comment)
                current_comment=str()
            current_comment+=entry
        seperated_comments.append(current_comment)
        return seperated_comments
   
    # reformats the topic files to be in a more re>adable form with the comments seperated correctly
    def formatting_topic_files(topic_id:str, comment_content:list[str]):
        parent_folder=f"{os.path.normpath(os.getcwd()+ os.sep +os.pardir)}{os.sep}ltt-analytics{os.sep}forum"
        path="{path_to_parent}/page-contents/{name}.txt".format(path_to_parent=parent_folder, name=topic_id)
        os.remove(path)
        comment_content_string='Post Content\n'
        for comment in comment_content:
            comment_content_string+=f"{comment}\n\n"
        # writes the string content into the file
        with open(path, 'w', encoding="utf-8") as f:
            f.write(comment_content_string)
        
        
class LoopCollect:       
    def import_dataframe(file_name:str, file_format:str)-> object:
        parent_folder=os.path.normpath(os.getcwd()+ os.sep +os.pardir)
        path="{path_to_parent}/dataframe/{name}.{file_type}".format(path_to_parent=parent_folder, name=file_name, file_type=file_format)
        # tp is the name of the main topic dataframe, i cant remeber why that is the name but there was a good reason i promise
        return path

    def combine_csv():
        logging.info('Dataframes being imported')
        path=LoopCollect.import_dataframe('collect_run', 'csv')
        global tp
        tp=pandas.read_csv(path)
        path=LoopCollect.import_dataframe('main', 'csv')
        placeholder=pandas.read_csv(path)
        for idx, import_topic_id in enumerate(tp['Topic ID']):
            for existing_topic_id in placeholder['Topic ID']:
                if import_topic_id==existing_topic_id:
                    tp.drop(idx, axis=0, inplace=True)
        frames=[tp, placeholder]
        global df
        df=pandas.concat(frames)
        df.reset_index(inplace=True, drop=True)
        logging.info(f'Main dataframe shape: {df.shape}')
        MiscTools.save_to_csv(df, 'main')

    def run_main_collect_cycle():        
        pass


def main():
    MiscTools.format_logging('main.log')
    MiscTools.remove_csv('collect_run.csv')
    GetData.setup_driver()
    href_list=GetData.collect_href()
    filtered_href_dict=TopicDataframe.filtering_topic_href(href_list)
    filtered_list=TopicDataframe.inital_form_tp(filtered_href_dict)
    title_dict=GetData.check_href_topic_title_and_date(len((filtered_list)))
    TopicDataframe.add_title_names(title_dict)
    TopicDataframe.add_comment_contents()
    # translate begins
    TopicDataframe.import_dataframe('collect_run', 'csv', seperator=',')
    # The main loop that goes through all the comment text files and seperates out the comments and re-writes the files in a
    # better format
    for topic_number in tp['Topic ID']:
        file_in_list_form=TextFormatConversion.reading_file_into_list(topic_number)
        seperated_comments=TextFormatConversion.seperating_comments(file_in_list_form)
        TextFormatConversion.formatting_topic_files(topic_number, seperated_comments)
        TopicDataframe.add_comment_number(topic_number, seperated_comments)
    MiscTools.save_to_csv(tp, 'collect_run')
    logging.error(f"{MiscTools.error_collection('Program_end')}")

    LoopCollect.combine_csv()
    while True:    
        LoopCollect.run_main_collect_cycle()
        LoopCollect.combine_csv()
        time.sleep(3600)

if __name__=='__main__':
    main()
