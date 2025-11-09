import json
import requests
import logging
import re 
import binascii
import hashlib
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519


# import requests

# Load the PEM key
pem_key = """
-----BEGIN PRIVATE KEY-----
B-----substitute---with---a---private---key----E
-----END PRIVATE KEY-----
"""

pem_bytes = pem_key.encode('utf-8')

key = serialization.load_pem_private_key(pem_bytes, password=None)
ed25519_key = key.private_bytes_raw()

def sha512_hash(input_string):
    # Create a new SHA-512 hash object
    sha512_hasher = hashlib.sha512()
    # Convert the input string to bytes
    input_bytes = input_string.encode('ascii')
    # Update the hash object with the input bytes
    sha512_hasher.update(input_bytes)
    # Get the hexadecimal representation of the hash
    hash_hex = sha512_hasher.hexdigest()
    # Return the hash
    return hash_hex

def myLog(msg):
    logging.info(msg)
    print(msg)

def error500(msg):
    myLog(msg)
    return {
        'statusCode': 500,
        'body': msg,
        'headers': {'Content-Type': 'text/plain'}}


def respond(err, res, headers):
    return {
        'statusCode': '400' if err else '200',
        'body': err.message if err else res,
        'headers': headers,
    }

def lambda_handler(event, context):
    myLog('Python HTTP trigger function processed a request. 1005')
    # Access headers from the event object
    headers = event.get('headers', {})

    if not "Accept-Signature" in headers and not "accept-signature" in headers:
        return error500("Accept-Signature not in request")
    
    acceptsignature = headers.get("Accept-Signature")
    if not acceptsignature:
        acceptsignature = headers.get("accept-signature")
    myLog("Accept-Signature in request: " + acceptsignature)
    match = re.search('nonce=([0-9]+);', acceptsignature)
    if not match:
        return error500('nonce not found')

    nonce = match.group(1)
    myLog("nonce: " + nonce)

    body_str = event.get('body', '')
    myLog("body: " + body_str)
    body = json.loads(body_str)
    if not "__typename" in body:
        return error500("__typename not in request")
    

    approve = True
    match body["__typename"]:
        case "OperationCreateVault_v3":
            if body["voting"] and body["voting"]["votes"] and any('fq' in vote['device']['id'] for vote in body["voting"]["votes"]):
                myLog("OperationCreateVault_v3 - not approving")
                approve = False
            elif body["details"] and body["details"]["vault"] and body["details"]["vault"]["details"] and ('malicious' in body["details"]["vault"]["details"]["name"]):
                myLog("OperationCreateVault_v3 - not approving")
                approve = False
        case "OperationReshare_v3":
            if body["rDetails"] and body["rDetails"]["newThreshold"] and body["rDetails"]["newThreshold"] == 7:
                myLog("OperationReshare_v3 - not approving")
                approve = False
        case "OperationSign":
            if body["details"] and body["details"]["vault"] and body["details"]["vault"]["details"] and ('malicious' in body["details"]["vault"]["details"]["name"]):
                myLog("OperationSign - not approving")
                approve = False
            elif body["signingData"] and body["signingData"]["data"] and ('malicious' in body["signingData"]["data"]):
                myLog("OperationSign - not approving")
                approve = False


    if approve:
        myLog("approving the request")
        decision = json.dumps({"status": "approved", "nonce": int(nonce)})
    else:
        myLog("rejecting the request")
        decision = json.dumps({"status": "rejected", "nonce": int(nonce)})

    content_hash_value = sha512_hash(decision)
    content_digest = base64.b64encode(bytearray.fromhex(content_hash_value)).decode('ascii')
    # careful with line breaks and spaces below
    message = """content-type: application/json
digest: SHA-512=<digest>"""
    message = message.replace("<digest>", content_digest)

    ed25519_sk = ed25519.Ed25519PrivateKey.from_private_bytes(ed25519_key)
    myLog("message: " + message)
    myLog("message (hex): " + message.encode('utf-8').hex())
    signature = ed25519_sk.sign(message.encode('utf-8'))
    signature_hex = signature.hex()
    myLog("signature (hex):" + signature_hex.upper())
    signature_b64 = base64.b64encode(signature).decode('ascii')
    myLog("signature (base64):" + signature_b64)
    keyId="eddsa-key"
    signature_header = "keyId=\"{keyId}\",algorithm=\"hs2019\",headers=\"content-type digest\",signature=\"{signature}\"".format(keyId = keyId, signature = signature_b64)
    digest_header = "SHA-512={digest}".format(digest = content_digest)
    return respond(
        None,
        decision,
        headers={"Content-Type": "application/json", "Signature": signature_header, "digest": digest_header,}
    )
