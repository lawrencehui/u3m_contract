from time import time, sleep

from algosdk import account, encoding
from algosdk.logic import get_application_address
from auction.operations import createAuctionApp, setupAuctionApp, placeBid, closeAuction
from auction.util import (
    getBalances,
    getAppGlobalState,
    getLastBlockTimestamp,
)
from auction.testing.setup import getAlgodClient
from auction.testing.resources import (
    getTemporaryAccount,
    optInToAsset,
    createDummyAsset,
)


def genAccounts():
    client = getAlgodClient()

    print("Generating temporary accounts...")
    creator = getTemporaryAccount(client)
    seller = getTemporaryAccount(client)
    buyer = getTemporaryAccount(client)

    print("Admin (auction creator account):", creator.getAddress())
    print("Admin menmonic: ", creator.getMnemonic())
    print("Seller (seller account):", seller.getAddress())
    print("Seller menmonic: ", seller.getMnemonic())
    print("Buyer (buyer account)", buyer.getAddress())
    print("Buyer menmonic: ", buyer.getMnemonic(), "\n")


genAccounts()
