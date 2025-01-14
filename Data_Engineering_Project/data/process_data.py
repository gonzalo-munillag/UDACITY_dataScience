import sys
import pandas as pd
import numpy as np
from sqlalchemy import create_engine


def load_data(messages_filepath, categories_filepath):
    
    """ Loads data from datasets and wrangles them for later model training.
    
    INPUT
    messages_filepath (str) -- filepath to the messages dataset
    categories_filepath (str) -- filepath to the categories dataset
    
    OUTPUT
    df (DataDrame) -- Dataframe containing both files
    """
    # read files as dataframes
    messages = pd.read_csv(messages_filepath)
    categories = pd.read_csv(categories_filepath)
    
    # Merge data
    df = pd.merge(messages, categories, left_on='id', right_on='id', how='left')
    
    return df

def clean_data(df):
    
    """ Cleans dataframe
    
    INPUT
    df (DataDrame) -- Dataframe containingall information
    
    OUTPUT
    df (DataDrame) -- Cleaned dataframe
    """
    
    # Extract column names
    # Extract the first value of the categories column as a string
    cat_names_series = pd.Series(df['categories'].iloc[0])[0]

    # Create list of categories by separating by ;
    sep = ';'
    cat_names_series = cat_names_series.split(';')

    # Eliminate the unnecessary part of the stirng after -
    cat_names_series = pd.Series(cat_names_series).str.split('-', 1).apply(lambda x: x[0])

    # create a dataframe of the 36 individual category columns
    categories = pd.Series(df['categories']).str.split(pat=';',expand=True)
    categories.columns = cat_names_series

    # Convert values of the categories (0 or 1) into numeric
    for column in categories.columns:
        # set each value to be the last character of the string
        categories[column] = categories[column].astype(str).str.get(-1)

        # convert column from string to numeric
        categories[column] = pd.to_numeric(categories[column])
        
    # We drop any row that is not binary (above 1)
    categories = categories[~(categories > 1).any(1)]

    # drop the original categories column from `df`
    df.drop(columns=['categories'], inplace=True, axis=1)
    
    # concatenate the original dataframe with the new `categories` dataframe
    df = pd.concat([df, categories], axis=1)

    # Remove duplicates
    df.drop_duplicates(inplace=True)
        
    return df


def save_data(df, database_filename):
    
    """ Saves dataframe in a sql database
    
    INPUT
    df (DataDrame) -- Dataframe containingall information
    database_filename (str) -- Path where to save the dataset
    """  
    
    # Start sql engine
    engine = create_engine('sqlite:///{}'.format(database_filename))
    
    # Save df to sql database
    df.to_sql(database_filename.split('/')[-1], engine, index=False, if_exists='replace')

def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
        
#         print(df.columns)
#         print(df.head)
        
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()
