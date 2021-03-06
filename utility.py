import os, sys, re, shutil
import json
from pathlib import Path
from datetime import *
import urllib.request
from argparse import ArgumentParser, RawTextHelpFormatter, ArgumentTypeError
from enums import *

def get_destination_dir(file_url, folder=None):
  store_directory = os.environ.get('STORE_DIRECTORY')
  if folder:
    store_directory = folder
  if not store_directory:
    store_directory = os.path.dirname(os.path.realpath(__file__))
  print("store_Directory",store_directory)
  return os.path.join(store_directory,file_url)

def get_download_url(file_url):
  return "{}{}".format(BASE_URL, file_url)

def get_all_symbols():
  response = urllib.request.urlopen("https://api.binance.com/api/v3/exchangeInfo").read()
  all_symbols = list(map(lambda symbol: symbol['symbol'], json.loads(response)['symbols']))
  USD_symbols = [symbols for symbols in all_symbols if "USD" in symbols]
  top_30_symbols = ['BTCUSDT','ETHUSDT','BCHUSDT','BUSDUSDT','USDCUSDT','POWRUSDT','BNBUSDT',
                    'LUNAUSDT','DOTUSDT','TRXUSDT','XRPUSDT','XRPUSDT','ATOMUSDT','LINKUSDT',
                    'MATICUSDT','SOLUSDT','ADAUSDT','CRVUSDT','SANDUSDT','AVAXUSDT','YFIUSDT',
                    'ELFUSDT','LTCUSDT','FTMUSDT','AAVEUSDT','NEARUSDT','DOGEUSDT','EOSUSDT',
                    'SUSHIUSDT','UNIUSDT']
  BTC_ETH_symbols = ['BTCUSDT','ETHUSDT']
  #return USD_symbols
  return BTC_ETH_symbols

def download_file(base_path,save_path, file_name, date_range=None, folder=None):
  download_path = "{}{}".format(base_path, file_name)
  
  print("download_path :",download_path)
  print("folder" ,folder)
  if folder:
    base_path = os.path.join(folder, base_path)
  if date_range:
    date_range = date_range.replace(" ","_")
    base_path = os.path.join(base_path, date_range)
  saving_path = get_destination_dir(os.path.join(save_path,file_name), folder)
  
  
  print("sving_path",saving_path)
  if os.path.exists(saving_path):
    print("\nfile already exists! {}".format(saving_path))
    return
  
  # make the directory
  if not os.path.exists(save_path):
    Path(get_destination_dir(save_path)).mkdir(parents=True, exist_ok=True)

  try:
    download_url = get_download_url(download_path)
    print(download_url)
    dl_file = urllib.request.urlopen(download_url)
    length = dl_file.getheader('content-length')
    if length:
      length = int(length)
      blocksize = max(4096,length//100)
    
    with open(saving_path, 'wb') as out_file:
      dl_progress = 0
      print("\nFile Download: {}".format(save_path))
      while True:
        buf = dl_file.read(blocksize)   
        if not buf:
          break
        dl_progress += len(buf)
        out_file.write(buf)
        done = int(50 * dl_progress / length)
        sys.stdout.write("\r[%s%s]" % ('#' * done, '.' * (50-done)) )    
        sys.stdout.flush()
    
  except urllib.error.HTTPError:
    print("\nFile not found: {}".format(download_url))
    pass
    
def convert_to_date_object(d):
  year, month, day = [int(x) for x in d.split('-')]
  print(year,month,day)
  date_obj = date(year, month, day)
  return date_obj

def get_start_end_date_objects(date_range):
  start, end = date_range.split()
  start_date = convert_to_date_object(start)
  end_date = convert_to_date_object(end)
  return start_date, end_date

def match_date_regex(arg_value, pat=re.compile(r'\d{4}-\d{2}-\d{2}')):
  if not pat.match(arg_value):
    raise ArgumentTypeError
  return arg_value

def check_directory(arg_value):
  if os.path.exists(arg_value):
    while True:
      option = input('Folder already exists! Do you want to overwrite it? y/n  ')
      if option != 'y' and option != 'n':
        print('Invalid Option!')
        continue
      elif option == 'y':
        shutil.rmtree(arg_value)
        break
      else:
        break
  return arg_value

def get_parser(parser_type):
  parser = ArgumentParser(description=("This is a script to download historical {} data").format(parser_type), formatter_class=RawTextHelpFormatter)
  parser.add_argument(
      '-s', dest='symbols', nargs='+',
      help='Single symbol or multiple symbols separated by space')
  parser.add_argument(
      '-y', dest='years', default=YEARS, nargs='+', choices=YEARS,
      help='Single year or multiple years separated by space\n-y 2019 2021 means to download {} from 2019 and 2021'.format(parser_type))
  parser.add_argument(
      '-m', dest='months', default=MONTHS,  nargs='+', type=int, choices=MONTHS,
      help='Single month or multiple months separated by space\n-m 2 12 means to download {} from feb and dec'.format(parser_type))
  parser.add_argument(
      '-d', dest='dates', nargs='+', type=match_date_regex,
      help='Date to download in [YYYY-MM-DD] format\nsingle date or multiple dates separated by space\ndownload past 35 days if no argument is parsed')
  parser.add_argument(
      '-startDate', dest='startDate', type=match_date_regex,
      help='Starting date to download in [YYYY-MM-DD] format')
  parser.add_argument(
      '-endDate', dest='endDate', type=check_directory,
      help='Ending date to download in [YYYY-MM-DD] format')
  parser.add_argument(
      '-save_path', dest='save_path', type=str,
      help='path of saving')
  parser.add_argument(
      '-folder', dest='folder', type=check_directory,
      help='Directory to store the downloaded data')
  parser.add_argument(
      '-c', dest='checksum', default=0, type=int, choices=[0,1],
      help='1 to download checksum file, default 0')

  if parser_type == 'klines':
    parser.add_argument(
      '-i', dest='intervals', default=INTERVALS, nargs='+', choices=INTERVALS,
      help='single kline interval or multiple intervals separated by space\n-i 1m 1w means to download klines interval of 1minute and 1week')


  return parser

if __name__ == "__main__":
    print(get_all_symbols())
    #download_file(base_path, file_name)

