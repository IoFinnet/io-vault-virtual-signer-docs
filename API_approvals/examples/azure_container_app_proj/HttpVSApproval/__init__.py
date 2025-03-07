import logging
import re 
import azure.functions as func
import json
import binascii
import hashlib
import base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ed25519

# import requests

# Load the PEM key
pem_key = """
-----BEGIN PRIVATE KEY-----
MC4CAQAwBQYDK2VwBCIEIBrCod3u4wxgY+N2KED2Y8YKTMEz4fRHOx5HrlraQP86
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
    return func.HttpResponse(
            body=msg,
            status_code=500
    )

def main(req: func.HttpRequest) -> func.HttpResponse:
    myLog('Python HTTP trigger function processed a request.')
    if not "Accept-Signature" in req.headers:
        return error500("Accept-Signature not in request")
    
    acceptsignature = req.headers["Accept-Signature"]
    myLog("Accept-Signature in request: " + acceptsignature)
    match = re.search('nonce=([0-9]+);', acceptsignature)
    if not match:
        return error500('nonce not found')

    nonce = match.group(1)
    myLog("nonce: " + nonce)

    body_str = req.get_body().decode("utf-8")
    body = json.loads(body_str)
    if not "__typename" in body:
        return error500("__typename not in request")
    
    if body["__typename"] == "ReshareRequest":
        approve = True
    else:
        if not "amountOriginal" in body:
            return error500("amountOriginal not in request")
        else:
            approve = "666" not in body["amountOriginal"]

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
    return func.HttpResponse(
        body=decision,
        status_code=200,
        headers={"Content-Type": "application/json", "Signature": signature_header, "digest": digest_header,}
    )
