# Sample Approvals API implementations

## Sample implementations of the Virtual Signer Approvals API following the HTTP Message Signatures protocol

### For Developers

The main README.md mentions that the customer's API that implements approval/rejection/abstention calls must implement the
HTTP Message Signatures protocol. The `lambda` folder contains a sample
NodeJS script for use as a AWS lambda. The `azure_container_app_proj` folder contains a sample Azure Container App with a
Python Function that can support the development of an API for approvals. This project will deploy the Python
script within a Docker image. *Note that both NodeJS and Python scripts refer to cryptographic libraries. It is
common for cryptographic libraries to contain native bindings that are CPU-specific. By deploying these projects
as Docker containers, one avoids problems of cross-platform incompatibilities.*
`azure_container_app_proj` contains a Dockerfile and the section below contains deployment instructions. 
`lambda`, in turn, contains only the sample NodeJS script.

### On the request contents
The Virtual Signer sends requests serialized as JSON to the customer's API. That is, the body of the request in its
entirety is the JSON serialization of two vault objects, depending on the type of user action: ReshareRequest or
TransactionRequest. See https://docs.iofinnet.com/reference/vault-objects#resharerequest and
https://docs.iofinnet.com/reference/vault-objects#transactionrequest for the details of these objects.
A ReshareRequest may represent a vault creation or a request to reshare, that is, to change the party composition
and/or weights of the vault. A TransactionRequest represents a request to sign either a transaction (as in a
transfer, a mint, a burn, etc) or a sign operation (as in a signature of data in a standard format).

### On response signatures
The request and the response follow the HTTP Message Signatures protocol ( https://datatracker.ietf.org/doc/draft-ietf-httpbis-message-signatures/ ).
The sample scripts have an Ed25519 private key. They take a JSON that is the body of the response to produce
a content digest and a signature. This is a sample response body:

```
{ "status": "rejected", "nonce": 3827271 }
```

Possible values of "status" in the response are "approved", "rejected", or "abstain".

The response JSON must echo back the `nonce` originally included in the request (`VS-Nonce` header). Its maximum value
is 0x7FFFFFFFFFFFFFFE.

Below is a sample request/response pair, where the Python script within the Azure Container App
produces the signed response, following the HTTP Message Signatures protocol:

```shell
 % curl -v --location 'https://vsapprovaltestfunc.greenbay-b1c1bd0a.eastus.azurecontainerapps.io/api/httpvsapproval' \
--header 'Accept-Signature: sig1=("content-type" "digest");nonce=83727271;keyid="eddsa-key"' \
--header 'VS-Nonce: 83727271' \
--header 'Content-Type: application/json' \
--data-raw '{
    "__typename": "TransactionRequest",
    "amountOriginal": "0.00606103",
    "amountUsd": "2.78440028823084577",
}'
*   Trying 4.157.75.188:443...
* Connected to vsapprovaltestfunc.greenbay-b1c1bd0a.eastus.azurecontainerapps.io (4.157.75.188) port 443 (#0)
[...]
> POST /api/httpvsapproval HTTP/2
> Host: vsapprovaltestfunc.greenbay-b1c1bd0a.eastus.azurecontainerapps.io
> User-Agent: curl/8.1.2
> Accept: */*
> Accept-Signature: sig1=("content-type" "digest");nonce=83727271;keyid="eddsa-key"
> VS-Nonce: 83727271
> Content-Type: application/json
> Content-Length: 439
> 
* We are completely uploaded and fine
< HTTP/2 200 
< content-type: application/json
< date: Fri, 04 Aug 2023 21:30:53 GMT
< server: Kestrel
< request-context: appId=cid-v1:62fa0dbc-ae2b-4a3d-b3d4-593648a55c62
< signature: keyId="eddsa-key",algorithm="hs2019",headers="content-type digest",signature="Ow0Sh6VItuKtC6nqAeB7Qx5GPcVe3rvjbZeRlLoRbYZKLawOv3ruFdoiAWWiKdgyxwITDpmFO8TqSfvO9140BQ=="
< digest: SHA-512=b9e4zA1CER+mr+K+Pmn1G1OaFc1cWXY5lKtk6Mdh3fmyy0mwLVFKmdpNidd3apveLmiRXFSAywg9YzMHMJUN3g==
< 
* Connection #0 to host vsapprovaltestfunc.greenbay-b1c1bd0a.eastus.azurecontainerapps.io left intact
{"status": "approved", "nonce": 83727271}
```

### The azure_container_app_proj project
You can open the project in Visual Studio Code. To deploy it, follow the steps of 
https://learn.microsoft.com/en-us/azure/azure-functions/functions-deploy-container-apps?tabs=acr%2Cbash&pivots=programming-language-python.

After updates to the Python script, to redeploy the updated Docker container, run

```
# az acr login --name <REGISTRY_NAME>
OLDV=v1.0.11
NEWV=v1.0.12
docker image rm <LOGIN_SERVER>/azurefunctionsimage:$OLDV
docker image rm <DOCKER_ID>/azurefunctionsimage:$OLDV

docker build --tag <DOCKER_ID>/azurefunctionsimage:$NEWV .
docker tag <DOCKER_ID>/azurefunctionsimage:$NEWV <LOGIN_SERVER>/azurefunctionsimage:$NEWV
docker push <LOGIN_SERVER>/azurefunctionsimage:$NEWV
az functionapp function show --resource-group AzureFunctionsContainers-rg --name <APP_NAME>  --function-name HttpVSApproval --query invokeUrlTemplate
```

The images below are screenshots of the Azure Portal.

After a deployment, you can set the current image of the Function App:
![Image Tag](azure_images/func_app_config.png?raw=true "Current image tag of Function App")

After a deployment, you can also manually delete old images in the registry:
![Registry Repo](azure_images/cont_registry_repos.png?raw=true "Delete old images")

You can monitor the logs by clicking on the invocation trace for a request/response pair (there is a delay):
![Monitor Logs](azure_images/Function_Monitor_logs.png?raw=true "Monitor Logs")

Alternatively, you can read the logs by accessing the Application Insights and querying the `traces` table (there is a delay):
![Logs in App Insights](azure_images/Function_Monitor_logs.png?raw=true "Logs in Application Insights")

