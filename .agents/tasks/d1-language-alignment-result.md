# Deliverable 1 — Telugu, Kannada, Malayalam Alignment Result

**Date:** 2025  
**Step:** D1 — Language Alignment  
**Outcome:** ✅ All changes applied — 120 backend tests pass

---

## Decision per Language

### Telugu (`te`) — Option A: Fully Aligned

Telugu is now fully aligned end-to-end.

| Layer | Before | After |
|---|---|---|
| `config.py` SUPPORTED_LANGUAGES default | `en,ta,hi` | `en,ta,hi,te,kn,ml` |
| `interview_session.py` SUPPORTED_LANGUAGES set | `{"en","ta","hi","es","fr","de","te","kn"}` | `{"en","ta","hi","es","fr","de","te","kn","ml"}` |
| `prompt_builder.py` | Falls through to generic handler | Dedicated Telugu block with conversational Tenglish style, technical terms policy, TTS limitation note |
| `detector.py` | Telugu U+0C00–U+0C7F NOT covered | Telugu range added with same ratio/confidence logic as Tamil/Hindi |
| `speechService.js` SUPPORTED_INTERVIEW_LANGUAGES | Had `te-IN` entry, no `limitedSupport` flag | Added `limitedSupport: true`, `limitedSupportNote: "Voice: rare outside Android/ChromeOS"` |
| `TeachingStudioPage.jsx` SUPPORTED_TEACHING_LANGUAGES | Had `te-IN` entry, no `limitedSupport` flag | Added `limitedSupport: true`, `limitedSupportNote: "Voice: rare outside Android/ChromeOS"` |
| `findBestVoiceForLang` | Telugu fell into generic `Other Languages` branch | Dedicated strict `te` branch — returns `null` (never silently falls to English) |
| `getLanguageVoiceMatch` | Generic no-voice message | Includes `limitedSupportNote` in the no-voice message |

**TTS voice availability:** Telugu voices are uncommon on macOS/Windows desktop browsers. They are available primarily on Android and ChromeOS. The honest `limitedSupportNote` is surfaced in the voice status message. TTS returns `null` (no silent English fallback).

---

### Kannada (`kn`) — Option B: Aligned with honest TTS limitation label

`kn-IN` was already present in `SUPPORTED_INTERVIEW_LANGUAGES` (speechService.js). Voice support is rare on most platforms. Applied Option B with a `limitedSupport` flag and honest label.

| Layer | Before | After |
|---|---|---|
| `config.py` SUPPORTED_LANGUAGES default | `en,ta,hi` | `en,ta,hi,te,kn,ml` |
| `interview_session.py` SUPPORTED_LANGUAGES set | `{"en","ta","hi","es","fr","de","te","kn"}` | `{"en","ta","hi","es","fr","de","te","kn","ml"}` |
| `prompt_builder.py` | Falls through to generic handler | Dedicated Kannada block with conversational Kanglish style, technical terms policy, TTS limitation note |
| `detector.py` | Kannada U+0C80–U+0CFF NOT covered | Kannada range added with same ratio/confidence logic |
| `speechService.js` SUPPORTED_INTERVIEW_LANGUAGES | Had `kn-IN` entry, no `limitedSupport` flag | Added `limitedSupport: true`, `limitedSupportNote: "Beta — limited voice support on most platforms"` |
| `TeachingStudioPage.jsx` SUPPORTED_TEACHING_LANGUAGES | Had `kn-IN` entry, no `limitedSupport` flag | Added `limitedSupport: true`, `limitedSupportNote: "Beta — limited voice support on most platforms"` |
| `findBestVoiceForLang` | Kannada fell into generic `Other Languages` branch | Dedicated strict `kn` branch — returns `null` (never silently falls to English) |
| `getLanguageVoiceMatch` | Generic no-voice message | Includes `limitedSupportNote` (`"Beta — limited voice support"`) in the no-voice message |

**TTS voice availability:** Kannada (kn-IN) voices are rare on macOS, Windows, and most Linux desktop browsers. Text responses are always active. Voice is shown as `Beta — limited voice support on most platforms`.

---

### Malayalam (`ml`) — Option B: Aligned with honest TTS limitation label

`ml-IN` was present in `TeachingStudioPage.jsx` `SUPPORTED_TEACHING_LANGUAGES` but was **missing** from `speechService.js` `SUPPORTED_INTERVIEW_LANGUAGES` and from `interview_session.py` `SUPPORTED_LANGUAGES`. Voice support is rare on most platforms.

