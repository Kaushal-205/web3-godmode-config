---
paths: "**/*.sol"
---

## Solidity Coding Standards

### Pragma
- Pin exact version for deployments: `pragma solidity 0.8.28;`
- No floating pragma (`^`) in production contracts

### Naming Conventions
- PascalCase for contracts, structs, enums, events, errors
- camelCase for functions, variables, modifiers
- SCREAMING_SNAKE_CASE for constants and immutables
- `I` prefix for interfaces: `IVault`, `IERC20`
- `_` prefix for internal/private functions and variables

### Documentation (NatSpec)
- `@notice` on all public/external functions (user-facing description)
- `@param` for every parameter
- `@return` for every return value
- `@dev` for implementation notes
- `@custom:` for custom annotations

### CEI Pattern — NON-NEGOTIABLE
All functions with external calls MUST follow Checks-Effects-Interactions:
1. **Checks**: Validate inputs, permissions, state
2. **Effects**: Update contract state
3. **Interactions**: External calls (last)

### Errors
- Use custom errors over require strings (cheaper gas)
- Name errors descriptively: `InsufficientBalance`, not `Error1`
- Include relevant parameters: `error InsufficientBalance(uint256 available, uint256 required)`

### Events
- Emit for EVERY state change
- Index up to 3 params for filtering (addresses, IDs)
- Past tense naming: `Deposited`, `Withdrawn`, `Transferred`

### Access Control
- Never use `tx.origin` — always `msg.sender`
- Use `Ownable2Step` over `Ownable` for safe ownership transfer
- Consider timelock for critical admin functions

### Function Ordering
```
external -> public -> internal -> private
Within each: state-changing before view/pure
```

### Security
- Invoke `/solidity-security` skill before writing Solidity
- Invoke `/smart-contract-audit` before deployment
