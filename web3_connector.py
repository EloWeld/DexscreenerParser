import json
from web3 import Web3
from web3.contract.contract import Contract
from web3.middleware import construct_sign_and_send_raw_middleware
from web3.middleware import geth_poa_middleware
from web3.middleware.cache import construct_simple_cache_middleware

# Setup
alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/lK2v_qBdtAzE5BFKZrquknGMWfD7bwbP"
web3 = Web3(Web3.HTTPProvider(alchemy_url))


class TokenWeb3Stats:
    def __init__(self):
        self.erc20_abi = [
            {
                "anonymous": False,
                "inputs": [
                    {"indexed": True, "internalType": "address", "name": "from", "type": "address"},
                    {"indexed": True, "internalType": "address", "name": "to", "type": "address"},
                    {"indexed": False, "internalType": "uint256", "name": "value", "type": "uint256"}
                ],
                "name": "Transfer",
                "type": "event"
            },
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "totalSupply",
                "outputs": [{"name": "", "type": "uint256"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function"
            },
            {
                "constant": True,
                "inputs": [],
                "name": "decimals",
                "outputs": [{"name": "", "type": "uint8"}],
                "payable": False,
                "stateMutability": "view",
                "type": "function"
            }
        ]

    def initToken(self, token_address, pair_address):
        self.token_address = token_address,
        self.pair_address = pair_address

        self.pairAddressCSM = web3.to_checksum_address(self.pair_address)

        self.tokenContract = self.getContract(token_address)
        self.pairContract = self.getContract(pair_address)

        self.tokenDecimals = self.getDecimals(self.tokenContract)
        self.pairDecimals = self.getDecimals(self.pairContract)

        self.token_supply = self.getSupply(self.tokenContract, self.tokenDecimals)
        self.pair_supply = self.getSupply(self.pairContract, self.pairDecimals)

    def getContract(self, token_address):
        return web3.eth.contract(address=web3.to_checksum_address(token_address), abi=self.erc20_abi)

    def getDecimals(self, token_contract: Contract):
        return token_contract.functions.decimals().call()

    def getSupply(self, contract, decimals):
        supply = contract.functions.totalSupply().call()
        return supply / (10 ** decimals)

    def getPairBalance(self):
        balance_in_pool = self.tokenContract.functions.balanceOf(self.pairAddressCSM).call()
        return balance_in_pool / (10 ** self.tokenDecimals)

    def getBurnedBalance(self):
        burn_address = web3.to_checksum_address("0x000000000000000000000000000000000000dEaD")
        burned_tokens = self.pairContract.functions.balanceOf(burn_address).call()
        self.burned_balance = burned_tokens / (10 ** self.pairDecimals)
        return self.burned_balance

    def getBurnedPercentage(self):
        return (self.burned_balance / self.pair_supply) * 100 if self.pair_supply > 0 else 0

    def getAddedLiquidity(self) -> float:
        # Получаем все блоки в диапазоне
        # Сначала собираем все события Transfer с нужным фильтром
        transfer_events = self.tokenContract.events.Transfer().create_filter(
            fromBlock=0, toBlock='latest', argument_filters={'from': self.token_address}
        ).get_all_entries()

        # Словарь для хранения транзакций по их хешам, чтобы избежать повторных вызовов
        tx_cache = {}
        total_added = 0

        for event in transfer_events:
            tx_hash = event['transactionHash']
            if tx_hash not in tx_cache:
                tx_cache[tx_hash] = web3.eth.get_transaction(tx_hash)

            tx_input = tx_cache[tx_hash]['input'].hex()
            if tx_input.startswith('0xc9567bf9') or tx_input.startswith('0xf305d719'):
                total_added += event['args']['value']

        # Сохраняем и возвращаем результат
        self.addedLiq = total_added / (10 ** self.tokenDecimals)
        return self.addedLiq

    def getAddedLiqPercentage(self):
        return (self.addedLiq / self.token_supply) * 100 if self.token_supply > 0 else 0

    def getAllInfo(self):
        ts = self.token_supply
        bb = self.getBurnedBalance()
        bp = self.getBurnedPercentage()
        al = self.getAddedLiquidity()
        ap = self.getAddedLiqPercentage()
        return dict(
            total_supply=ts,
            pair_balance=al,
            pair_percent=ap,
            burned_balance=bb,
            burned_percent=bp,
        )


if __name__ == "__main__":
    print("Connected to node")
    token_address = "0x19848077f45356b21164c412Eff3D3E4ff6Ebc31"
    pair_address = "0xB01cC2918234ec8e3Fd649Df395837DDC9B88353"
    analyzer = TokenWeb3Stats()
    analyzer.initToken(token_address, pair_address)
    info = analyzer.getAllInfo()
    print(json.dumps(info, indent=4))
