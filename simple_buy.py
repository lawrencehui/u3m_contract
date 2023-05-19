from time import time, sleep
from algosdk import account, encoding, mnemonic
from algosdk.logic import get_application_address

from src.simple_escrow.operations import createEscrowApp, setupEscrowApp, buyNft, closeApp, getContracts
from src.common.setup import getAlgodClient
from src.common.resources import getTemporaryAccount, optInToAsset, createDummyAsset
from src.common.util import getBalances, getLastBlockTimestamp
from src.common.account import Account

import base64


def main_simple_buy():
    client = getAlgodClient()

    print("Generating temporary accounts...")
    creator = getTemporaryAccount(client)
    seller = getTemporaryAccount(client)
    buyer = getTemporaryAccount(client)

    # seller_mnemonic = "good always among hover measure common meadow strategy where cash element glow bean obey change harsh street uncle business short vapor void cross able genre"
    # seller = Account(mnemonic.to_private_key(seller_mnemonic))

    # buyer_mnemonic = "yard lucky liberty music output connect program swallow logic warfare school report grid logic great poem lion fiscal broccoli join blood aspect price above width"
    # buyer = Account(mnemonic.to_private_key(buyer_mnemonic))

    print("Admin (auction creator account):", creator.getAddress())
    print("Admin menmonic: ", creator.getMnemonic())
    print("Seller (seller account):", seller.getAddress())
    print("Seller menmonic: ", seller.getMnemonic())
    print("Buyer (buyer account)", buyer.getAddress())
    print("Buyer menmonic: ", buyer.getMnemonic(), "\n")

    nftAmount = 1
    nftID = createDummyAsset(client, nftAmount, seller)

    print("The NFT ID is", nftID)
    print("Seller's balances:", getBalances(client, seller.getAddress()), "\n")

    print("Seller is listing the NFT for sale...")
    sale_price = 1_200_000

    appID = createEscrowApp(
        client=client,
        seller=seller,
        nftID=nftID,
        price=sale_price
    )

    print(
        "Done. The escrow app ID is",
        appID,
        "and the escrow contract address is",
        get_application_address(appID),
        "\n",
    )

    # nftID = 846
    # appID = 847

    print("Seller is setting up and funding NFT auction...")
    setupEscrowApp(
        client=client,
        appID=appID,
        funder=seller,
        nftHolder=seller,
        nftID=nftID,
        nftAmount=1,
    )
    print("Done\n")

    print("Balance Summary:\n")
    actualAppBalancesBefore = getBalances(
        client, get_application_address(appID))
    print("Auction escrow balances:", actualAppBalancesBefore, "\n")

    print("Buyer is opting into NFT with ID", nftID)
    optInToAsset(client, nftID, buyer)

    buyerBalancesBefore = getBalances(client, buyer.getAddress())
    print("Buyer wants to buy the NFT, his balances before buying:",
          buyerBalancesBefore)

    # [audit fix] 4.1 Improper Buyer Balance Validations
    if(buyerBalancesBefore.get(0) > sale_price):
        buyNft(client=client, appID=appID, buyer=buyer, seller=seller, price=sale_price)
    
    else: 
        raise Exception("buyer balance lower than sale price")

    print("Done Opt in and buying\n")

    actualAppBalances = getBalances(client, get_application_address(appID))
    print("The escrow account now holds the following:", actualAppBalances)

    actualSellerBalances = getBalances(client, seller.getAddress())
    print("Seller's balances after txn: ", actualSellerBalances, " Algos")

    actualBuyerBalances = getBalances(client, buyer.getAddress())
    print("Buyer's balances after txn: ", actualBuyerBalances, " Algos")

    # [audit fix] 4.2 Balance Verification before Closing the App
    if(actualAppBalances.get(0) == 0 and actualSellerBalances.get(nftID) == 0 and actualBuyerBalances.get(nftID) == 1):
        print("Account balance verification success. Seller is closing out the app\n")
        closeApp(client, appID, seller)
    else: 
        raise Exception("account balance verifications failed ")
    
    print("Done closing")


main_simple_buy()


def simple_buy_test():
    client = getAlgodClient()
    approval, clear = getContracts(client)

    approval_file = open("./output/approval_simple_escrow.txt", "w")
    n = approval_file.write(approval)
    approval_file.close()

    clear_file = open("./output/clear_simple_escrow.txt", "w")
    n = clear_file.write(clear)
    clear_file.close()


# simple_buy_test()
