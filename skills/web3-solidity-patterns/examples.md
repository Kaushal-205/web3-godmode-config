# Solidity Pattern Examples

## Minimal Proxy (EIP-1167)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {Clones} from "@openzeppelin/contracts/proxy/Clones.sol";
import {Initializable} from "@openzeppelin/contracts/proxy/utils/Initializable.sol";

contract Vault is Initializable {
    address public owner;
    address public token;

    function initialize(address _token, address _owner) external initializer {
        token = _token;
        owner = _owner;
    }
}

contract VaultFactory {
    using Clones for address;

    address public immutable implementation;
    address[] public allVaults;

    event VaultCreated(address indexed vault, address indexed owner, address token);

    constructor() {
        implementation = address(new Vault());
    }

    function createVault(address token) external returns (address vault) {
        vault = implementation.clone();
        Vault(vault).initialize(token, msg.sender);
        allVaults.push(vault);
        emit VaultCreated(vault, msg.sender, token);
    }

    function createDeterministic(address token, bytes32 salt) external returns (address vault) {
        vault = implementation.cloneDeterministic(salt);
        Vault(vault).initialize(token, msg.sender);
        allVaults.push(vault);
        emit VaultCreated(vault, msg.sender, token);
    }

    function predict(bytes32 salt) external view returns (address) {
        return implementation.predictDeterministicAddress(salt);
    }
}
```

## UUPS Proxy

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {UUPSUpgradeable} from "@openzeppelin/contracts-upgradeable/proxy/utils/UUPSUpgradeable.sol";
import {OwnableUpgradeable} from "@openzeppelin/contracts-upgradeable/access/OwnableUpgradeable.sol";
import {Initializable} from "@openzeppelin/contracts-upgradeable/proxy/utils/Initializable.sol";

contract MyTokenV1 is Initializable, UUPSUpgradeable, OwnableUpgradeable {
    mapping(address => uint256) public balances;

    /// @custom:oz-upgrades-unsafe-allow constructor
    constructor() {
        _disableInitializers();
    }

    function initialize(address initialOwner) external initializer {
        __Ownable_init(initialOwner);
        __UUPSUpgradeable_init();
    }

    function mint(address to, uint256 amount) external onlyOwner {
        balances[to] += amount;
    }

    function _authorizeUpgrade(address newImplementation) internal override onlyOwner {}
}

// V2: Add new storage AFTER existing fields (append-only)
contract MyTokenV2 is MyTokenV1 {
    uint256 public maxSupply; // NEW: appended after existing storage

    function setMaxSupply(uint256 _maxSupply) external onlyOwner {
        maxSupply = _maxSupply;
    }
}
```

## Diamond Pattern (EIP-2535)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

// Simplified Diamond skeleton — use diamond-3 reference implementation for production

struct FacetCut {
    address facetAddress;
    FacetCutAction action;
    bytes4[] functionSelectors;
}

enum FacetCutAction { Add, Replace, Remove }

contract Diamond {
    struct DiamondStorage {
        mapping(bytes4 => address) selectorToFacet;
        address contractOwner;
    }

    bytes32 constant DIAMOND_STORAGE_POSITION = keccak256("diamond.standard.diamond.storage");

    function diamondStorage() internal pure returns (DiamondStorage storage ds) {
        bytes32 position = DIAMOND_STORAGE_POSITION;
        assembly { ds.slot := position }
    }

    fallback() external payable {
        DiamondStorage storage ds = diamondStorage();
        address facet = ds.selectorToFacet[msg.sig];
        require(facet != address(0), "Diamond: Function does not exist");

        assembly {
            calldatacopy(0, 0, calldatasize())
            let result := delegatecall(gas(), facet, 0, calldatasize(), 0, 0)
            returndatacopy(0, 0, returndatasize())
            switch result
            case 0 { revert(0, returndatasize()) }
            default { return(0, returndatasize()) }
        }
    }
}
```

## Governor (DAO)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {Governor} from "@openzeppelin/contracts/governance/Governor.sol";
import {GovernorSettings} from "@openzeppelin/contracts/governance/extensions/GovernorSettings.sol";
import {GovernorCountingSimple} from "@openzeppelin/contracts/governance/extensions/GovernorCountingSimple.sol";
import {GovernorVotes} from "@openzeppelin/contracts/governance/extensions/GovernorVotes.sol";
import {GovernorVotesQuorumFraction} from "@openzeppelin/contracts/governance/extensions/GovernorVotesQuorumFraction.sol";
import {GovernorTimelockControl} from "@openzeppelin/contracts/governance/extensions/GovernorTimelockControl.sol";
import {IVotes} from "@openzeppelin/contracts/governance/utils/IVotes.sol";
import {TimelockController} from "@openzeppelin/contracts/governance/TimelockController.sol";

contract MyGovernor is
    Governor,
    GovernorSettings,
    GovernorCountingSimple,
    GovernorVotes,
    GovernorVotesQuorumFraction,
    GovernorTimelockControl
{
    constructor(IVotes token, TimelockController timelock)
        Governor("MyGovernor")
        GovernorSettings(
            7200,   // votingDelay: 1 day (blocks)
            50400,  // votingPeriod: 1 week (blocks)
            100e18  // proposalThreshold: 100 tokens
        )
        GovernorVotes(token)
        GovernorVotesQuorumFraction(4) // 4% quorum
        GovernorTimelockControl(timelock)
    {}

    // Required overrides omitted for brevity
    // Use OpenZeppelin Wizard to generate complete implementation
}
```

## ERC-20 with Permit (EIP-2612)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity 0.8.28;

import {ERC20} from "@openzeppelin/contracts/token/ERC20/ERC20.sol";
import {ERC20Permit} from "@openzeppelin/contracts/token/ERC20/extensions/ERC20Permit.sol";
import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";

contract MyToken is ERC20, ERC20Permit, Ownable {
    constructor(address initialOwner)
        ERC20("MyToken", "MTK")
        ERC20Permit("MyToken")
        Ownable(initialOwner)
    {
        _mint(initialOwner, 1_000_000e18);
    }

    function mint(address to, uint256 amount) external onlyOwner {
        _mint(to, amount);
    }
}

// Usage: gasless approve via signature
// 1. User signs permit off-chain (EIP-712)
// 2. Anyone can submit permit(owner, spender, value, deadline, v, r, s)
// 3. Approval set without user paying gas
```
