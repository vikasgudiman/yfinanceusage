from screener import Stock

def get_stock_details(symbol: str):
    # Example: symbol = "RELIANCE"
    stock = Stock(symbol)

    data = {}

    try:
        # Basic details
        data["Face Value"] = stock.face_value
        data["Sector PE"] = stock.sector_pe
        data["ROCE"] = stock.roce
        data["ROE"] = stock.roe
        data["ROA"] = stock.roa

        # Shareholding pattern
        shareholding = stock.shareholding
        data["Promoters"] = shareholding.get("Promoters", None)
        data["FIIs"] = shareholding.get("FIIs", None)
        data["DIIs"] = shareholding.get("DIIs", None)
        data["Public"] = shareholding.get("Public", None)

    except Exception as e:
        print("Error:", e)

    return data


if __name__ == "__main__":
    symbol = "RELIANCE"  # input stock symbol
    details = get_stock_details(symbol)
    print(details)
