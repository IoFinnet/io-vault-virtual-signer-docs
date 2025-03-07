# Loading Configuration from a Smart Contract
   `DeviceConfigManager.sol` is a sample Solidity smart contract that holds configuration for various Virtual Signer
instances. Note that the configuration attributes of type string should be encrypted and decrypted by smart contract
clients. Developers may use the env/config/sc-util/scutil.go command-line utility to write and read configuration
to/from the smart contract. You may build the scutil.go tool with the command `go build scutil.go`.
   `setConfigCore.sh` and `getConfigCore.sh` are scripts that invoke `scutil`. In particular, note that
`setConfigCore.sh` refers to one or more .json files that contain main configuration to be encrypted and written
onto the configuration smart contract. (Equivalent functionality is performed by the configuration dApp).

# Approval via Smart Contract

`Approval.sol` is a sample Solidity smart contract that approves, rejects or abstains from the request. When compiling the
smart contract, the Solidity compiler generates an ABI JSON. We take this ABI JSON to generate Go bindings using the 
go-ethereum `abigen` tool:
`./abigen --abi Approval.abi -pkg approval --type Approval --out sc_approval_generated.go`

These steps are described at https://geth.ethereum.org/docs/developers/dapp-developer/native-bindings.

The smart contract must have three functions with the following signatures:
```
function approvedKeygenReshare(string memory encodedKeygenReshare) public returns (uint8)
function approvedTx(string memory encodedTx) public returns (uint8)
function approvedSignOp(string memory encodedSignOp) public returns (uint8)
```

They may be marked as `pure` optionally. Each function determines if a request is approved (0),
rejected (1) or abstained from (2). The string arguments are ABI encoded structs that must also be defined in the
smart contract:

```
struct KeygenReshareRequestOriginalSignersSC {
   uint Weight ;
   string Uiid ;
   string Id   ;
}

struct KeygenReshareRequestNewSignersSC {
   uint Weight ;
   string Uiid ;
   string Id   ;
}

struct KeygenReshareRequestSC {
   string Typename             ;
   string Id                   ;
   string ExpiresAt            ;
   string OrganisationId       ;
   string ReshareRequestStatus ;
   string VaultId              ;
   string VaultName            ;
   uint ReshareNonce         ;
   uint NewThreshold         ;
   KeygenReshareRequestOriginalSignersSC[] OriginalSigners;
   KeygenReshareRequestNewSignersSC[] NewSigners;
}

struct SigningTransactionRequestMetadataSC  {
   string MaxFees            ;
   uint MaxFeePerGas         ;
   uint MaxPriorityFeePerGas ;
   string Source             ;
   string SourceUrl          ;
   string ContractData       ;
}

struct SigningTransactionRequestSC {
   string Typename                 ;
   string Id                       ;
   string CreatedAt ;
   string UpdatedAt ;
   string ExpiresAt ;
   string CreatedByUserId ;
   string AmountOriginal           ;
   string AmountUsd                ;
   string ReceivingAddress ;
   string SendingAddressId ;
   string VaultId                  ;
   string VaultName                ;
   string AssetId                  ;
   string OrganisationId           ;
   string RawTransaction           ;
   string Status ;
   string AssetExecutionType       ;
   SigningTransactionRequestMetadataSC Metadata;
   string NetworkId                ;
}

struct NodeOpSignRequestSC {
   string Typename            ;
   string Id                  ;
   string OrganisationId      ;
   string OperationSignStatus ;
   string VaultId             ;
   string VaultName           ;
   string Data                ;
   string ContentType         ;
   uint ChainId             ;
}
```

Each approve* function decodes the argument and may use a value to approve or reject.

`approvedKeygenReshare` should decode a `KeygenReshareRequestSC` object.
`approvedTx` should decode a `SigningTransactionRequestSC` object.
`approvedSignOp` should decode a `NodeOpSignRequestSC` object.

For example:
```
function decodeTx(bytes memory data) public pure returns (string memory) {
   SigningTransactionRequestSC memory txReq = abi.decode(data, (SigningTransactionRequestSC));
   return (txReq.AmountOriginal);
}

function approvedTx(bytes memory encodedTx) public returns (uint8) {
   (string memory amountOriginal) = decodeTx(encodedTx);
   amount = parse(amountOriginal);
   if (amount < 200) {
       return APPROVE;
   }
   return REJECT;
}
```

For smart contract programming, here is the ABI specification:

```json
[{"inputs":[],"name":"ABSTAIN","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"ABSTAINAMOUNT","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"ABSTAINSTRING","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"APPROVE","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"REJECT","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"REJECTAMOUNT","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[],"name":"REJECTSTRING","outputs":[{"internalType":"bytes32","name":"","type":"bytes32"}],"stateMutability":"view","type":"function"},{"inputs":[{"internalType":"bytes","name":"encodedKeygenReshare","type":"bytes"}],"name":"approvedKeygenReshare","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"bytes","name":"encodedSignOp","type":"bytes"}],"name":"approvedSignOp","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"bytes","name":"encodedTx","type":"bytes"}],"name":"approvedTx","outputs":[{"internalType":"uint8","name":"","type":"uint8"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"bytes","name":"data","type":"bytes"}],"name":"decodeKeygenReshare","outputs":[{"internalType":"string","name":"","type":"string"},{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"bytes","name":"data","type":"bytes"}],"name":"decodeSignOp","outputs":[{"internalType":"string","name":"","type":"string"},{"internalType":"uint256","name":"","type":"uint256"}],"stateMutability":"pure","type":"function"},{"inputs":[{"internalType":"bytes","name":"data","type":"bytes"}],"name":"decodeTx","outputs":[{"internalType":"string","name":"","type":"string"}],"stateMutability":"pure","type":"function"}]
```

Internally, the Virtual Signer uses the github.com/ethereum/go-ethereum/accounts/abi library for ABI encoding
(internal/approval/sc_encoding.go). At the root of the ABI structure there is a tuple and the components are the fields of Go structs
KeygenReshareRequestSC, SigningTransactionRequestSC, and NodeOpSignRequestSC. Note that these three Go structs
and any other nested structs must be the same as the structs used in the smart contract.
The Virtual Signer maps values from GraphQL requests
onto these three structs, KeygenReshareRequestSC, SigningTransactionRequestSC, and NodeOpSignRequestSC. If there are
changes to GraphQL request schema or queries that relate to these three structs, the following must be
updated within the Virtual Signer: sc_encoding.go, sc_type_mapping.go and the structs inside the smart contract.
