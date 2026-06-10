##if you get error "ModuleNotFoundError: No module named 'pandas'",
## you need to install pandas using pip
## pip install pandas
import pandas as pd

#load my csv file using pandas in a dataframe
df = pd.read_csv('dataset/nyc_weather.csv')

# Display the first few rows of the dataframe
#print(df.head())

## Accessing a specific column with first rows
## SELECT col FROM dbtable
#print(df['EST'])
## Accessing first cell (First row, first column)
#print(df['EST'][0])
## Access while columns 
#print(df[['EST', 'VisibilityMiles', 'Humidity']])
##Get the max value of temprature - SELECT MAX(TemperatureF) FROM dbtable
#print(df['Temperature'].max())
## Get dates on which it rain - SELECT date FROM table WHERE Events = 'Rain'
#print(df['EST'][df['Events'] == 'Rain'])
## Increase the temprature by 10 degrees and store in a new column Anubhav
#df['Anubhav'] = df['Temperature'] + 10
#print(df)
## Get the mean of the windSpeed
print(df['WindSpeedMPH'].mean())
print(df)
df.fillna(0, inplace=True)  # Fill NaN values with 0
print(df['WindSpeedMPH'].mean())  # Recalculate mean after filling NaN values
