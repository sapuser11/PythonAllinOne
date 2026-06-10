import os
import requests
from dotenv import load_dotenv
from pathlib import Path
import pandas as pd

def download_odata_excel():
    """
    Downloads XLSX file from SAP OData service using Basic Authentication
    with credentials from .env file
    """
    # Load environment variables from .env file
    load_dotenv()
    
    # Get credentials and URL from environment variables
    username = os.getenv('SAP_USERNAME')
    password = os.getenv('SAP_PASSWORD')
    base_url = os.getenv('SAP_ODATA_BASE_URL', 'http://stsrvr.mynetgear.com:8021')
    
    # Construct the full URL
    url = f"{base_url}/sap/opu/odata/sap/ZATS_SHOPE_CDS/zats_shope?$format=xlsx"
    
    # Check if credentials are available
    if not username or not password:
        raise ValueError("SAP credentials are not set in .env file")
    
    try:
        # Make the OData request with basic authentication
        response = requests.get(
            url,
            auth=(username, password),
            headers={'Accept': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'}
        )
        
        # Raise an exception if the request was unsuccessful
        response.raise_for_status()
        
        # Save the file locally
        output_path = Path('./zats_shope_data.xlsx')
        with open(output_path, 'wb') as file:
            file.write(response.content)
        
        print(f"Excel file downloaded successfully to: {output_path.absolute()}")
        return output_path
        
    except requests.RequestException as e:
        print(f"Error downloading OData file: {e}")
        raise

def process_excel_to_csv(excel_path):
    """
    Renames columns in the downloaded Excel file and converts it to CSV format.
    
    Args:
        excel_path (Path): Path to the downloaded Excel file
        
    Returns:
        Path: Path to the generated CSV file
    """
    try:
        # Read the Excel file
        df = pd.read_excel(excel_path)
        
        # Rename columns
        column_mapping = {
            df.columns[0]: 'id',
            df.columns[1]: 'type',
            df.columns[2]: 'name',
            df.columns[3]: 'country',
            df.columns[4]: 'year',
            df.columns[5]: 'duration',
            df.columns[6]: 'description',
            df.columns[7]: 'image'
        }
        
        df = df.rename(columns=column_mapping)
        
        # Save as CSV
        output_path = Path('./movies.csv')
        df.to_csv(output_path, index=False)
        
        print(f"CSV file created successfully at: {output_path.absolute()}")
        return output_path
    
    except Exception as e:
        print(f"Error processing Excel file: {e}")
        raise

if __name__ == "__main__":
    download_odata_excel()
    process_excel_to_csv(Path('./zats_shope_data.xlsx'))