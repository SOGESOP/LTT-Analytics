import logging
import pandas
import os

class MiscTools:
    # formats the logger, please hide your shock
    def format_logging(file_name:str):
        # adds the path to the logging/ viewing folder
        innital_logger_path=str(os.getcwd())
        loggger_folder_path=f"{innital_logger_path[:-12]}/log-view"
        logger_path=f"{innital_logger_path[:-12]}/log-view/{file_name}"
        # removes the loggin file form previous runthrough
        existing_files=os.listdir(loggger_folder_path)
        path='{cwd}/{name}'.format(cwd=os.getcwd(), name=file_name)
        if f'{file_name}' in existing_files:
            os.remove(logger_path)
        # configures logger
        logging.basicConfig(level=logging.INFO,
                            handlers=[logging.FileHandler(logger_path)])    
    # used to collect all the errors that have been recorded and adds them at the end of the logging file
    #~ to make it easier to see which errors have occured
    def error_collection(current_error):
        # checks if list error_list exists, if not then adds it in
        if 'error_list' not in  locals():
            global error_list
            error_list=[]
        error_list.append(current_error)
        return error_list
    
    # saves csv of dataframe, again please hide your shock
    def save_to_csv(dataframe_name:object, file_name:str):
        parent_folder=os.path.normpath(os.getcwd()+ os.sep +os.pardir)
        path="{parent_folder}/dataframe".format(parent_folder=parent_folder)
        dataframe_name.to_csv('{cwd}/{name}.csv'.format(cwd=path, name=file_name))
    
    # splices a string to find the substring you want, with the substring start index and ending
    #~ symbol being passed     
    def string_splicer_symbol(href,string_start_index, search_start_index, end_symbol, include_limit):
        end_index=0
        for char in href[search_start_index:]:
            end_index+=1
            if char in end_symbol:
                total_index=search_start_index+end_index
                # this checks if you want the limit symbol to be included in the string
                if include_limit==False:
                    target_string=href[string_start_index:(total_index-1)]
                else:
                    target_string=href[string_start_index:total_index]
                return target_string
        
        
