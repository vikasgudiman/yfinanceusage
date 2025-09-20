import pandas as pd

def read_data(file_path):

    stocks_df = pd.read_excel(file_path, sheet_name="Sheet1", skiprows=10)

    stocks_df = stocks_df.dropna(axis=1, how="all").dropna(how="all")

    stock_names = stocks_df["Stock Name"].tolist()
    
    return stock_names

if __name__ == "__main__":
    read_data(r"C:\Users\aakas\Desktop\Vikas\Docs\Passport\Application\Stocks_Holdings_Statement_0018393144_2025-09-19_1758389141823.xlsx")