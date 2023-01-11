from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction
from algosdk.logic import get_application_address
from algosdk import account, encoding
from typing import Tuple, List

from algosdk.v2client.algod import AlgodClient
from algosdk.future import transaction
from algosdk.logic import get_application_address
from algosdk import account, encoding
from pyteal import compileTeal, Mode

from .contracts import approval_program, clear_state_program
from ..common.account import Account
from ..common.resources import waitForTransaction
from ..common.util import fullyCompileContract, getAppGlobalState

APPROVAL_PROGRAM = b""
CLEAR_STATE_PROGRAM = b""


def getContracts(client: AlgodClient) -> Tuple[bytes, bytes]:
    """Get the compiled TEAL contracts for the auction.

    Args:
                    client: An algod client that has the ability to compile TEAL programs.

    Returns:
                    A tuple of 2 byte strings. The first is the approval program, and the
                    second is the clear state program.
    """
    global APPROVAL_PROGRAM
    global CLEAR_STATE_PROGRAM

    if len(APPROVAL_PROGRAM) == 0:
        APPROVAL_PROGRAM = fullyCompileContract(client, approval_program())
        CLEAR_STATE_PROGRAM = fullyCompileContract(
            client, clear_state_program())

    return APPROVAL_PROGRAM, CLEAR_STATE_PROGRAM


def createEscrowApp(
    client: AlgodClient,
    seller: str,
    nftID: int,
    price: int
) -> int:

    approval, clear = getContracts(client)

    globalSchema = transaction.StateSchema(num_uints=2, num_byte_slices=2)
    localSchema = transaction.StateSchema(num_uints=0, num_byte_slices=0)

    app_args = [
        encoding.decode_address(seller.getAddress()),
        nftID.to_bytes(8, "big"),
        price.to_bytes(8, "big")
    ]

    txn = transaction.ApplicationCreateTxn(
        sender=seller.getAddress(),
        on_complete=transaction.OnComplete.NoOpOC,
        approval_program=approval,
        clear_program=clear,
        global_schema=globalSchema,
        local_schema=localSchema,
        app_args=app_args,
        sp=client.suggested_params(),
    )
    signedTxn = txn.sign(seller.getPrivateKey())
    client.send_transaction(signedTxn)

    response = waitForTransaction(client, signedTxn.get_txid())
    assert response.applicationIndex is not None and response.applicationIndex > 0

    return response.applicationIndex


def setupEscrowApp(
    client: AlgodClient,
    appID: int,
    funder: Account,
    nftHolder: Account,
    nftID: int,
    nftAmount: int,
) -> None:

    appAddr = get_application_address(appID)

    suggestedParams = client.suggested_params()
    fundingAmount = (
        # min account balance
        100_000
        # additional min balance to opt into NFT
        + 100_000
        # 3 * min txn fee
        + 3 * 1_000
    )

    fundAppTxn = transaction.PaymentTxn(
        sender=funder.getAddress(),
        receiver=appAddr,
        amt=fundingAmount,
        sp=suggestedParams,
    )

    setupTxn = transaction.ApplicationCallTxn(
        sender=funder.getAddress(),
        index=appID,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"setup"],
        foreign_assets=[nftID],
        sp=suggestedParams,
    )

    fundNftTxn = transaction.AssetTransferTxn(
        sender=nftHolder.getAddress(),
        receiver=appAddr,
        index=nftID,
        amt=nftAmount,
        sp=suggestedParams,
    )

    transaction.assign_group_id([fundAppTxn, setupTxn, fundNftTxn])

    signedFundAppTxn = fundAppTxn.sign(funder.getPrivateKey())
    signedSetupTxn = setupTxn.sign(funder.getPrivateKey())
    signedFundNftTxn = fundNftTxn.sign(nftHolder.getPrivateKey())

    client.send_transactions(
        [signedFundAppTxn, signedSetupTxn, signedFundNftTxn])

    waitForTransaction(client, signedFundAppTxn.get_txid())


def buyNft(
    client: AlgodClient,
    appID: int,
    buyer: Account,
    seller: Account,
    price: int
) -> None:

    appAddr = get_application_address(appID)
    appGlobalState = getAppGlobalState(client, appID)
    nftID = appGlobalState[b"nft_id"]

    suggestedParams = client.suggested_params()

    payTxn = transaction.PaymentTxn(
        sender=buyer.getAddress(),
        receiver=appAddr,
        amt=price,
        sp=suggestedParams,
    )

    appCallTxn = transaction.ApplicationCallTxn(
        sender=buyer.getAddress(),
        index=appID,
        on_complete=transaction.OnComplete.NoOpOC,
        app_args=[b"buy"],
        foreign_assets=[nftID],
        accounts=[seller.getAddress()],
        sp=suggestedParams,
    )

    transaction.assign_group_id([payTxn, appCallTxn])

    signedPayTxn = payTxn.sign(buyer.getPrivateKey())
    signedAppCallTxn = appCallTxn.sign(buyer.getPrivateKey())

    client.send_transactions([signedPayTxn, signedAppCallTxn])

    waitForTransaction(client, appCallTxn.get_txid())


def closeApp(client: AlgodClient, appID: int, closer: Account):
    appGlobalState = getAppGlobalState(client, appID)

    nftID = appGlobalState[b"nft_id"]
    print(f"nftID: {nftID}")

    accounts: List[str] = [
        encoding.encode_address(appGlobalState[b"seller"]),
        encoding.encode_address(appGlobalState[b"buyer"])
    ]

    deleteTxn = transaction.ApplicationDeleteTxn(
        sender=closer.getAddress(),
        index=appID,
        accounts=accounts,
        foreign_assets=[nftID],
        sp=client.suggested_params(),
    )

    signedDeleteTxn = deleteTxn.sign(closer.getPrivateKey())

    client.send_transaction(signedDeleteTxn)

    waitForTransaction(client, signedDeleteTxn.get_txid())
