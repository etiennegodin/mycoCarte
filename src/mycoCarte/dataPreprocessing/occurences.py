import os 
import pandas as pd


def cleanOccurencesData(csv_occurences_path,cleaned_occurences_path, overwrite = False ):
    """
    Input : Takes in a csv path of occurences, reads and cleans it
    Output: Dict {path : Dataframe of cleaned occurences}
    """

    print(f'#{__name__}.cleanOccurencesData')

    def process():
        # read csv
        df = pd.read_csv(csv_occurences_path)

        # keep only canada & quebec
        df = df[df.countryCode == 'CA']
        df = df[df.stateProvince == 'Québec']

        # remove occurences with same latLong values (preserved specimens from older sources)
        df = df.drop_duplicates(subset=['decimalLatitude'], keep = 'last')
        df = df.drop_duplicates(subset=['decimalLongitude'],keep = 'last')

        # remove before 2000
        df = df[df.year >= 2000]

        df.to_csv(cleaned_occurences_path, index = False)
        print('Writting cleaned occurences to:')
        print(cleaned_occurences_path)

        output = {cleaned_occurences_path :df}
        return output
    
    def read():
        df = pd.read_csv(csv_occurences_path)
        output = {cleaned_occurences_path : df}
        return output

    if os.path.isfile(cleaned_occurences_path):
        print(f'Cleaned occurences already on file')
        if overwrite:
            print('Overwritting')
            output = process()
        else:
            # Written, not overriding, just reading it back to create dict and df 
            output = read()
    else:
        output = process
    
    return output


def preprocessOccurenceData():
    pass