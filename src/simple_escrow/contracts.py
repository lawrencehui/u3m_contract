from pyteal import *


def approval_program():
    seller_key = Bytes("seller")
    nft_id_key = Bytes("nft_id")
    sale_price_key = Bytes("sale_price")
    buyer_key = Bytes("buyer")

    @Subroutine(TealType.none)
    def closeNFTTo(assetID: Expr, account: Expr) -> Expr:
        asset_holding = AssetHolding.balance(
            Global.current_application_address(), assetID
        )
        return Seq(
            asset_holding,
            If(asset_holding.hasValue()).Then(
                Seq(
                    InnerTxnBuilder.Begin(),
                    InnerTxnBuilder.SetFields(
                        {
                            TxnField.type_enum: TxnType.AssetTransfer,
                            TxnField.xfer_asset: assetID,
                            TxnField.asset_close_to: account,
                        }
                    ),
                    InnerTxnBuilder.Submit(),
                )
            ),
        )

    # @Subroutine(TealType.none)
    # def repayPreviousLeadBidder(prevLeadBidder: Expr, prevLeadBidAmount: Expr) -> Expr:
    #     return Seq(
    #         InnerTxnBuilder.Begin(),
    #         InnerTxnBuilder.SetFields(
    #             {
    #                 TxnField.type_enum: TxnType.Payment,
    #                 TxnField.amount: prevLeadBidAmount - Global.min_txn_fee(),
    #                 TxnField.receiver: prevLeadBidder,
    #             }
    #         ),
    #         InnerTxnBuilder.Submit(),
    #     )

    @Subroutine(TealType.none)
    def closeAccountTo(account: Expr) -> Expr:
        return If(Balance(Global.current_application_address()) != Int(0)).Then(
            Seq(
                InnerTxnBuilder.Begin(),
                InnerTxnBuilder.SetFields(
                    {
                        TxnField.type_enum: TxnType.Payment,
                        TxnField.close_remainder_to: account,
                    }
                ),
                InnerTxnBuilder.Submit(),
            )
        )

    on_create = Seq(
        App.globalPut(seller_key, Txn.application_args[0]),
        App.globalPut(nft_id_key, Btoi(Txn.application_args[1])),
        App.globalPut(sale_price_key, Btoi(Txn.application_args[2])),
        Approve(),
    )

    on_setup = Seq(
        InnerTxnBuilder.Begin(),
        InnerTxnBuilder.SetFields(
            {
                TxnField.type_enum: TxnType.AssetTransfer,
                TxnField.xfer_asset: App.globalGet(nft_id_key),
                TxnField.asset_receiver: Global.current_application_address(),
            }
        ),
        InnerTxnBuilder.Submit(),
        Approve(),
    )
    on_buy_txn_index = Txn.group_index() - Int(1)
    on_buy_nft_holding = AssetHolding.balance(
        Global.current_application_address(), App.globalGet(nft_id_key)
    )
    on_buy = Seq(
        on_buy_nft_holding,
        Assert(
            And(
                # the listing has been set up
                on_buy_nft_holding.hasValue(),
                on_buy_nft_holding.value() > Int(0),
                Gtxn[on_buy_txn_index].type_enum() == TxnType.Payment,
                Gtxn[on_buy_txn_index].sender() == Txn.sender(),
                Gtxn[on_buy_txn_index].receiver()
                == Global.current_application_address(),
                Gtxn[on_buy_txn_index].amount() >= Global.min_txn_fee(),
            )
        ),

        If(
            Gtxn[on_buy_txn_index].amount() >= App.globalGet(sale_price_key)
        ).Then(
            Seq(
                App.globalPut(buyer_key, Gtxn[on_buy_txn_index].sender()),
                # if the auction contract account has opted into the nft, close it out
                closeNFTTo(App.globalGet(nft_id_key),
                           App.globalGet(buyer_key)),
                # if the auction contract still has funds, send them all to the seller
                closeAccountTo(App.globalGet(seller_key)),
                Approve(),
            )
        ),
        Reject(),
    )

    on_call_method = Txn.application_args[0]
    on_call = Cond(
        [on_call_method == Bytes("setup"), on_setup],
        [on_call_method == Bytes("buy"), on_buy],
    )

    on_delete_nft_holding = AssetHolding.balance(
        Global.current_application_address(), App.globalGet(nft_id_key)
    )
    on_delete = Seq(
        on_delete_nft_holding,
        Assert(
            Or(
                # sender must either be the seller or the auction creator
                Txn.sender() == App.globalGet(seller_key),
                Txn.sender() == Global.creator_address(),
            )
        ),
        # Seller decided to delist the NFT and should get the NFT back
        If(
            And(
                on_delete_nft_holding.hasValue(),
                on_delete_nft_holding.value() > Int(0),
            )
        )
        .Then(
            Seq(
                closeNFTTo(App.globalGet(nft_id_key),
                           App.globalGet(seller_key)),
                closeAccountTo(App.globalGet(seller_key)),
                Approve(),
            )
        )
        # Buyer already bought the NFT, close the app
        .Else(
            Seq(
                closeAccountTo(App.globalGet(seller_key)),
                Approve(),
            )
        ),
        Reject()

    )

    program = Cond(
        [Txn.application_id() == Int(0), on_create],
        [Txn.on_completion() == OnComplete.NoOp, on_call],
        [
            Txn.on_completion() == OnComplete.DeleteApplication,
            on_delete,
        ],
        [
            Or(
                Txn.on_completion() == OnComplete.OptIn,
                Txn.on_completion() == OnComplete.CloseOut,
                Txn.on_completion() == OnComplete.UpdateApplication,
            ),
            Reject(),
        ],
    )

    return program


def clear_state_program():
    return Approve()


if __name__ == "__main__":
    with open("exchange_approval.teal", "w") as f:
        compiled = compileTeal(
            approval_program(), mode=Mode.Application, version=5)
        f.write(compiled)

    with open("exchange_clear_state.teal", "w") as f:
        compiled = compileTeal(clear_state_program(),
                               mode=Mode.Application, version=5)
        f.write(compiled)
