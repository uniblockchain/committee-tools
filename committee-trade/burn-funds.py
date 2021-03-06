from grapheneapi.grapheneclient import GrapheneClient
from pprint import pprint
import config
from datetime import datetime
import time


def formatTimeFromNow(secs=0):
    return datetime.utcfromtimestamp(time.time() + int(secs)).strftime(
        "%Y-%m-%dT%H:%M:%S"
    )


if __name__ == "__main__":
    client = GrapheneClient(config)
    core_asset = client.getObject("1.3.0")
    account = client.rpc.get_account(config.account)
    proposer = client.rpc.get_account(config.proposer)

    ops = []

    for asset_name in config.burn_assets:
        asset = client.rpc.get_asset(asset_name)
        amount = config.burn_assets[asset_name]

        op = client.rpc.get_prototype_operation("asset_reserve_operation")
        op[1]["payer"] = account["id"]
        op[1]["amount_to_reserve"]["asset_id"] = asset["id"]
        op[1]["amount_to_reserve"]["amount"] = int(amount * 10 ** asset["precision"])
        ops.append(op)

    buildHandle = client.rpc.begin_builder_transaction()
    for op in ops:
        client.rpc.add_operation_to_builder_transaction(buildHandle, op)
    client.rpc.set_fees_on_builder_transaction(buildHandle, "1.3.0")
    client.rpc.propose_builder_transaction2(
        buildHandle, proposer["name"], formatTimeFromNow(60 * 60 * 24), 0, False
    )
    client.rpc.set_fees_on_builder_transaction(buildHandle, "1.3.0")
    tx = client.rpc.sign_builder_transaction(buildHandle, False)
    pprint(tx)
