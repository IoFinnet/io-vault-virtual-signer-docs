// SPDX-License-Identifier: UNLICENSED
pragma solidity ^0.8.9;
/**
 * @title Approval
 */
contract Approval {

uint8 public constant APPROVE = 0;
uint8 public constant REJECT = 1;
uint8 public constant ABSTAIN = 2;
bytes32 public constant REJECTAMOUNT = keccak256(abi.encodePacked("6660000000000000")); // 0.00666 to Wei (precision of 18)
bytes32 public constant ABSTAINAMOUNT = keccak256(abi.encodePacked("9990000000000000")); // 0.00999 to Wei (precision of 18)
bytes32 public constant REJECTSTRING = keccak256(abi.encodePacked("do fail the test"));
bytes32 public constant ABSTAINSTRING = keccak256(abi.encodePacked("do abstain"));

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
	string Source          ;
	string ContractData     ;
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

    function decodeKeygenReshare(bytes memory data) public pure returns (string memory, uint) {
        KeygenReshareRequestSC memory kgReq = abi.decode(data, (KeygenReshareRequestSC));
        return (kgReq.Id, kgReq.NewThreshold);
    }

    function decodeTx(bytes memory data) public pure returns (string memory) {
        SigningTransactionRequestSC memory txReq = abi.decode(data, (SigningTransactionRequestSC));
        return (txReq.AmountOriginal);
    }

    function decodeSignOp(bytes memory data) public pure returns (string memory, uint) {
        NodeOpSignRequestSC memory sopReq = abi.decode(data, (NodeOpSignRequestSC));
        return (sopReq.Data, sopReq.ChainId);
    }

    function approvedKeygenReshare(bytes memory encodedKeygenReshare) public pure returns (uint8){
        (string memory id, uint t) = decodeKeygenReshare(encodedKeygenReshare);
        if (t == 9) {
            return ABSTAIN;
        } else if (t >= 10) {
            return REJECT;
        }
        return APPROVE;
    }

    function approvedTx(bytes memory encodedTx) public pure returns (uint8){
        (string memory amountOriginal) = decodeTx(encodedTx);
        bytes32 amountOriginalBytes = keccak256(abi.encodePacked(amountOriginal));
        if (amountOriginalBytes == REJECTAMOUNT) {
            return REJECT;
        } else if (amountOriginalBytes == ABSTAINAMOUNT) {
            return ABSTAIN;
        }
        return APPROVE;
    }

    function approvedSignOp(bytes memory encodedSignOp) public pure returns (uint8){
        (string memory data, uint chainId) = decodeSignOp(encodedSignOp);
        bytes32 dataBytes = keccak256(abi.encodePacked(data));
        if (dataBytes == REJECTSTRING) {
            return REJECT;
        } else if (dataBytes == ABSTAINSTRING) {
            return ABSTAIN;
        }
        return APPROVE;
    }
}