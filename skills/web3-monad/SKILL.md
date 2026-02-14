---
name: web3-monad
description: Monad L1 blockchain reference. Use when deploying to Monad, building on Monad, or needing Monad-specific architecture details. Covers MonadBFT, parallel execution, EVM compatibility, and deployment patterns.
---

# Monad L1 Reference

## Overview

Monad is a high-performance EVM-compatible L1 blockchain featuring:
- **MonadBFT**: Pipelined HotStuff-based consensus
- **Parallel execution**: Optimistic parallel transaction execution
- **MonadDb**: Custom database for blockchain state
- **10,000+ TPS** with 1-second block times
- **Full EVM bytecode compatibility** — deploy existing Solidity as-is

## Key Architecture

### MonadBFT Consensus
- Pipelined BFT consensus (process multiple blocks simultaneously)
- Single-slot finality
- Leader rotation for fairness

### Parallel Execution
- Transactions execute optimistically in parallel
- Conflicts detected and re-executed serially
- Most transactions don't conflict, achieving near-linear speedup
- **No changes needed in your Solidity code** — parallelism is at runtime level

### MonadDb
- Custom storage engine optimized for blockchain access patterns
- Async I/O for non-blocking state reads
- Merkle trie with efficient proof generation

## Chain Configuration

| Property | Testnet |
|----------|---------|
| Name | Monad Testnet |
| Chain ID | 10143 |
| RPC URL | https://testnet-rpc.monad.xyz |
| WebSocket | wss://testnet-rpc.monad.xyz |
| Explorer | https://testnet.monadexplorer.com |
| Currency | MON |
| Faucet | https://faucet.monad.xyz |

## Deployment

### Standard EVM Tooling Works
Monad is EVM bytecode compatible. Use Foundry, Hardhat, or any EVM toolchain.

```bash
# Foundry
forge script script/Deploy.s.sol --rpc-url https://testnet-rpc.monad.xyz --broadcast

# Hardhat
npx hardhat run scripts/deploy.ts --network monad
```

### hardhat.config.ts
```typescript
networks: {
  monad: {
    url: "https://testnet-rpc.monad.xyz",
    chainId: 10143,
    accounts: [process.env.DEPLOYER_KEY!],
  },
}
```

### foundry.toml
```toml
[rpc_endpoints]
monad_testnet = "https://testnet-rpc.monad.xyz"
```

### viem Chain Definition
```typescript
import { defineChain } from "viem"

export const monadTestnet = defineChain({
  id: 10143,
  name: "Monad Testnet",
  nativeCurrency: { name: "MON", symbol: "MON", decimals: 18 },
  rpcUrls: {
    default: { http: ["https://testnet-rpc.monad.xyz"] },
  },
  blockExplorers: {
    default: { name: "Monad Explorer", url: "https://testnet.monadexplorer.com" },
  },
})
```

## Performance Considerations

### What's Different from Ethereum
- **Block time**: 1 second (vs 12 seconds on Ethereum)
- **Throughput**: 10,000+ TPS (vs ~30 TPS on Ethereum)
- **Finality**: Single-slot (vs ~12 minutes on Ethereum)
- **Gas costs**: Significantly lower due to higher throughput

### What's the Same
- EVM opcodes (Solidity compiles identically)
- Transaction format (same as Ethereum)
- Contract addresses (same derivation)
- Standard RPC methods (eth_*)

### Parallel Execution Impact
- Contracts that access independent state parallelize naturally
- Contracts competing for the same storage slots may serialize
- Design for independent state when possible (per-user mappings vs global counters)
- No code changes required — just awareness of access patterns

## Smart Contract Tips

- **Gas optimization still matters** — even though gas is cheaper, optimize for users
- **Same security model** — all Solidity security best practices apply
- **Block time awareness** — 1-second blocks mean `block.timestamp` granularity differs
- **High throughput means more MEV opportunity** — consider MEV protection
