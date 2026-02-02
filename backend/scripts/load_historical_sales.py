#ETL script to load the data in postgres database
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pandas as pd
from sqlalchemy.orm import Session 
from database import Session_local
from models import HistoricalSales



def load_data():
    print("Starting historical sales load.....")
    df = pd.read_csv('cleaned_sales.csv')
    df["sale_date"] = pd.to_datetime(df["sale_date"]).dt.date

    db: Session = Session_local()

    if db.query(HistoricalSales).first():
        print("historical_sales already contains data. Skipping load.")
        return

    try:
        for row in df.itertuples(index=False):
            record = HistoricalSales(
                domain = row.domain,
                quantity = int(row.quantity),
                sale_date = row.sale_date)
            
            db.add(record)
        
        db.commit()
        print("Historical data loaded successfully")

    except Exception as e:
        db.rollback()
        print("Error: ", e)

    
    finally:
        db.close()
    
if __name__ == "__main__":
    load_data()