    # this will save the body information from the page, giving them the topic number as their title
    def scrape_soup(href:str, title_number:str):
        logging.info(f"Accessing the soup for page with id: {title_number}")
        # this section gets the content from the passed href
        response=requests.get(href)
        soup=BeautifulSoup(response.content, 'html.parser')
        main_text=soup.get_text(separator='#')
        # this paths to the page-contents folder and writes the info that has been obtained
        inital_path=os.getcwd()
        path="{init_path}/page-contents/{filename}.txt".format(init_path=inital_path[:-12], filename=title_number)
        with open(path, 'w') as f:
            f.write(main_text)


    # will run the text scraper to pick up all the comments on the page and add them to a text file
    def add_page_contents():
        # pretty self explanatory
        for href, title_id in zip(tp['href'], tp['Topic ID']):
            GetData.scrape_soup(href, title_id)
            logging.info(f"File added for title id: {title_id}")
