const crypto = require('crypto');
const noble = require('noble-ed25519');
const pemJwk = require('pem-jwk').pem2jwk;

const pem_key = `
-----BEGIN PRIVATE KEY-----
...
-----END PRIVATE KEY-----
`;

exports.handler = async (event, context) => {

    // Convert PEM to JWK
    let jwkKey = pemJwk(pem_key);

    // Convert JWK to Ed25519 Private Key
    let ed25519_key = Buffer.from(jwkKey.d, 'base64');

    console.log("private key:" + ed25519_key.toString('hex'));

    const sha512_hash = (input_string) => {
        return crypto.createHash('sha512').update(input_string).digest('hex');
    }
    let nonce = ""
    if (event.headers && event.headers['VS-Nonce']) {
        nonce = event.headers['VS-Nonce']
    }
    let response_str = "{ \"status\": \"approved\", \"nonce\":" + nonce + "}";
    let content_hash_value = sha512_hash(response_str);
    let content_digest = Buffer.from(content_hash_value, 'hex').toString('base64');
    console.log("SHA512 content digest: "+ content_digest);

    let message = `content-type: application/json
digest: SHA-512=${content_digest}`;

    // Convert the private key from hex to Uint8Array for noble-ed25519
    let privateKeyUint8Array = new Uint8Array(ed25519_key.buffer);

    const signature = await noble.sign(message, privateKeyUint8Array);
    let signature_hex = Buffer.from(signature).toString('hex');
    console.log("signature (hex):" + signature_hex.toUpperCase());
    let signature_b64 = Buffer.from(signature).toString('base64');
    console.log("signature (base64):" + signature_b64);

    return {
        statusCode: 200,
        headers: {
            'Content-Type': 'application/json',
            'digest': `SHA-512=${content_digest}`,
            'Signature': signature_b64
        },
        body: response_str,
        isBase64Encoded: false
    };
}
