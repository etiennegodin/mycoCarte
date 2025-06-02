import pandas as pd

# Sample bias to grid 
# Merge bias layers
output_path = 'data/interim/geodata/vector/bias/csv/combinedBiases.csv'

def readBiasData(output_path = output_path):
    print(f'#{__name__}.readBiasData')
    df = pd.read_csv(output_path)

    return df