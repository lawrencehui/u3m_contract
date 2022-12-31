from time import time, sleep
from algosdk import account, encoding, mnemonic
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

from auction.account import Account
from pyteal import *


def manualTestScript():
    client = getAlgodClient()

    print("Generating accounts from mnemonic...")

    # generate new Buyer
    # buyer = getTemporaryAccount(client)
    # print("Buyer (buyer account)", buyer.getAddress())
    # print("Buyer menmonic: ", buyer.getMnemonic(), "\n")

    creator_mnemonic = "market slender zone eternal identify gossip album find spin vital cotton provide apart hazard finger wash absurd enemy inform panda barely potato lens absent hour"
    creator = Account(mnemonic.to_private_key(creator_mnemonic))

    seller_mnemonic = "vivid express idea horn artwork transfer unfair shoulder hip over blast head turkey eagle siren shift sustain naive elder blast fatal plug dry above join"
    seller = Account(mnemonic.to_private_key(seller_mnemonic))

    # buyer_mnemonic = "moon fun aunt reopen april asset squeeze doctor arena island host soul canyon donate talk grit few pair gadget main fine brave song abstract badge"
    buyer_mnemonic = "edit drip spray perfect canvas spare fortune cereal surprise venture rebel riot mistake autumn usual kidney blanket ski balcony debate essay possible observe able wide"
    buyer = Account(mnemonic.to_private_key(buyer_mnemonic))

    actualAppBalancesBefore = getBalances(client, get_application_address(553))
    print("Auction escrow balances:", actualAppBalancesBefore, "\n")

    # # closeAuction(client, 175, seller)

    nftID = 508

    # startTime = int(time()) + 2 * 60  # start time is 10 seconds in the future
    # endTime = startTime + 120 * 60  # end time is 30 seconds after start
    # reserve = 1_000_000  # 1 Algo
    # increment = 100_000  # 0.1 Algo
    # print("Admin is creating an auction that lasts 30 seconds to auction off the NFT...")
    # appID = createAuctionApp(
    #     client=client,
    #     sender=creator,
    #     seller=seller.getAddress(),
    #     nftID=nftID,
    #     startTime=startTime,
    #     endTime=endTime,
    #     reserve=reserve,
    #     minBidIncrement=increment,
    # )

    # print(f'start time: {startTime}')
    # print(f'end time: {endTime}')

    # print(
    #     "Done. The auction app ID is",
    #     appID,
    #     "and the escrow account is",
    #     get_application_address(appID),
    #     "\n",
    # )

    # print("Seller is setting up and funding NFT auction...")
    # setupAuctionApp(
    #     client=client,
    #     appID=541,
    #     funder=creator,
    #     nftHolder=seller,
    #     nftID=nftID,
    #     nftAmount=1,
    # )
    # print("Done\n")

    # placeBid(client, 495, buyer, 1500000)

    actualBuyerBalances = getBalances(client, buyer.getAddress())
    print("Buyer's balances after auction: ", actualBuyerBalances, " Algos")


manualTestScript()
