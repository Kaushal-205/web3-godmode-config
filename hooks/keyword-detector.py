#!/usr/bin/env python3
"""
Keyword Detector Hook for Claude Code
Detects special keywords and injects mode-specific context.
10 modes: ultrawork, search, analyze, think, refactor, review, test, optimize, secure, deploy
"""

import json
import sys
import re


MODES = {
    # Original modes
    "ultrawork": {
        "pattern": r"\b(ultrawork|ulw|ultra\s*work)\b",
        "context": """[ULTRAWORK MODE ACTIVATED]

Execute with maximum capability:

1. **Parallel Execution**: Launch multiple agents/tools simultaneously
2. **Comprehensive Planning**: Create detailed todo list BEFORE starting
3. **Thorough Verification**: Run diagnostics on all changed files
4. **No Premature Stopping**: Continue until ALL tasks complete
5. **Evidence-Based**: Verify each change works correctly

Workflow:
- Use Task tool to delegate to specialized agents (explore, oracle)
- Launch independent searches in parallel
- Create todos for complex multi-step work
- Mark todos complete only after verification"""
    },

    "search": {
        "pattern": r"\b(search|find|locate|where\s+is)\b",
        "context": """[SEARCH MODE ACTIVATED]

Maximize search thoroughness:

1. **Parallel Searches**: Launch multiple search operations simultaneously
2. **Multiple Angles**: Search by name, content, pattern, and structure
3. **Cross-Reference**: Verify findings across multiple sources
4. **Exhaustive**: Don't stop at first result - find ALL matches

Tools to use in parallel:
- Grep for text patterns
- Glob for file patterns
- LSP for symbol definitions/references
- Git for history when relevant

Report:
- All matching files with absolute paths
- Relevance explanation for each match
- Confidence level in completeness"""
    },

    "analyze": {
        "pattern": r"\b(analyze|investigate|debug|diagnose)\b",
        "context": """[ANALYSIS MODE ACTIVATED]

Deep investigation protocol:

1. **Gather Evidence**: Read all relevant files before forming conclusions
2. **Multi-Phase Analysis**:
   - Phase 1: Surface-level scan
   - Phase 2: Deep dive into suspicious areas
   - Phase 3: Cross-reference and validate
3. **Consult Experts**: Use oracle agent for complex reasoning
4. **Document Findings**: Systematic, evidence-based conclusions

For debugging:
- Check recent changes (git log, git blame)
- Trace data flow through the system
- Identify edge cases and error paths
- Propose hypothesis and test it"""
    },

    "think": {
        "pattern": r"\b(think\s*(deeply|hard|carefully))\b",
        "context": """[EXTENDED THINKING MODE]

Take time for thorough reasoning:

1. **Step Back**: Consider the broader context and implications
2. **Multiple Perspectives**: Evaluate different approaches
3. **Trade-off Analysis**: Document pros/cons of each option
4. **Risk Assessment**: Identify potential issues before implementing
5. **Validation Plan**: How will we verify success?

Before acting:
- State your understanding of the problem
- List assumptions being made
- Outline the approach with rationale
- Identify potential failure modes"""
    },

    # New modes
    "refactor": {
        "pattern": r"\b(refactor|restructure|reorganize|clean\s*up)\b",
        "context": """[REFACTOR MODE ACTIVATED]

Refactoring discipline:

1. **Assess First**: Understand existing patterns before changing them
2. **Incremental Changes**: Small, verifiable steps - never big-bang
3. **Behavior Preservation**: Tests must pass after EVERY step
4. **No Feature Work**: Refactoring and features are separate commits
5. **Document Why**: Note what pattern you're moving toward

Workflow:
- Run existing tests first (establish baseline)
- Make one structural change at a time
- Verify tests pass after each change
- If no tests exist, write characterization tests FIRST"""
    },

    "review": {
        "pattern": r"\b(review\s+(this|my|the|code|pr)|code\s*review)\b",
        "context": """[REVIEW MODE ACTIVATED]

Route to appropriate reviewer:

- **TypeScript/React**: Use kieran-typescript-reviewer (compound)
- **Solidity/.sol**: Use security-sentinel + solidity-security skill
- **Rust/.rs**: Use rust-patterns skill + manual review
- **Rails/Ruby**: Use kieran-rails-reviewer (compound)
- **Python**: Use kieran-python-reviewer (compound)
- **Architecture**: Use architecture-strategist (compound)
- **PR Review**: Use /pr-review-toolkit:review-pr skill

Review checklist:
- Type safety, error handling, edge cases
- Naming clarity, code shape, single responsibility
- Security implications (especially web3)
- Test coverage for changes"""
    },

    "test": {
        "pattern": r"\b(write\s+tests?|add\s+tests?|test\s+this|testing)\b",
        "context": """[TEST MODE ACTIVATED]

Testing standards:

1. **BDD Structure**: Use #given, #when, #then comments
2. **Edge Cases**: Empty, null, boundary, concurrent, network-down
3. **One assertion per test** (logical, not literal)
4. **Mock external deps** only - never mock the unit under test
5. **Descriptive names**: Test name explains the scenario

For Solidity:
- Use forge test with -vvvv for traces
- Fuzz testing for numeric inputs
- Fork testing for mainnet state
- Invariant testing for protocol properties

For React:
- Test behavior, not implementation
- Use testing-library patterns
- Test user interactions, not component internals"""
    },

    "optimize": {
        "pattern": r"\b(optimize|performance|speed\s*up|slow|gas\s*optim)\b",
        "context": """[OPTIMIZE MODE ACTIVATED]

Performance analysis:

For **TypeScript/React**:
- Route to performance-oracle (compound) for profiling
- Check vercel-react-best-practices rules
- Bundle size, re-renders, waterfall elimination

For **Solidity** (gas optimization):
- Invoke /solidity-security skill (gas-optimization.md)
- Storage packing, calldata vs memory, custom errors
- Cache storage reads, batch operations
- Use unchecked blocks where overflow is impossible

For **Rust**:
- Profile before optimizing (cargo flamegraph)
- Minimize allocations, use references
- Iterator chains over manual loops"""
    },

    "secure": {
        "pattern": r"\b(security|audit|vulnerab|exploit|attack|reentrancy)\b",
        "context": """[SECURITY MODE ACTIVATED]

Security analysis:

For **Solidity (.sol)**:
- Invoke /solidity-security skill immediately
- Check: reentrancy, access control, integer safety, oracle manipulation
- Check: flash loan vectors, delegate call risks, storage collision
- Route to security-sentinel (compound) for deep scan

For **General code**:
- Route to security-sentinel (compound)
- OWASP Top 10 checks
- Input validation, injection vectors
- Authentication/authorization review
- Secrets scanning (no hardcoded keys/passwords)

For **Web3 Frontend**:
- Signature request validation
- Transaction simulation before signing
- Phishing vector analysis"""
    },

    "deploy": {
        "pattern": r"\b(deploy|deployment|mainnet|testnet|going\s+live)\b",
        "context": """[DEPLOY MODE ACTIVATED]

Deployment protocol:

1. **Chain Awareness**: Confirm target chain before proceeding
2. **Pre-deploy Checklist**:
   - All tests passing
   - Invoke /smart-contract-audit for Solidity
   - Constructor args verified
   - Proxy implementation correct (if upgradeable)
3. **Deploy Steps**:
   - Simulate without --broadcast first
   - Use --slow for mainnet
   - Verify on explorer immediately after
4. **Post-deploy**:
   - Verify initial state is correct
   - Run integration tests against deployed contract
   - Transfer ownership to multi-sig (mainnet)

Invoke /deploy-check command for structured verification."""
    },
}


