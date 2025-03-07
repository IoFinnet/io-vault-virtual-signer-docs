// SPDX-License-Identifier: GPL-3.0

pragma solidity >=0.8.2 <0.9.0;

/**
 * @title DeviceConfigManager
 * @dev Store & retrieve value in a variable
 * @custom:dev-run-script ./scripts/deploy_with_ethers.ts
 */
contract DeviceConfigManager {
    struct ConfigCore {
        address owner;
        // Service
        uint16 Port;

        // Authentication
        string AuthClientId;
        string AuthClientSecret;

        ApprovalConfig ConfigApproval;

        // MQTT
        string MQTTEndpoint;
        string MQTTCACert;

        // VS Devices
        string[] InitialDevices;
        string OrgId;

        // Prometheus
        uint16 PrometheusPort;

        WifiConfig ConfigWifi;
    }

    struct ApprovalConfig {
        // Approval
        string ApprovalMode; // Possible values: "AlwaysApprove", "SmartContract", "API". But these are encrypted.
        string ApprovalNodeRPCAddress;
        string ApprovalSmartContractAddress;
        string ExternalTransactionApprovalURL;
        string ExternalReshareApprovalURL;
        string ApprovalHTTPPublicKeyHex;
    }

    struct WifiConfig {
        string wifiSSID; // New field for WiFi SSID
        string wifiPassphrase; // New field for WiFi passphrase
    }

    mapping(bytes32 => ConfigCore) public deviceConfigs;

    modifier onlyOwner(bytes32 hashedMacAddress) {
        require(
            msg.sender == deviceConfigs[hashedMacAddress].owner,
            "Not the owner"
        );
        _;
    }

    function setConfigCore(
        bytes32 hashedMacAddress,
        ConfigCore memory config
    ) public {
        // TODO - uncomment - require(deviceConfigs[hashedMacAddress].owner == address(0), "Config already exists");
        config.owner = msg.sender;
        deviceConfigs[hashedMacAddress] = config;
        //emit Config1Updated(hashedMacAddress);
    }

    function getConfigCore(
        bytes32 hashedMacAddress
    ) public view returns (ConfigCore memory) {
        return deviceConfigs[hashedMacAddress];
    }

    function updateConfigCoreFields(
        bytes32 hashedMacAddress,
        uint16 newPort,
        string memory newAuthClientId,
        string memory newAuthClientSecret
    ) public onlyOwner(hashedMacAddress) {
        ConfigCore storage config = deviceConfigs[hashedMacAddress];
        config.Port = newPort;
        config.AuthClientId = newAuthClientId;
        config.AuthClientSecret = newAuthClientSecret;
        // TODO other fields
        // emit Config1Updated(hashedMacAddress);
    }

    function validateApprovalMode(
        string memory mode
    ) internal pure returns (bool) {
        return (stringsEqual(mode, "AlwaysApprove") ||
            stringsEqual(mode, "SmartContract") ||
            stringsEqual(mode, "API"));
    }

    function stringsEqual(
        string memory a,
        string memory b
    ) internal pure returns (bool) {
        return keccak256(abi.encodePacked(a)) == keccak256(abi.encodePacked(b));
    }
}
