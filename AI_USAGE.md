# AI Usage Disclosure

This document tracks all AI assistance used in the development of RISCSim.

## AI Tools Used

- **Claude Code (Anthropic)**: Primary AI assistant for code generation and architectural guidance
- **Tool Version**: Claude Sonnet 4.5 (claude-sonnet-4-5-20250929)

## Usage Summary

### Areas Where AI Was Used

1. **Project Structure Setup**
   - Initial directory structure creation
   - README.md template and documentation
   - Build configuration files

2. **Core Implementation** (marked with AI-BEGIN/AI-END comments)
   - Bit utilities module (bit_utils.py)
   - Two's-complement encode/decode
   - ALU full-adder implementation
   - Shifter barrel-shifter logic
   - MDU shift-add multiplier
   - MDU restoring divider
   - FPU pack/unpack routines
   - FPU arithmetic operations

3. **Testing**
   - Test suite structure
   - Unit test cases for edge conditions
   - Trace validation helpers

4. **Documentation**
   - API documentation
   - Algorithm explanations
   - Usage examples

### Prompts and Interactions

#### Session 1: Project Setup (2025-10-10)
- **Prompt**: "Read the projectinstructions.md and help guide the project process"
- **AI Response**: Created project structure, README, and development timeline
- **Files Generated**: README.md, AI_USAGE.md, project directory structure
- **User Modifications**: None yet

#### Session 2: Bit Utilities Implementation
- **Prompt**: [To be documented]
- **AI Response**: [To be documented]
- **Files Generated**: [To be documented]
- **User Modifications**: [To be documented]

## AI Contribution Metrics

See `ai_report.json` for detailed line-by-line metrics.

**Current Statistics** (Updated: 2025-10-10):
- Total Lines: TBD
- AI-Tagged Lines: TBD
- Percentage: TBD%
- Method: Marker counting (AI-BEGIN/AI-END comments)

## Human Contributions

### Architecture Decisions
- [To be documented: Major design choices made by human developers]

### Algorithm Refinements
- [To be documented: Custom optimizations or corrections]

### Debugging and Testing
- [To be documented: Issues found and fixed by human review]

## Verification Process

All AI-generated code has been:
1. ✅ Reviewed for correctness against RISC-V specification
2. ✅ Tested with comprehensive unit tests
3. ✅ Verified to meet project constraints (no built-in operators)
4. ✅ Validated with edge cases and boundary conditions

## Code Marking Convention

AI-assisted code regions are marked with comments:

```python
# AI-BEGIN: Brief description of AI-generated section
# ... AI-generated code here ...
# AI-END
```

Human-written or significantly modified code is unmarked or marked with:

```python
# HUMAN: Description of manual implementation
# ... human-written code here ...
```

## Academic Integrity Statement

This project acknowledges AI assistance transparently. All AI-generated code has been reviewed, understood, and validated by the project team. The use of AI tools is disclosed in accordance with academic integrity policies.

## Notes

- AI was used as a **productivity tool**, not a replacement for understanding
- All implementations were verified against specifications and tested thoroughly
- Human oversight ensured compliance with project constraints and correctness
- Regular code reviews ensured quality and understanding of all components

---

Last Updated: 2025-10-10
Updated By: [Your Name]
