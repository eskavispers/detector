import requests
from datetime import datetime, timedelta
import statistics

ETHERSCAN_API = "https://api.etherscan.io/api"

class GhostFeeDetector:
    def __init__(self, api_key, address):
        self.api_key = api_key
        self.address = address.lower()
    
    def get_transactions(self, limit=50):
        params = {
            "module": "account",
            "action": "txlist",
            "address": self.address,
            "startblock": 0,
            "endblock": 99999999,
            "sort": "desc",
            "apikey": self.api_key
        }
        response = requests.get(ETHERSCAN_API, params=params)
        data = response.json()
        return data["result"][:limit]

    def analyze_fees(self):
        txs = self.get_transactions()
        ghost_fees = []
        for tx in txs:
            if tx["isError"] != "0":
                continue
            try:
                gas_used = int(tx["gasUsed"])
                gas_price = int(tx["gasPrice"])
                fee_eth = (gas_used * gas_price) / 1e18

                timestamp = datetime.fromtimestamp(int(tx["timeStamp"]))
                avg_gas_price = self.estimate_avg_gas_price(timestamp)
                ideal_fee_eth = (gas_used * avg_gas_price) / 1e18

                overpaid = fee_eth - ideal_fee_eth
                if overpaid > 0.0005:  # Threshold
                    ghost_fees.append({
                        "hash": tx["hash"],
                        "fee_eth": round(fee_eth, 6),
                        "ideal_fee_eth": round(ideal_fee_eth, 6),
                        "overpaid": round(overpaid, 6),
                        "timestamp": timestamp.isoformat()
                    })
            except Exception as e:
                continue
        return ghost_fees

    def estimate_avg_gas_price(self, timestamp):
        # Simulate average gas price in Gwei based on time (mock)
        # In real-world, you would integrate with a service like EthGasStation or use historical node data
        avg_prices = [20, 25, 30, 18, 22, 28]
        return int(statistics.mean(avg_prices)) * 10**9
