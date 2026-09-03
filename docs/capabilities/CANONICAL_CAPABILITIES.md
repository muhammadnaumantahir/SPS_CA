# SPS-CA Canonical Capability Baseline

CAP-001 through CAP-010 are the fixed Stage-0 capabilities. Each has one primary responsibility and one primary intent class.

| ID | Capability | Intent | Source effect |
|---|---|---|---|
| CAP-001 | Code Generation | `code_generation` | Creates/replaces requested source |
| CAP-002 | Code Modification | `code_modification` | Modifies existing source |
| CAP-003 | Code Explanation & Analysis | `analysis` | Read-only |
| CAP-004 | Bug Detection & Diagnosis | `bug_diagnosis` | Read-only |
| CAP-005 | Bug Fixing | `bug_fixing` | Corrects source |
| CAP-006 | Refactoring & Optimization | `refactoring` | Reworks source while preserving intent |
| CAP-007 | Test Generation | `test_generation` | Creates tests only |
| CAP-008 | Documentation Generation | `documentation` | Adds requested documentation |
| CAP-009 | Code Validation & Review | `validation` | Read-only validation/review |
| CAP-010 | Project/File Operations | `project_operations` | Plans file/project operations; mutation requires authorized execution |

## Request routing

The Brain infers programming language and classifies intent before capability selection. The model receives only eligible capabilities for the classified intent. Returned IDs are post-validated and corrected when a model proposes an ineligible capability.

Example: `write Python code to add, subtract, multiply and divide numbers; first ask how many numbers` → `code_generation` → **CAP-001**. It must never route to CAP-007.

Example: `generate pytest tests for this function` → `test_generation` → **CAP-007**.

Examples: `explain this code` → CAP-003; `find the bug` → CAP-004; `fix the bug` → CAP-005; `refactor this code` → CAP-006; `document this function` → CAP-008; `validate this code` → CAP-009.

## Evolution rule

CAP-001..CAP-010 are permanently reserved for the baseline. Generated capabilities start at CAP-011 and retain trigger evidence, provenance, parent lineage, validation evidence and historical migration references.

The former generated Parse Error Handler with historical ID CAP-010 is preserved as CAP-011.
