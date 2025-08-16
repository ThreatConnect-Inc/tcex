---
applyTo: tests/**/*.py
description: Guideline for Pytest Test Cases
---
# PYTEST CODING GUIDELINES

## OVERVIEW

This document contains ABSOLUTE MANDATORY instructions for creating Python Pytest test cases. These rules MUST be followed EXACTLY without any deviation, interpretation, or modification. Every instruction is precise and non-negotiable.

## 1. DOCUMENTATION RULES {#documentation-rules}

### 1.1 Module Docstring Requirements {#module-docstring-requirements}

#### 1.1.1 Update Instructions (MANDATORY)
- **MUST** If a well-structured module docstring matching existing rules exists, make NO changes and move on to next steps.
- **MUST** If docstring is minimal or lacks required sections, enhance it following the exact format specified in [Docstring Structure](#module-docstring-structure)
- **MUST** Only leave code unchanged if docstring already follows the complete format specified in [Docstring Structure](#module-docstring-structure)

#### 1.1.2 Docstring Structure (MANDATORY) {#module-docstring-structure}
Every module docstring MUST follow this EXACT format with NO VARIATIONS:

```python
"""[Class Name] for [Purpose].

[Detailed description of what the module represents and its purpose in the system.]

Classes:
    [Class Name]: [Purpose]

TcEx Module Tested: [TcEx Module Name]
"""
```

#### 1.1.3 Restrictions (MANDATORY)
- **MUST NOT** use `Example:` section in docstring.

### 1.2 Class Docstring Requirements {#class-docstring-requirements}

#### 1.2.1 Update Instructions (MANDATORY)
- **MUST** If a well-structured class docstring matching existing rules exists, make NO changes and move on to next steps.
- **MUST** If docstring is minimal or lacks required sections, enhance it following the exact format specified in [Docstring Structure](#class-docstring-structure)
- **MUST** Only leave code unchanged if docstring already follows the complete format specified in [Docstring Structure](#class-docstring-structure)

#### 1.2.2 Docstring Structure (MANDATORY) {#class-docstring-structure}
Every class docstring MUST follow this EXACT format with NO VARIATIONS:

```python
class ClassName(EndpointBase):
    """[Class Name] for [Purpose].

    [Detailed description of what the class represents and its purpose in the system.]

    Fixtures:
        [Fixture Name]: [Purpose of the fixture]
    """
```

#### 1.2.3 Restrictions (MANDATORY)
- **MUST NOT** use `Example:` section in docstring.

#### 1.2.4 Attribute Section (OPTIONAL)
- **MUST** add `Attribute:` section if defined in [Docstring Structure](#class-docstring-structure)

#### 1.2.5 Usage Section (OPTIONAL)
- **MUST** add `Usage:` section if defined in [Docstring Structure](#class-docstring-structure)

## 2. IMPORT RULES {#import-rules}

### 2.1 Import Sorting
- **Important** import sorting is handled by [Ruff](https://docs.astral.sh/ruff/) during [Formatting and Linting](#formatting-and-linting-rules)

### 2.2 Bottom of File Import
- **MUST** leave existing imports, that are at the bottom of the file, at the bottom of the file

## 3. CLASS RULES {#class-rules}

### 3.1 Class Structure Requirements
- **MUST** follow PEP 8 class naming conventions (PascalCase)
- **MUST** include proper type hints for all methods
- **MUST** implement `__init__` method with proper parameter documentation
- **MUST** use descriptive method names that clearly indicate functionality

### 3.2 Class Documentation
- **MUST** include comprehensive docstrings for all public methods
- **MUST** document all parameters, return values, and exceptions
- **MUST** provide usage examples in docstrings when appropriate

### 3.3 Style Requirements
- **MUST** use a line length of 100 characters for all code
- **MUST** use a line length of 100 characters for all docstrings
- **MUST** use a line length of 100 characters for all comments

## 4. GENERAL CODE RULES {#general-code-rules}

### 4.1 Update Instructions (MANDATORY)
- **MUST** If a well-structured code matching existing rules exists, make NO changes and move on to next steps.
- **MUST** If code is minimal or lacks required feature, enhance it following the exact format specified in section [General Code Rules](#general-code-rules) AND [Custom Code Rules](#custom-code-rules)
- **MUST** Only leave code unchanged if the code already follows the complete format specified in [General Code Rules](#general-code-rules) AND [Custom Code Rules](#custom-code-rules)
- **MUST** When making code changes to existing code, make minimal change to address bugs, security issues, or explicit instructions provided in prompt

### 4.3 Typing Hints

### 4.3.1 Method Signature Argument Type Hints (MANDATORY)
- **MUST** ensure ALL method arguments have proper type hints
- **MUST** use appropriate types for all parameters (e.g., `int`, `str`, `bool`, custom types)
- **MUST** use `| None` for optional parameters
- **MUST** use proper return type annotations (e.g., `-> None`, `-> str`, etc.)

### 4.3.1 Method Return Type Hints (MANDATORY)
- **MUST** ensure ALL method return types are properly annotated
- **MUST** use appropriate return types for all methods (e.g., `-> None`, `-> str`, etc.)

## 5. CUSTOM CODE RULES (MANDATORY) {#custom-code-rules}

### 5.1 Existing Files - MANDATORY REQUIREMENTS
- **MUST** code changes are only allowed if absolutely required
- **MUST** any security issues in the code should still be addressed
- **MUST** any bug in the code issues should still be addressed

### 5.2 Method Docstring
- **MUST** include a well structured docstring for all methods
- **MUST** provide details of the test case in docstring
- **MUST** list out fixtures in docstring

## 5.3 Pytest Mark Parametrize
- **MUST** use `pytest.param` for all `@pytest.mark.parametrize` usage
- **MUST** use a valid `id` for `pytest.param` that is prefix with `pass` or `fail` dependent on if the test is intended to pass
- **MUST NOT** use tuples for `@pytest.mark.parametrize` inputs

## 6. FORMATTING AND LINTING RULES (MANDATORY) {#formatting-and-linting-rules}

**IMPORTANT** After ALL edits are COMPLETE formatting and linting should be handled by ruff.

### 6.1 Formatting Files
- **MUST** run `uv run ruff format [filename]`

### 6.2 Linting Files
- **MUST** run `uv run ruff check --fix [filename]`

### 6.3 Quote Fixer
- **MUST** run `uv run pre-commit run double-quote-string-fixer --files [filename]`

## 7. VALIDATION CHECKLIST (MANDATORY)

- **MUST** Before submitting and change, verify all the following validations.

### 7.1 Documentation Guidelines Validation
Validation rules applicable to [Documentation Rules](#documentation-rules)

- [ ] Module docstring are only changed when the structure is NOT well defined according to [Module Docstring Structure](#module-docstring-structure)
- [ ] Class docstring are only changed when the structure is NOT well defined according to [Class Docstring Structure](#class-docstring-structure)
- [ ] Module docstring matches structure defined in [Module Docstring Structure](#module-docstring-structure)
- [ ] Class docstring matches structure defined in [Class Docstring Structure](#class-docstring-structure)
- [ ] Endpoint class inherits from appropriate base class

### 7.2 Import Validation
Validation rules applicable to [Import Rules](#import-rules)

### 7.3 Class Guideline Validation
Validation rules applicable to [Class Rules](#class-rules)

### 7.4 General Code Validation
Validation rules applicable to [General Code Rules](#general-code-rules)

- [ ] Code changes are only made if absolutely required (security/bug fixes)
- [ ] Existing well-structured code is preserved without modification
- [ ] Bug issues are addressed when present
- [ ] Security issues are addressed when present see [Security Validation](#security-validation)
- [ ] All method signatures have proper type hinting

#### 7.4.2 Error Handling {#error-handling}

- [ ] Exception logging is used where appropriate
- [ ] Exception variable is `ex` in all cases
- [ ] Exception message is passed in as `ex_msg`

#### 7.4.3 Security Validation {#security-validation}

- [ ] All inputs are validated

### 7.5 Custom Code Validation
Validation rules applicable to [Custom Code Rules](#custom-code-rules)

### 7.6 Formatting and Linting Validation
Validation rules applicable to [Formatting and Linting Rules](#formatting-and-linting-rules)

- [ ] Ruff formatting and Linting is complete and passing

## 8. VIOLATION CONSEQUENCES (MANDATORY)

Any deviation from these rules results in:
1. **Immediate code rejection**
2. **Mandatory rewrite following exact specifications**
3. **No exceptions or interpretations allowed**
4. **Zero tolerance for "creative" solutions**

## 9. ENFORCEMENT MECHANISM (MANDATORY)

- **Automated linting**: All code MUST pass ruff check and ruff format
- **Manual review**: Every line checked against these exact specifications
- **Continuous monitoring**: Regular audits to ensure compliance
- **Immediate correction**: Violations fixed within 24 hours

**COMPLIANCE IS MANDATORY. NO EXCEPTIONS.**
