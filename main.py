import time
import requests

HELIUS_API_KEY = "1a523e98-b65d-463f-b1b0-ace4c0b2a448"
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1385624443975499787/MVHkl-u88YdPyzIARwNh6oZ5SxSbvoivv_BbPgLXUnsvCax1rv70NbIicuoAHuB29A_x"
BINANCE_ADDRESSES = ["5tzFkiKscXHK5ZXCGbXZxdw7gTjjD1mBwuoFbhUvuAi9"]

def send_discord_alert(message):
    data = {"content": message}
    requests.post(DISCORD_WEBHOOK_URL, json=data)

def is_wallet_fresh(address):
    url = f"https://api.helius.xyz/v0/addresses/{address}/transactions?api-key={HELIUS_API_KEY}&limit=1"
    resp = requests.get(url)
    txs = resp.json()
    return len(txs) == 1

def monitor():
    fresh_wallets = set()
    while True:
        for binance in BINANCE_ADDRESSES:
            url = f"https://api.helius.xyz/v0/addresses/{binance}/transactions?api-key={HELIUS_API_KEY}&limit=10"
            resp = requests.get(url)
            txs = resp.json()
            for tx in txs:
                if (
                    tx.get("type") == "TRANSFER"
                    and tx.get("amount", 0) == 9.999
                    and is_wallet_fresh(tx["to"])
                ):
                    fresh_wallets.add(tx["to"])
                    send_discord_alert(
                        f"🚨 9.999 SOL envoyés à un wallet vierge !\nFrom: {binance}\nTo: {tx['to']}\nLien: https://solscan.io/tx/{tx['signature']}"
                    )
        for wallet in list(fresh_wallets):
            url = f"https://api.helius.xyz/v0/addresses/{wallet}/transactions?api-key={HELIUS_API_KEY}&limit=2"
            resp = requests.get(url)
            txs = resp.json()
            if len(txs) > 1:
                send_discord_alert(
                    f"🕵️ Activité détectée sur wallet fraîche\nWallet: {wallet}\nLien: https://solscan.io/account/{wallet}"
                )
                fresh_wallets.remove(wallet)
        time.sleep(5)

if __name__ == "__main__":
    monitor()