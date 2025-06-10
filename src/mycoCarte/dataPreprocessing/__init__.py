import pandas as pd 


def remove_rows_Nans(df : pd.DataFrame, name :str = None):
    print(name)
    if isinstance(name, str):
        f'Removing Nans in {name} df'

    before = df.shape[0]
    df.dropna(inplace= True)
    after = df.shape[0]

    diff = before - after
    ratio = after / before
    ratio = round(ratio, 2)

    if diff > 0:
        print(f'Removed {diff} rows with Nans from {before} ({ratio}%)')
    # Count NaN values per column
    nan_counts = df.isna().sum()
    #print(nan_counts)    
    return df


def mergeDataset(final_df : pd.DataFrame, dfs_to_merge : dict):
    print(f'#{__name__}.mergeDataset')

    for name, df in dfs_to_merge.items():
        try:
            final_df = final_df.merge(df, on = 'FID',how = 'left')
            print(f'Merging {name} to full dataset')
        except Exception as e:
            print(f'Failed to merge {str(df)} data')
            print(e)

    final_df.dropna(axis = 0, how = 'any', inplace= True)

    return final_df 