def main():
    try:
        input_data = json.load(sys.stdin)
    except json.JSONDecodeError:
        sys.exit(0)

    prompt = input_data.get("prompt", "").lower()

    # Check all modes, collect all matches (first match wins for context injection)
    for mode_name, mode_config in MODES.items():
        if re.search(mode_config["pattern"], prompt):
            output = {
                "hookSpecificOutput": {
                    "hookEventName": "UserPromptSubmit",
                    "additionalContext": mode_config["context"].strip()
                }
            }
            print(json.dumps(output))
            sys.exit(0)

    # Skill reminder on session-start-like prompts
    if re.search(r"\b(start|begin|let'?s\s+go|ready|new\s+project)\b", prompt):
        reminder = """[SKILL REMINDER]
Available skills for this session: /rigorous-coding, /solidity-security, /rust-patterns,
/web3-frontend, /web3-foundry, /web3-hardhat, /web3-privy, /smart-contract-audit,
/react-useeffect, /vercel-react-best-practices, /planning-with-files, /interview,
/web3-eip-reference, /web3-solana-simd, /web3-monad, /web3-megaeth, /web3-solidity-patterns.
Invoke the relevant skill before writing code in that domain."""
        output = {
            "hookSpecificOutput": {
                "hookEventName": "UserPromptSubmit",
                "additionalContext": reminder.strip()
            }
        }
        print(json.dumps(output))

    sys.exit(0)


if __name__ == "__main__":
    main()
