# U3M Auction Smart Contract (based on Algorand Auction Demo)

This repo contains a basic setup of smart contracts to list, place bid and exchange NFTs through on-chain NFT auction using the Algorand blockchain.

## Usage

The file `auction/operations.py` provides a set of functions and interface that uses the AlgoSDK to create and interact with auctions.

The main contract file `auction/contracts.py` is a PyTeal contract that can be run to compile to the `*.teal` files (i.e. `auction_approval.teal` and `auction_clear_state.teal`)

## Development Setup

Set up venv (one time):

- `python3 -m venv venv`

Active venv:

- `. venv/bin/activate` (if your shell is bash/zsh)
- `. venv/bin/activate.fish` (if your shell is fish)

Install dependencies:

- `pip install -r requirements.txt`

Run tests:

- First, start an instance of [sandbox](https://github.com/algorand/sandbox) (requires Docker): `./sandbox up nightly`
- `pytest`
- When finished, the sandbox can be stopped with `./sandbox down`

To run the auction walk-through:

- `python3 main.py`
