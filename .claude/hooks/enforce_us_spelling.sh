#!/usr/bin/env bash
#
# PreToolUse hook for Write | Edit | NotebookEdit — rejects file content that
# contains British (en-GB) spellings, enforcing American English (US) spelling.
#
# Stdin: a JSON envelope. The text being written is read from (in order):
#   .tool_input.content       (Write)
#   .tool_input.new_string    (Edit)
#   .tool_input.new_source    (NotebookEdit)
# Exit codes:
#   0  = allow the tool call
#   2  = block the tool call; stderr is shown to the model so it can correct
#
# Rationale: $CLAUDE_PROJECT_DIR/CLAUDE.md → "Style and Language Conventions"
# requires US spelling for all natural-language output, code comments, and docs.
#
# Design note: this uses an explicit British→US WORD DENYLIST matched on word
# boundaries — NOT the -ise/-our/-re/ll *patterns*, which false-positive on
# legitimate US words (rise, hour, future, ball, expertise, parameter, ...).
# Keep the denylist clearly-British only to avoid noise.
#
# Override: to intentionally keep a British token (e.g. an external API field
# you cannot rename), this hook is skipped for its own denylist file; for other
# files, temporarily disable the hook in settings.local.json.

set -euo pipefail

PAYLOAD="$(cat)"
CONTENT="$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.content // .tool_input.new_string // .tool_input.new_source // ""')"
FILE_PATH="$(printf '%s' "$PAYLOAD" | jq -r '.tool_input.file_path // .tool_input.notebook_path // ""')"
TOOL="$(printf '%s' "$PAYLOAD" | jq -r '.tool_name // "edit"')"

# Nothing to check.
[ -z "$CONTENT" ] && exit 0

# Skip this hook's own denylist file (it necessarily contains British words).
case "$FILE_PATH" in
    */enforce_us_spelling.sh) exit 0 ;;
esac

# British (key) → American (value). Lowercase keys; word-boundary matched.
declare -A SPELL=(
    # -our → -or
    [colour]=color [colours]=colors [coloured]=colored [colouring]=coloring
    [behaviour]=behavior [behaviours]=behaviors [behavioural]=behavioral
    [favour]=favor [favours]=favors [favoured]=favored [favourite]=favorite
    [favourites]=favorites [favourable]=favorable [flavour]=flavor [flavours]=flavors
    [honour]=honor [labour]=labor [neighbour]=neighbor [neighbours]=neighbors
    [neighbouring]=neighboring [rumour]=rumor [harbour]=harbor [odour]=odor
    [vapour]=vapor [savour]=savor [endeavour]=endeavor
    # -ise → -ize (clearly-British verbs + inflections)
    [organise]=organize [organised]=organized [organising]=organizing
    [organisation]=organization [organisations]=organizations
    [realise]=realize [realised]=realized [realising]=realizing
    [recognise]=recognize [recognised]=recognized [recognising]=recognizing
    [analyse]=analyze [analysed]=analyzed [analysing]=analyzing [analyser]=analyzer
    [initialise]=initialize [initialised]=initialized [initialising]=initializing
    [initialisation]=initialization
    [normalise]=normalize [normalised]=normalized [normalising]=normalizing
    [normalisation]=normalization
    [serialise]=serialize [serialised]=serialized [serialising]=serializing
    [serialisation]=serialization [deserialise]=deserialize [deserialised]=deserialized
    [customise]=customize [customised]=customized [customising]=customizing
    [customisation]=customization
    [optimise]=optimize [optimised]=optimized [optimising]=optimizing
    [optimisation]=optimization
    [summarise]=summarize [summarised]=summarized [summarising]=summarizing
    [authorise]=authorize [authorised]=authorized [authorising]=authorizing
    [authorisation]=authorization
    [synchronise]=synchronize [synchronised]=synchronized [synchronising]=synchronizing
    [prioritise]=prioritize [prioritised]=prioritized [prioritising]=prioritizing
    [categorise]=categorize [categorised]=categorized [categorising]=categorizing
    [finalise]=finalize [finalised]=finalized [finalising]=finalizing
    [minimise]=minimize [minimised]=minimized [minimising]=minimizing
    [maximise]=maximize [maximised]=maximized [maximising]=maximizing
    [standardise]=standardize [standardised]=standardized
    [centralise]=centralize [centralised]=centralized
    [capitalise]=capitalize [capitalised]=capitalized
    [utilise]=utilize [utilised]=utilized [utilising]=utilizing
    [emphasise]=emphasize [emphasised]=emphasized
    [specialise]=specialize [specialised]=specialized
    [characterise]=characterize [characterised]=characterized
    # -re → -er
    [centre]=center [centres]=centers [centred]=centered [centring]=centering
    [metre]=meter [metres]=meters [litre]=liter [litres]=liters
    [theatre]=theater [fibre]=fiber [fibres]=fibers [calibre]=caliber [sabre]=saber
    # British double-l → US single-l (inflections only)
    [cancelled]=canceled [cancelling]=canceling
    [travelled]=traveled [travelling]=traveling [traveller]=traveler
    [labelled]=labeled [labelling]=labeling
    [modelled]=modeled [modelling]=modeling
    [signalled]=signaled [signalling]=signaling
    [fuelled]=fueled [fuelling]=fueling
    [counselled]=counseled [counselling]=counseling
    [levelled]=leveled [levelling]=leveling [marvelled]=marveled
    # British single-l → US double-l
    [enrol]=enroll [enrolment]=enrollment [fulfil]=fulfill [fulfilment]=fulfillment
    [instalment]=installment [skilful]=skillful [wilful]=willful
    # -ence → -ense
    [licence]=license [licences]=licenses [defence]=defense [offence]=offense
    [pretence]=pretense
    # -logue → -log
    [catalogue]=catalog [catalogues]=catalogs [catalogued]=cataloged
    # misc clearly-British
    [grey]=gray [programme]=program [artefact]=artifact [artefacts]=artifacts
    [practise]=practice [practised]=practiced [practising]=practicing
    [whilst]=while [cheque]=check [cheques]=checks [mould]=mold
    [sceptical]=skeptical [aluminium]=aluminum
)

# Single alternation; word-boundary, case-insensitive; collect unique matches.
PATTERN="$(IFS='|'; printf '%s' "${!SPELL[*]}")"
MATCHES="$(printf '%s' "$CONTENT" \
    | /opt/homebrew/opt/grep/libexec/gnubin/grep -iwoE "$PATTERN" 2>/dev/null \
    | /opt/homebrew/opt/coreutils/libexec/gnubin/tr '[:upper:]' '[:lower:]' \
    | /opt/homebrew/opt/coreutils/libexec/gnubin/sort -u || true)"

[ -z "$MATCHES" ] && exit 0

{
    printf '[enforce_us_spelling] BLOCKED: British (en-GB) spelling in %s (%s).\n\n' "$TOOL" "${FILE_PATH:-unknown}"
    printf 'Per %s/CLAUDE.md → "Style and Language Conventions": use\n' "${CLAUDE_PROJECT_DIR:-the project}"
    printf 'strict American English (US) spelling in code, comments, and docs.\n\n'
    printf 'Replace:\n'
    while IFS= read -r word; do
        [ -z "$word" ] && continue
        printf '  - %s → %s\n' "$word" "${SPELL[$word]:-<US form>}"
    done <<< "$MATCHES"
    printf '\nRe-issue the edit with the US spelling(s).\n'
} >&2

exit 2
