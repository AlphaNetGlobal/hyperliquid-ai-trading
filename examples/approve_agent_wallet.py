"""Approve a trade-only agent wallet on Hyperliquid and confirm it is registered.

An agent wallet (Hyperliquid also calls it an API wallet) is a separate key that
can sign orders and cancels for your account. It cannot withdraw or transfer
funds: those actions need a signature from your main wallet. This is how
AlphaNet trades for its users while funds stay in each user's own Hyperliquid
account.

This script:
  1. approves a new named agent wallet for your account,
  2. prints the new agent's address (and its private key, which you would hand
     to the software that trades for you),
  3. lists the account's approved named agents, with expiry dates, to confirm it.

It never places an order.

Usage:
    cp .env.example .env        # fill in HL_ACCOUNT_PRIVATE_KEY
    python examples/approve_agent_wallet.py --name my-bot

Runs on testnet unless HL_NETWORK=mainnet. Based on the official SDK example
hyperliquid-python-sdk/examples/basic_agent.py.
"""

import argparse
import os
from datetime import datetime, timezone

import eth_account
from dotenv import load_dotenv
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info
from hyperliquid.utils import constants


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--name", required=True, help="agent name, e.g. my-bot")
    args = parser.parse_args()

    load_dotenv()
    key = os.environ.get("HL_ACCOUNT_PRIVATE_KEY")
    if not key:
        raise SystemExit("Set HL_ACCOUNT_PRIVATE_KEY in .env (see .env.example).")
    mainnet = os.environ.get("HL_NETWORK", "").lower() == "mainnet"
    base_url = constants.MAINNET_API_URL if mainnet else constants.TESTNET_API_URL

    wallet = eth_account.Account.from_key(key)
    exchange = Exchange(wallet, base_url)
    info = Info(base_url, skip_ws=True)

    # Approvals must be signed by the main wallet. An agent cannot approve
    # another agent, and an agent can never withdraw or transfer funds.
    # Approving a new agent under a name that is already in use replaces the
    # old agent with that name; the old key stops working. Approving a new
    # unnamed agent replaces the previous unnamed one.
    result, agent_key = exchange.approve_agent(args.name)
    if result.get("status") != "ok":
        raise SystemExit(f"Approval failed: {result}")

    agent = eth_account.Account.from_key(agent_key)
    print(f"Network:        {'mainnet' if mainnet else 'testnet'}")
    print(f"Account:        {wallet.address}")
    print(f"Agent name:     {args.name}")
    print(f"Agent address:  {agent.address}")
    print(f"Agent key:      {agent_key}")
    print("Store the agent key securely. It can trade for this account but cannot withdraw.\n")

    # Named agents expire. Hyperliquid prunes an agent once it expires, once it
    # is replaced, or once the account that approved it has no funds. Do not
    # reuse an old agent address after it has been pruned.
    print("Approved named agents on this account:")
    for a in info.extra_agents(wallet.address):
        until = datetime.fromtimestamp(a["validUntil"] / 1000, tz=timezone.utc)
        mark = "  <- new" if a["address"].lower() == agent.address.lower() else ""
        print(f"  {a['name']:<20} {a['address']}  valid until {until:%Y-%m-%d}{mark}")


if __name__ == "__main__":
    main()
