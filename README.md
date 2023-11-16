# Bitcoin Wallet Recovery Tool with BIP39 Mnemonic Support

**IMPORTANT: script never tested, it will be done in some days (hopefully)**

This Python script is designed to help users recover their BIP39 24-words Bitcoin wallet in case some of the mnemonic words are lost.

## Introduction

If you've lost some of your BIP39 mnemonic words, this tool can assist you in recovering your Bitcoin wallet. 
Keep in mind that the script is not optimized for multiple missing words, so the recovery process may take a significant amount of time.

#### note

Missing words must be contiguous

## Configuration

You can customize the recovery process by setting the following parameters:

- **Number of Missing Words:** Specify the number of missing words in your mnemonic. Note that the script is less optimized for multiple missing words.

- **Position of the First Missing Word:** Multiple missing words must be contiguous. Positions start from 1 (not 0)

- **Witness Type:** Choose the witness type for the wallet (`segwit`, `legacy`, or `p2sh-segwit`).

- **Gap Limit:** Set the gap limit, which determines the number of addresses to scan.

**Important:** Do not change or delete the "english.txt" file as it contains the BIP39 words list required for the recovery process.

## Usage

To use the script, run the following command:

```bash
python3 ./script.py
```
The script will systematically check every possible combination of seed phrases until it discovers funds or transactions. 
If successful, the mnemonic will be displayed on the screen and saved in a file within the same directory as the script.

## Dependencies

Make sure to have `bitcoinlib` and `requests` installed before trying to run the script.
You can install them using `pip`:
```bash
pip install bitcoinlib
pip install requests
```
Make sure to navigate to the directory containing the script before executing the command.
