from time import time, sleep
from algosdk import account, encoding, mnemonic
from algosdk.logic import get_application_address
# from auction.operations import createAuctionApp, setupAuctionApp, placeBid, closeAuction
# from common.util import (
#     getBalances,
#     getAppGlobalState,
#     getLastBlockTimestamp,
# )
# from auction.testing.setup import getAlgodClient
# from auction.testing.resources import (
#     getTemporaryAccount,
#     optInToAsset,
#     createDummyAsset,
# )
from src.auction.operations import createAuctionApp, setupAuctionApp, placeBid, closeAuction
from src.common.setup import getAlgodClient
from src.common.resources import getTemporaryAccount, optInToAsset, createDummyAsset
from src.common.util import getBalances, getLastBlockTimestamp


def main_u3m():
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

    nftAmount = 1
    nftID = createDummyAsset(client, nftAmount, seller)

    print("The NFT ID is", nftID)
    print("Seller's balances:", getBalances(client, seller.getAddress()), "\n")

    startTime = int(time()) + 10  # start time is 10 seconds in the future
    endTime = startTime + 5 * 60  # end time is 5 * 60 seconds after start
    reserve = 1_000_000  # 1 Algo
    increment = 100_000  # 0.1 Algo
    print("Admin is creating an auction that lasts 30 seconds to auction off the NFT...")
    appID = createAuctionApp(
        client=client,
        sender=creator,
        seller=seller.getAddress(),
        nftID=nftID,
        startTime=startTime,
        endTime=endTime,
        reserve=reserve,
        minBidIncrement=increment,
    )

    print(
        "Done. The auction app ID is",
        appID,
        "and the escrow account is",
        get_application_address(appID),
        "\n",
    )

    print("Seller is setting up and funding NFT auction...")
    setupAuctionApp(
        client=client,
        appID=appID,
        funder=creator,
        nftHolder=seller,
        nftID=nftID,
        nftAmount=nftAmount,
    )
    print("Done\n")

    print("Balance Summary:\n")

    sellerBalancesBefore = getBalances(client, seller.getAddress())
    sellerAlgosBefore = sellerBalancesBefore[0]
    print("Seller's balances before:", sellerBalancesBefore)

    _, lastRoundTime = getLastBlockTimestamp(client)

    print("lastRoundtime is: ", lastRoundTime)
    print("start time is ", startTime)
    print("end time is ", endTime)
    print("startTime - lastRoundTime = ", startTime - lastRoundTime)

    if lastRoundTime < startTime + 5:
        sleep(startTime + 5 - lastRoundTime)

    actualAppBalancesBefore = getBalances(
        client, get_application_address(appID))
    print("Auction escrow balances:", actualAppBalancesBefore, "\n")

    bidAmount = reserve
    buyerBalancesBefore = getBalances(client, buyer.getAddress())
    buyerAlgosBefore = buyerBalancesBefore[0]
    print("Buyer wants to bid on NFT, her balances before bid:", buyerBalancesBefore)
    print("Buyer is placing bid for", bidAmount, "microAlgos")

    placeBid(client=client, appID=appID, bidder=buyer, bidAmount=bidAmount)

    print("Buyer is opting into NFT with ID", nftID)
    optInToAsset(client, nftID, buyer)

    print("Done Bidding and Opt in\n")

    _, lastRoundTime = getLastBlockTimestamp(client)
    if lastRoundTime < endTime + 5:
        waitTime = endTime + 5 - lastRoundTime
        print("Waiting {} seconds for the auction to finish\n".format(waitTime))
        sleep(waitTime)

    print("Seller is closing out the auction\n")
    closeAuction(client, appID, seller)

    actualAppBalances = getBalances(client, get_application_address(appID))
    print("The auction escrow now holds the following:", actualAppBalances)

    # buyerNftBalance = getBalances(client, buyer.getAddress())[nftID]
    # print("The buyerNftBalance: (should be 1)", buyerNftBalance)

    sellerNftBalance = getBalances(client, seller.getAddress())[nftID]
    print("The sellerNftBalance: (should be 1)", sellerNftBalance)

    actualSellerBalances = getBalances(client, seller.getAddress())
    print("Seller's balances after auction: ", actualSellerBalances, " Algos")

    actualBuyerBalances = getBalances(client, buyer.getAddress())
    print("Buyer's balances after auction: ", actualBuyerBalances, " Algos")


main_u3m()
