import requests
import sys
import itertools
from bitcoinlib.wallets import Wallet, wallet_delete_if_exists
from bitcoinlib.mnemonic import Mnemonic

"""
Code block to be changed by the user:
Default values are specific for a legacy wallet created from a 24-word mnemonic, with the last one missing.
"""
number_of_missing_words = 1     
    # 1-24. How many words you can't remember

position_of_missing_words = 24  
    # 1-24. Position of the first unknown word. 1 means you don't remember the first one, 24 the last, and so on)

wallet_witness_type = 'legacy'  
    # Changeable in 'segwit' for native segregated witness wallet, or 'p2sh-segwit' for legacy compatible wallets

known_first = "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon"
    # first known part of the seed. Leave "" if the words you don't remember are the first ones

known_second = ""
    # first known part of the seed. Leave "" if the words you don't remember are the last ones

gap_limit = 10
    #1-50: number of address to scan. default is 10

"""
End of user-defined parameters block.
From here onwards is the validation and execution section of the script.
DON'T CHANGE THE FOLLOWING CODE (Unless you know what you are doing - and you want to help me improve this script xD -)
"""

# BIP39 list of 2048 words
try:
    english_bip39_file = open("english.txt")
except:
    print("something went wrong opening the file")
    sys.exit()
else:
    BIP39_word_list = english_bip39_file.read().split("\n")
finally:
    english_bip39_file.close()

# First part: checking if params are OK
if type(number_of_missing_words) != type(1):
    print("use an int type for number_of_missing_words")
    sys.exit()

if number_of_missing_words >24 or number_of_missing_words <1:
    print("number_of_missing_words must be a number between 1 and 24")
    sys.exit()

if type(position_of_missing_words) != type(1):
    print("use an int type for position_of_missing_words")
    sys.exit()

if position_of_missing_words >24 or position_of_missing_words <1:
    print("position_of_missing_words must be a number between 1 and 24")
    sys.exit()

if position_of_missing_words > 25-number_of_missing_words:
    print("Please be consistent with the values you set. number_of_missing_words can't be greater of free positions in the seedphrase")
    sys.exit()

if type(known_first) != type(known_second) != type("sample"):
    print("use string type for both first_known and second_known")
    sys.exit()

if len(known_first.split()) + number_of_missing_words + len(known_second.split()) != 24:
    print("Number of words inconsistent")
    sys.exit()

for aux in known_first.split():
    if aux not in BIP39_word_list:
        print("known part of your mnemonic contains non-standard words")
        sys.exit()

for aux in known_second.split():
    if aux not in BIP39_word_list:
        print("known part of your mnemonic contains non-standard words")
        sys.exit()

if wallet_witness_type != 'segwit' and wallet_witness_type != 'legacy' and wallet_witness_type != 'p2sh-segwit':
    print("invalid witness type")
    sys.exit()

if type(gap_limit) != type(10):
    print("use an int type for gap_limit")
    sys.exit()
    
if gap_limit<1 and gap_limit >50:
    print("gap_limit must be a number between 1 and 50")
    sys.exit()

# Second part: searching  

def convertTuple(tup):
    st = ' '.join(map(str, tup))
    return st

if number_of_missing_words >= 1:
    print("looks like you lost at least 2 words. That's a lot of entropy, it will take a while")

something_found = False

for missing_words_tuple in itertools.product(BIP39_word_list, repeat=number_of_missing_words):
    
    wallet_delete_if_exists("Wallet", db_uri=None, force=False, db_password=None)
    
    phrase = known_first+" "+convertTuple(missing_words_tuple)+" "+known_second

    try:
        w = Wallet.create("Wallet", witness_type=wallet_witness_type, keys=phrase, network='bitcoin')
    except ValueError: # normally: invalid checksum, skip iteration
        continue
    except Warning:
        continue
    
    print("\nscanning possible wallet: \n", phrase)
    
    try:
        w.scan()
        if w.balance() == 0 :
            print("balance not found")
            print("proceed search for txs ...")
        else:
            print("EUREKA!")
            print("\tbalance:\n\t\t", w.balance)
            store_valid_wallet = open("Valid_mnemonics", "a")
            store_valid_wallet.write("\nWallet with Balance:\n")
            store_valid_wallet.write(phrase+"\n")
            something_found = True
            continue
    except:
        print("cannot scan the entire wallet")
        print("proceed scanning first ", gap_limit," addresses")
    
    walletKeys = w.get_keys(number_of_keys=gap_limit)
    i = 0
    for key in walletKeys:
        i = i+1
        address = key.address
        result = requests.get(f"https://blockstream.info/api/address/{address}")
        api_response = result.json()
        if api_response["chain_stats"]["tx_count"]>0:
            print("address number", i,"contains transactions")
            print("saving seedphrase in Mnemonic_with_txs file")
            store_valid_wallet = open("Mnemonic_with_txs", "a")
            store_valid_wallet.write(phrase+"\n")
            store_valid_wallet.close()
            something_found = True
        if api_response["chain_stats"]["funded_txo_sum"]>0:
            print("Balace Found!")
            print("balance of address",i,":\n\t", api_response["chain_stats"]["funded_txo_sum"])
            print("saving phrase in Valid_mnemonics file")
            store_valid_wallet = open("Valid_mnemonics", "a")
            store_valid_wallet.write("\nWallet with Balance:\n")
            store_valid_wallet.write(phrase+"\n")
            store_valid_wallet.close()
            something_found = True
        else:
            print("nothin found on the address",i)

if something_found == False:
    print("Sadly, nothing has been found")