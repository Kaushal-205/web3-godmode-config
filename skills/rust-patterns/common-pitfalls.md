# Anchor/Solana Common Pitfalls

## Missing Signer Check
```rust
// BAD: No signer verification — anyone can call
#[derive(Accounts)]
pub struct Withdraw<'info> {
    #[account(mut)]
    pub vault: Account<'info, Vault>,
    pub authority: AccountInfo<'info>,  // NOT verified as signer
}

// GOOD: Signer type enforces signature
#[derive(Accounts)]
pub struct Withdraw<'info> {
    #[account(mut, has_one = authority)]
    pub vault: Account<'info, Vault>,
    pub authority: Signer<'info>,  // Must sign transaction
}
```

## Missing Owner Check
```rust
// BAD: Account could be owned by any program
pub vault: AccountInfo<'info>,

// GOOD: Account<'info, T> auto-validates program ownership
pub vault: Account<'info, Vault>,
```

## PDA Bump Canonicalization
```rust
// BAD: User-supplied bump — attacker can use non-canonical bump
pub fn init(ctx: Context<Init>, bump: u8) -> Result<()> {
    ctx.accounts.pda.bump = bump;  // Could be non-canonical
    Ok(())
}

// GOOD: Let Anchor find canonical bump
#[account(
    seeds = [b"vault", user.key().as_ref()],
    bump,  // Anchor stores canonical bump
)]
pub vault: Account<'info, Vault>,
```

## Arithmetic Overflow in Token Math
```rust
// BAD: Can overflow with large token amounts
let fee = amount * fee_rate / 10000;

// GOOD: Use checked math
let fee = amount
    .checked_mul(fee_rate)
    .ok_or(ErrorCode::MathOverflow)?
    .checked_div(10000)
    .ok_or(ErrorCode::MathOverflow)?;

// ALSO GOOD: u128 intermediate for precision
let fee = (amount as u128)
    .checked_mul(fee_rate as u128)
    .ok_or(ErrorCode::MathOverflow)?
    .checked_div(10000)
    .ok_or(ErrorCode::MathOverflow)? as u64;
```

## Reinitialization Attack
```rust
// BAD: Can be called again to reset state
pub fn initialize(ctx: Context<Initialize>) -> Result<()> {
    let account = &mut ctx.accounts.my_account;
    account.authority = ctx.accounts.authority.key();
    account.balance = 0;
    Ok(())
}

// GOOD: Use init constraint (fails if already initialized)
#[account(
    init,  // Anchor checks account is uninitialized
    payer = authority,
    space = 8 + MyAccount::INIT_SPACE,
)]
pub my_account: Account<'info, MyAccount>,

// ALSO GOOD: Manual guard with discriminator
// Anchor's `init` already handles this via account discriminator
```

## Duplicate Mutable Accounts
```rust
// BAD: Same account passed as both from and to
pub fn transfer(ctx: Context<Transfer>) -> Result<()> {
    // If from == to, amount gets doubled
    ctx.accounts.from.balance -= amount;
    ctx.accounts.to.balance += amount;
    Ok(())
}

// GOOD: Validate accounts are different
#[account(
    mut,
    constraint = from.key() != to.key() @ ErrorCode::DuplicateAccounts,
)]
pub from: Account<'info, TokenVault>,
```

## Account Confusion (Wrong Account Type)
```rust
// BAD: Accepting generic AccountInfo for typed operation
pub fn process(ctx: Context<Process>) -> Result<()> {
    let data = ctx.accounts.token_account.try_borrow_data()?;
    // Manual deserialization — error-prone
}

// GOOD: Use typed accounts
pub token_account: Account<'info, TokenAccount>,
// Anchor validates: correct program owner, valid deserialization
```

## Closeable Account Vulnerability
```rust
// BAD: Closed account can be resurrected
pub fn close_account(ctx: Context<CloseAccount>) -> Result<()> {
    let account = &ctx.accounts.my_account;
    **ctx.accounts.recipient.lamports.borrow_mut() += account.to_account_info().lamports();
    **account.to_account_info().lamports.borrow_mut() = 0;
    // Data not zeroed — account can be re-opened
}

// GOOD: Use Anchor's close constraint
#[account(
    mut,
    close = recipient,  // Zeros data, transfers lamports, sets discriminator
    has_one = authority,
)]
pub my_account: Account<'info, MyAccount>,
```

## Missing Rent Exemption Check
```rust
// Anchor handles this automatically with `init`
// But if manually creating accounts:
let required_lamports = Rent::get()?.minimum_balance(space);
// Ensure account has enough lamports to be rent-exempt
```
