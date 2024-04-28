from sec_edgar_downloader import Downloader

dl = Downloader("Georgia Institute of Technology", "ywu995@gatech.edu")

def download(symbol: str):
    dl.get("10-K", symbol, download_details=True)

if __name__ == '__main__':
    # take input from command line
    symbol = input("Enter the symbol: ")
    download(symbol)