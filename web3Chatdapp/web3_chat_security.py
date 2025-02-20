from web3 import Web3
import json
import requests
from io import BytesIO

# Replace these with your own details
INFURA_URL = "https://json-rpc.evm.testnet.iotaledger.net"  # -- rpc for IOTA-EVM Testnet --
# CONTRACT_ADDRESS = "0x4e76F57CC0e6c30A8312DfD116817bFE6B1F2C95" -- don't change it , used for future reference !!
CONTRACT_ADDRESS = "0xF0871f790692E41baCBE811610aF982Ffd19396b"  # current address :fire
PRIVATE_KEY = "d6f0733d8ee97dc32f83e9fd7247bfc8a6527e92653f77a5bda28d76c13fd9e7"  # account key -- ! --
SENDER_ADDRESS = "0xD8338cb83c2107FAf8ceA049D119912aa5babad8" 

# Pinata API 
PINATA_API_KEY = "ff8bb0e5c012e5a4aa32"
PINATA_API_SECRET = "9652e162fe06ba0ceb91cc1289f025969a90b03c1a3ecfe7c293ea11997ad441"
PINATA_BASE_URL = "https://api.pinata.cloud"
# https://api.pinata.cloud/pinning/pinFileToIPFS to upload
PINATA_UPLOAD_URL = f"{PINATA_BASE_URL}/pinning/pinFileToIPFS"
IPFS_GATEWAY = "https://gateway.pinata.cloud/ipfs/"

# contract ABI
CONTRACT_ABI = json.loads("""
[
	{
		"anonymous": false,
		"inputs": [
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "timestamp",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "from",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "uint256",
				"name": "to",
				"type": "uint256"
			},
			{
				"indexed": false,
				"internalType": "string",
				"name": "content",
				"type": "string"
			}
		],
		"name": "MessageSent",
		"type": "event"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_from",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_to",
				"type": "uint256"
			},
			{
				"internalType": "string",
				"name": "_content",
				"type": "string"
			}
		],
		"name": "sendMessage",
		"outputs": [],
		"stateMutability": "nonpayable",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_user1",
				"type": "uint256"
			},
			{
				"internalType": "uint256",
				"name": "_user2",
				"type": "uint256"
			}
		],
		"name": "getChatHistory",
		"outputs": [
			{
				"components": [
					{
						"internalType": "uint256",
						"name": "timestamp",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "from",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "to",
						"type": "uint256"
					},
					{
						"internalType": "string",
						"name": "content",
						"type": "string"
					}
				],
				"internalType": "struct SimpleChatApp.Message[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	},
	{
		"inputs": [
			{
				"internalType": "uint256",
				"name": "_userPhone",
				"type": "uint256"
			}
		],
		"name": "getUserMessages",
		"outputs": [
			{
				"components": [
					{
						"internalType": "uint256",
						"name": "timestamp",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "from",
						"type": "uint256"
					},
					{
						"internalType": "uint256",
						"name": "to",
						"type": "uint256"
					},
					{
						"internalType": "string",
						"name": "content",
						"type": "string"
					}
				],
				"internalType": "struct SimpleChatApp.Message[]",
				"name": "",
				"type": "tuple[]"
			}
		],
		"stateMutability": "view",
		"type": "function"
	}
]
""")

# Connect to IOTA-EVM network
web3 = Web3(Web3.HTTPProvider(INFURA_URL))

# Check connection
if web3.is_connected():
    print("Connected to IOTA network")
else:
    print("Failed to connect to Ethereum network")
    exit()

# Contract object
contract = web3.eth.contract(address=CONTRACT_ADDRESS, abi=CONTRACT_ABI)

def upload_to_ipfs(file_path):
    try:
        # Open the file to upload
        with open(file_path, "rb") as file:
            files = {"file": file}
            headers = {
                "pinata_api_key": PINATA_API_KEY,
                "pinata_secret_api_key": PINATA_API_SECRET,
            }

            # Send request to Pinata
            response = requests.post(PINATA_UPLOAD_URL, files=files, headers=headers)

            # Check response status
            if response.status_code == 200:
                ipfs_hash = response.json()["IpfsHash"]
                print(f"File uploaded to IPFS with hash: {ipfs_hash}")
                return ipfs_hash
            else:
                print(f"Failed to upload file to IPFS: {response.json()}")
                return None
    except Exception as e:
        print(f"Error uploading to IPFS: {e}")
        return None

# Get file from ipfs
def fetch_from_ipfs(ipfs_hash):
    try:
        url = f"{IPFS_GATEWAY}{ipfs_hash}"  # Use IPFS gateway to fetch the file
        response = requests.get(url, stream=True)

        if response.status_code == 200:
            print(f"Successfully fetched file from IPFS: {url}")
            return response.content
        else:
            print(f"Failed to fetch file from IPFS: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error fetching from IPFS: {e}")
        return None


