---
paths: "**/*.rs"
---

## Rust Coding Standards

### Naming
- snake_case for functions, variables, modules, crate names
- PascalCase for types, traits, enum variants
- SCREAMING_SNAKE_CASE for constants and statics
- Prefix unused variables with `_`

### Error Handling
- Use `thiserror` for library errors (typed, specific)
- Use `anyhow` for application errors (convenient context)
- Never `unwrap()` or `expect()` in production code
- Use `?` operator for propagation
- Add context: `.context("failed to parse config")?`

### Function Design
- Prefer `&str` over `String` for input parameters
- Prefer `&[T]` over `Vec<T>` for input parameters
- Return owned types (`String`, `Vec<T>`) from functions
- Use `impl Trait` for return types when concrete type is irrelevant

### Patterns
- Prefer iterators over manual loops
- Use `match` exhaustively — no catch-all `_` unless intentional
- Derive common traits: `Debug`, `Clone`, `PartialEq`, `Eq`
- Use `#[must_use]` on functions whose return values shouldn't be ignored
- Prefer `if let` / `let else` over `match` for single-pattern cases

### Anchor/Solana
- When writing Anchor programs, invoke `/rust-patterns` skill
- Validate all account constraints (`has_one`, `seeds`, `signer`)
- Use canonical PDA bumps (never accept user-supplied bumps)
- Use checked math for token amounts
