import pandas as pd
import numpy as np

def process_data_from_to_dict(attributes):
    attributes_list = []
    attributes_list.append(attributes)
    attributes_df = process_data(attributes_list)
    processed_attributes = attributes_df.to_dict('index')
    processed_attributes = processed_attributes[0]
    return processed_attributes

def process_data(data):
    df = pd.DataFrame(data, dtype=object).fillna(np.NaN)

    def get_first_word(col):
        return df[col].str.split('\s+').str[0]

    def find_index(row, string, split, occured):
        occurence = 0
        for index, split in enumerate(row.split(split)):
            if string in split:
                occurence += 1
            if occurence == occured:
                return index

    def apply_os(row):
        if 'Windows' in str(row['operatingSystem']):
            ostype = 'Windows'
        elif 'Mac' in str(row['operatingSystem']):
            ostype = 'MacOS'
        elif 'Chrome' in str(row['operatingSystem']):
            ostype = 'Chrome OS'
        else:
            ostype = np.NaN
        return ostype

    df['make'] = get_first_word('title')

    df['model'] = df.apply(lambda row: ' '.join(row.title.split(' ')[1:find_index(row.title, '"', ' ', 1)]), axis=1)
    
    if 'operatingSystem' in list(df.columns.values):
        df['operatingSystem'] = df.apply(apply_os, axis=1)
    
    if 'ram' in list(df.columns.values):
        df['ram'] = df.apply(lambda row: ' '.join(str(row.ram).split(' ')[0:2]), axis=1)
    
    if 'storage' in list(df.columns.values):
        df['storage'] = df.apply(lambda row: ' '.join(str(row.storage).split(' ')[:-1]), axis=1)
    
    if 'processor' in list(df.columns.values):
        df['processorMake'] = df.apply(lambda row: str(row.processor).split(' ')[1] if len(str(row.processor).split(' ')) > 1 else np.NaN, axis=1)
        df['processorModel'] = df.apply(lambda row: ' '.join(str(row.processor).split(' ')[2:find_index(row.processor, 'Processor', ' ', 1)]) if any('Processor' in string for string in str(row.processor).split(' ')) else (' '.join(str(row.processor).split(' ')[2:find_index(row.processor, 'chip', ' ', 1)+1]) if any('chip' in string for string in str(row.processor).split(' ')) else np.NaN), axis=1)

        df['cores'] = df.apply(lambda row: str(row.processor).split(' ')[find_index(row.processor, 'core', ' ', 1)] if any('core' in string for string in str(row.processor).split(' ')) else np.NaN, axis=1)

        df['clockSpeed'] = df.apply(lambda row: str(row.processor).split('-')[find_index(row.processor, 'GHz', '-', 1)] if any('GHz' in string for string in str(row.processor).split(' ')) else np.NaN, axis=1)

    columns_wanted = ['uuid',
        'productID',
        'url',
        'title',
        'make',
        'model',
        'price',
        'imgSrc',
        'rating',
        'ratingCount',
        'type',
        'operatingSystem',
        'ram',
        'processorMake',
        'processorModel',
        'cores',
        'clockSpeed',
        'storage',
        'screenSize',
        'touchscreen',
        'memoryCardReader',
        'camera',
        'batteryLife',
        'colour',
        'weight',
        'dimensions']

    for column in list(df.columns.values):
        if column not in columns_wanted:
            df.drop(columns=[column], inplace=True)
    return df