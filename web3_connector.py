from web3 import Web3

# Setup
alchemy_url = "https://eth-mainnet.g.alchemy.com/v2/lK2v_qBdtAzE5BFKZrquknGMWfD7bwbP"
w3 = Web3(Web3.HTTPProvider(alchemy_url))

# ABI для стандарта ERC-20
erc20_abi = [
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
        "outputs": [
            {
                "name": "",
                "type": "uint256"
            }
        ],
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

# Проверка подключения
if w3.is_connected():
    print("Connected to Ethereum node")
else:
    print("Failed to connect to Ethereum node")
    

def getContract(token_address):
    return w3.eth.contract(address=Web3.to_checksum_address(token_address), abi=erc20_abi)

def getDecimals(token_contract):
    return token_contract.functions.decimals().call()

def getTotalSupply(token_address, token_contract=None):
    if token_contract is None:
        token_contract = getContract(token_address)
    
    decimals = getDecimals(token_contract)
        
    # Вызов функции totalSupply
    total_supply = token_contract.functions.totalSupply().call()

    # Преобразование total supply в читаемый формат с учетом десятичных знаков
    total_supply_readable = total_supply / (10 ** decimals)

    return total_supply_readable

def getTotalSupply2(token_address, token_contract=None):
    if token_contract is None:
        token_contract = getContract(token_address)
    
    # Вызов функции totalSupply
    total_supply = token_contract.functions.totalSupply().call()
    decimals = getDecimals(token_contract)
    
    return total_supply, decimals

def getPairBalance(token_address, pair_address, token_contract=None):
    if token_contract is None:
        # Создание контрактного объекта токена
        token_contract = getContract(token_address)

    decimals = getDecimals(token_contract)

    # Получение баланса токенов в пуле
    balance_in_pool = token_contract.functions.balanceOf(Web3.to_checksum_address(pair_address)).call()
    balance_in_pool_readable = balance_in_pool / (10 ** decimals)

    return balance_in_pool_readable
    

def getBurnedBalance(token_address, token_contract=None):
    if token_contract is None:
        # Создание контрактного объекта токена
        token_contract = getContract(token_address)
        
    # Получение общего количества сожженных токенов
    burn_address = Web3.to_checksum_address("0x000000000000000000000000000000000000dEaD")
    burned_tokens = token_contract.functions.balanceOf(burn_address).call()
    decimals = getDecimals(token_contract)
    burned_tokens_readable = burned_tokens / (10 ** decimals)

    return burned_tokens_readable

def getBurnedPercentage(contract_address):
    contract = getContract(contract_address)
    
    # Получение общего количества токенов
    total_supply, decimals = getTotalSupply2(contract_address, contract)
    
    # Получение количества сожженных токенов
    burned_tokens_readable = getBurnedBalance(contract_address, contract)
    
    # Преобразование total supply и burned tokens в читаемый формат с учетом десятичных знаков
    total_supply_readable = total_supply / (10 ** decimals)
    
    # Вычисление процента сожженных токенов
    burned_percentage = (burned_tokens_readable / total_supply_readable) * 100 if total_supply > 0 else 0
    
    return burned_percentage

if __name__ == "__main__":
    token_address = "0x66536F22fdf0D16299B2684a48C20431286de48f"
    burned_percentage = getBurnedPercentage(token_address)
    print(f"Burned Percentage: {burned_percentage}%")