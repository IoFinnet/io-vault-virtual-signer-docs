# Sample Approvals API implementations

## Sample implementations of the Virtual Signer Approvals API following the HTTP Message Signatures protocol

### For Developers

The customer's API that implements approval/rejection/abstention calls must implement the
HTTP Message Signatures protocol. The `lambda-js` and `lambda-python` folders contain sample
NodeJS and Python scripts for use as AWS lambda. The `azure_container_app_proj` folder also contains a sample Azure Container App with another
Python Function that can support the development of an API for approvals. This project will deploy the Python
script within a Docker image. *Note that the NodeJS and Python scripts refer to cryptographic libraries. It is
common for cryptographic libraries to contain native bindings that are CPU-specific. By deploying these projects
as Docker containers, one avoids problems of cross-platform incompatibilities.*
`azure_container_app_proj` contains a Dockerfile and the section below contains deployment instructions. 
`lambda-js` and `lambda-python`, in turn, contain only sample scripts.

### On the request contents
The Virtual Signer sends requests (as an HTTP client) serialized as JSON to the customer's API when `"ApprovalMode"` in its configuration is set to `"API"`.
See https://docs.iofinnet.com/docs/approve-with-api-sample-requests#/ for the details of these requests.

### On response signatures
The request and the response must follow the HTTP Message Signatures protocol ( https://datatracker.ietf.org/doc/draft-ietf-httpbis-message-signatures/ ).
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
    "__typename": "OperationTransferOut_v3",
    "id" : "xw8ufea4rdtaaaas1ck89htz",
    ...
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
> Content-Length: 1939
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