def send_message(sender_phone, receiver_phone, message_content, media_file_path=None):
    try:
        # If a media file is provided, upload it to IPFS
        if media_file_path:
            ipfs_hash = upload_to_ipfs(media_file_path)
            if not ipfs_hash:
                print("Failed to upload media to IPFS. Aborting message send.")
                return
            # Include IPFS hash in the message content
            message_content += f" [IPFS: {ipfs_hash}]"

        # Get the nonce for the sender's wallet
        nonce = web3.eth.get_transaction_count(SENDER_ADDRESS)

        # Build the transaction
        txn = contract.functions.sendMessage(sender_phone, receiver_phone, message_content).build_transaction({
            'from': SENDER_ADDRESS,
            'nonce': nonce,
            'gas': 2000000,
            'gasPrice': web3.to_wei('10', 'gwei')  # gas_prive <= 30 (at max) !
        })

        # Sign 
        signed_txn = web3.eth.account.sign_transaction(txn, private_key=PRIVATE_KEY)

        # Send transaction
        txn_hash = web3.eth.send_raw_transaction(signed_txn.raw_transaction)
        print(f"Transaction hash: {txn_hash.hex()}")

        # Wait for the transaction to be mined
        receipt = web3.eth.wait_for_transaction_receipt(txn_hash)
        print(f"Transaction successful! Block number: {receipt['blockNumber']}")
    except Exception as e:
        print(f"Error sending message: {e}")


def get_chat_history(user1, user2):
    try:
        messages = contract.functions.getChatHistory(user1, user2).call()
        print(f"Chat history between {user1} and {user2}:")

        for msg in messages:
            timestamp, sender, receiver, content = msg
            print(f"Timestamp: {timestamp}, From: {sender}, To: {receiver}, Content: {content}")

            # Check if the message contains an IPFS hash
            if "[IPFS:" in content:
                ipfs_hash = content.split("[IPFS:")[1].split("]")[0].strip()
                print(f"Fetching multimedia from IPFS: {ipfs_hash}")
                media_data = fetch_from_ipfs(ipfs_hash)

                # Save the media file locally (optional) [comment it before the OG deployment !] -- ! --
                if media_data:
                    file_name = f"media_{ipfs_hash[:8]}.bin"
                    with open(file_name, "wb") as media_file:
                        media_file.write(media_data)
                    print(f"Media saved locally as: {file_name}")
    except Exception as e:
        print(f"Error retrieving chat history: {e}")
        
def get_user_messages(user_phone):
    try:
        messages = contract.functions.getUserMessages(user_phone).call()
        print(f"Messages for {user_phone}:")
        user_data = []
        for msg in messages:
            timestamp = msg[0]
            sender = msg[1]
            receiver = msg[2]
            content = msg[3]
            user_data.append({
                'Timestamp': timestamp,
                'From': sender,
                'To': receiver,
                'Content': content
            })
            if "[IPFS:" in content:
                ipfs_hash = content.split("[IPFS:")[1].split("]")[0].strip()
                print(f"Detected multimedia message. IPFS Hash: {ipfs_hash}")
                try:
                    file_data = fetch_from_ipfs(ipfs_hash)
                    if file_data:
                        print(f"Successfully retrieved multimedia for IPFS Hash: {ipfs_hash}")
                    else:
                        print(f"Failed to retrieve multimedia for IPFS Hash: {ipfs_hash}")
                except Exception as fetch_error:
                    print(f"Error fetching IPFS data: {fetch_error}")
        return user_data
    except Exception as e:
        print(f"Error retrieving messages: {e}")
        return []


# if __name__ == "__main__": 
#     sender_phone = 11
#     receiver_phone = 99
#     # text_message = "Hello! How are you?"
#     # print(f"Sending text message from {sender_phone} to {receiver_phone}: {text_message}")
#     # send_message(sender_phone, receiver_phone, text_message)

#     # message
#     multimedia_message = "Here is a photo"
#     media_file_path = "sunset.jpg"  # -- replace the path -- !
#     print(f"Sending multimedia message from {sender_phone} to {receiver_phone}: {multimedia_message}")
#     send_message(sender_phone, receiver_phone, multimedia_message, media_file_path)

#     # Example: Retrieve chat history
#     print(f"\nRetrieving chat history between {sender_phone} and {receiver_phone}...")
#     get_chat_history(sender_phone, receiver_phone)


# # with multimedia . ! --

# send_message(23423,23423,'hi')