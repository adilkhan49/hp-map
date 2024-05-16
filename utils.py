import gspread
import pandas as pd

def get_data(CREDENTIALS,SPREADSHEET_ID,WORKSHEET_NAME,TGT_CSV_FILENAME):
    gc = gspread.service_account(filename=CREDENTIALS)
    sh = gc.open_by_key(SPREADSHEET_ID)
    ws = sh.worksheet(WORKSHEET_NAME)
    df = pd.DataFrame(ws.get_all_records())
    df.to_csv(TGT_CSV_FILENAME,index=False)
    print(f'{len(df)} records saved to {TGT_CSV_FILENAME}')
    return df

if __name__ == '__main__':
    CREDENTIALS = 'credentials.json'
    SPREADSHEET_ID="1XVVdtHa9h10QZ1hoQ2gh5HGywcgT7X61UhgiI9-6JrY"
    WORKSHEET_NAME = 'Pops'
    TGT_CSV_FILENAME = 'Pop Sheet - Pops.csv'
    get_data(SPREADSHEET_ID,WORKSHEET_NAME,TGT_CSV_FILENAME)