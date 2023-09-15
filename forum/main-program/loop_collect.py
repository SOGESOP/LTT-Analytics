from MiscToolsMain import MiscTools
import time
import logging
import os
import subprocess
import pandas

# run the collect
# save the csv info
# consider how comment files will be written over, so think of way to remove bad rows from outdated comment files

# while True:
#     run collect
#     combine csv

# def run_main_collect_cycle():
#     collect_file_path=f'{os.getcwd()}/collect.py'
#     analyse_file_path=f'{os.getcwd()}/translate.py'    
#     try:
#         subprocess.run(["python", collect_file_path], check=True)
#         subprocess.run(["python", analyse_file_path], check=True)
#     except Exception as error:
#         logging.error(f'Main Program has failed to run due to {error}')

def run_main_collect_cycle():
    # find a way to run the script and wait on the completion of the 
    # collect script to run the translate script
    work on this bit here
    pass


def import_dataframe(file_name:str, file_format:str)-> object:
    parent_folder=os.path.normpath(os.getcwd()+ os.sep +os.pardir)
    path="{path_to_parent}/dataframe/{name}.{file_type}".format(path_to_parent=parent_folder, name=file_name, file_type=file_format)
    # tp is the name of the main topic dataframe, i cant remeber why that is the name but there was a good reason i promise
    return path
    
def combine_csv():
    logging.info('Dataframes being imported')
    path=import_dataframe('collect_run', 'csv')
    global tp
    tp=pandas.read_csv(path)
    path=import_dataframe('main', 'csv')
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

def main():
    MiscTools.format_logging('loop-collect.log')
    while True:    
        run_main_collect_cycle()
        combine_csv()
        time.sleep(3600)


if __name__=='__main__':
    main()
    
    
    