| Layer | Before | After |
|---|---|---|
| `config.py` SUPPORTED_LANGUAGES default | `en,ta,hi` | `en,ta,hi,te,kn,ml` |
| `interview_session.py` SUPPORTED_LANGUAGES set | `{"en","ta","hi","es","fr","de","te","kn"}` — ml MISSING | Added `"ml"` |
| `prompt_builder.py` | Falls through to generic handler | Dedicated Malayalam block with conversational Manglish style, technical terms policy, TTS limitation note |
| `detector.py` | Malayalam U+0D00–U+0D7F NOT covered | Malayalam range added with same ratio/confidence logic |
| `speechService.js` SUPPORTED_INTERVIEW_LANGUAGES | ml MISSING entirely | Added `ml-IN` entry with `limitedSupport: true`, `limitedSupportNote: "Beta — limited voice support on most platforms"` |
| `TeachingStudioPage.jsx` SUPPORTED_TEACHING_LANGUAGES | Had `ml-IN` entry, no `limitedSupport` flag | Added `limitedSupport: true`, `limitedSupportNote: "Beta — limited voice support on most platforms"` |
| `findBestVoiceForLang` | No `ml` branch | Dedicated strict `ml` branch — returns `null` (never silently falls to English) |
| `getLanguageVoiceMatch` | Generic no-voice message | Includes `limitedSupportNote` in the no-voice message |

**TTS voice availability:** Malayalam (ml-IN) voices are rare on macOS, Windows, and most Linux desktop browsers. Text responses are always active. Voice is shown as `Beta — limited voice support on most platforms`.

---

## Files Changed

| File | Change |
|---|---|
| `backend/app/ai/language/detector.py` | Added Telugu (U+0C00–U+0C7F), Kannada (U+0C80–U+0CFF), Malayalam (U+0D00–U+0D7F) Unicode ranges to `detect_unicode_script`. Added confidence variables and return branches for `te`, `kn`, `ml` following the same pattern as Tamil/Hindi. |
| `backend/app/core/config.py` | Changed `SUPPORTED_LANGUAGES` default from `"en,ta,hi"` to `"en,ta,hi,te,kn,ml"`. |
| `backend/app/schemas/interview_session.py` | Added `"ml"` to the `SUPPORTED_LANGUAGES` set (was missing despite `ml-IN` being in TeachingStudioPage). |
| `backend/app/ai/language/prompt_builder.py` | Added three dedicated language instruction blocks for `te` (Telugu/Tenglish), `kn` (Kannada/Kanglish), and `ml` (Malayalam/Manglish), each following the same conversational tone, preserve technical terms, code-mixing policy, and TTS limitation note as Tamil/Hindi. |
| `frontend/src/services/speechService.js` | (1) Added `ml-IN` entry to `SUPPORTED_INTERVIEW_LANGUAGES`. (2) Added `limitedSupport: true` + `limitedSupportNote` fields to `te`, `kn`, `ml` entries. (3) Added dedicated strict `te`, `kn`, `ml` branches in `findBestVoiceForLang` (return `null`, never English fallback). (4) Updated `getLanguageVoiceMatch` no-voice message to include `limitedSupportNote` when present. (5) Added explicit comment noting `te`, `kn`, `ml` strict match semantics. |
| `frontend/src/pages/TeachingStudioPage.jsx` | Added `limitedSupport: true` + `limitedSupportNote` fields to `te`, `kn`, `ml` entries in `SUPPORTED_TEACHING_LANGUAGES`. |

---

## No-Silent-Fallback Guarantee

For all three languages — Telugu, Kannada, Malayalam — the TTS path is now:

1. `findBestVoiceForLang(voices, 'te'/'kn'/'ml')` → returns a `te-IN`/`kn-IN`/`ml-IN` voice if available, or `null`.
2. `getLanguageVoiceMatch` → when voice is `null`, returns `{ isSupported: false, message: "... not installed ... (Beta — limited voice support ...)" }`.
3. `speakTextInLanguage` → calls `onUnsupported(match)` and returns `false`. Callers display the honest message.
4. English TTS is **never** substituted silently for a requested Indic language.

---

## Backend Test Results

```
120 passed, 7 warnings in 49.28s
```

All pre-existing tests continue to pass. The 7 warnings are pre-existing deprecation notices unrelated to this change.

---

## Constraints Respected

- No language removed from any selector.
- No silent English TTS fallback for any Indic language.
- No new dependencies introduced.
- Prior changes (FEAT-001 and FEAT-002 commits) preserved.
- Code style matched throughout.
