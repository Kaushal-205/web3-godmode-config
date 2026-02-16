---
paths: "**/*.sol, foundry.toml"
---

## Foundry Rules

### General Commands
```bash
forge build          # Compile contracts
forge test           # Run tests
forge test -vvvv     # Verbose traces
forge script         # Run deployment scripts
forge verify-contract # Verify on explorer
```

### Chain Configuration

| Chain | ID | RPC | Explorer | Verify URL |
|-------|-----|-----|----------|------------|
| Ethereum | 1 | https://eth.llamarpc.com | https://etherscan.io | https://api.etherscan.io/api |
| Base | 8453 | https://mainnet.base.org | https://basescan.org | https://api.basescan.org/api |
| Arbitrum | 42161 | https://arb1.arbitrum.io/rpc | https://arbiscan.io | https://api.arbiscan.io/api |
| Arbitrum Sepolia | 421614 | https://sepolia-rollup.arbitrum.io/rpc | https://sepolia.arbiscan.io | https://api-sepolia.arbiscan.io/api |
| Optimism | 10 | https://mainnet.optimism.io | https://optimistic.etherscan.io | https://api-optimistic.etherscan.io/api |
| Polygon | 137 | https://polygon-rpc.com | https://polygonscan.com | https://api.polygonscan.com/api |
| Abstract | 2741 | https://api.mainnet.abs.xyz | https://abscan.org | https://api.abscan.org/api |
| Abstract Testnet | 11124 | https://api.testnet.abs.xyz | https://sepolia.abscan.org | https://api-sepolia.abscan.org/api |
| Monad Testnet | 10143 | https://testnet-rpc.monad.xyz | https://testnet.monadexplorer.com | — |
| MegaETH Testnet | 6342 | https://carrot.megaeth.com/rpc | https://megaexplorer.xyz | — |

### Abstract (ZKsync-based)
Abstract requires `foundry-zksync`. **Always** include `--zksync` flag:
```bash
forge build --zksync
forge test --zksync
forge script script/Deploy.s.sol --zksync --rpc-url https://api.testnet.abs.xyz --broadcast
```

### Deployment Rules
- **Environment variables** for private keys: `--private-key $DEPLOYER_KEY`
- **Never hardcode** private keys or RPC URLs in scripts
- **Verify after deploy**: `forge verify-contract <addr> <Contract> --chain <id> --verifier-url <url>`
- **Mainnet**: Use `--slow` flag to avoid nonce issues
- **Simulation first**: Run without `--broadcast` to simulate
- **Multi-sig**: For mainnet, prefer multi-sig deployment (Safe, Gnosis)

### foundry.toml Template
```toml
[profile.default]
src = "src"
out = "out"
libs = ["lib"]
solc_version = "0.8.28"
optimizer = true
optimizer_runs = 200
via_ir = false

[rpc_endpoints]
mainnet = "${ETH_RPC_URL}"
base = "${BASE_RPC_URL}"
arbitrum = "${ARB_RPC_URL}"
arbitrum_sepolia = "${ARB_SEPOLIA_RPC_URL}"
abstract_mainnet = "https://api.mainnet.abs.xyz"
abstract_testnet = "https://api.testnet.abs.xyz"

[etherscan]
mainnet = { key = "${ETHERSCAN_API_KEY}" }
base = { key = "${BASESCAN_API_KEY}", url = "https://api.basescan.org/api" }
arbitrum = { key = "${ARBISCAN_API_KEY}", url = "https://api.arbiscan.io/api" }
arbitrum_sepolia = { key = "${ARBISCAN_API_KEY}", url = "https://api-sepolia.arbiscan.io/api", chain = 421614 }
abstract_mainnet = { key = "${ABSCAN_API_KEY}", url = "https://api.abscan.org/api", chain = 2741 }
```
