from sec_edgar_downloader import Downloader
import logging

dl = Downloader("Georgia Institute of Technology", "ywu995@gatech.edu")

def download(symbol: str):
    dl.get("10-K", symbol, download_details=True)
    logging.info(f"Successfully downloaded 10-K filings for {symbol}")

if __name__ == '__main__':
    # take input from command line
    symbol = input("Enter the symbol: ")
    download(symbol)