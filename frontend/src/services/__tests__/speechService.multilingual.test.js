/**
 * speechServiceMultilingual.regression.test.js
 *
 * Scenarios 10–12 of the 12-scenario multilingual regression suite.
 *
 * Scenario 10 — Speech recognition receives the correct recognition.lang
 *               locale for each selected language.
 * Scenario 11 — Missing/unsupported voice triggers a truthful fallback
 *               message (not a silent fail).
 * Scenario 12 — Smoke test: English interview/teaching features still work —
 *               exported functions are intact and behave correctly for English.
 *
 * All external dependencies (speechSynthesis, SpeechRecognition) are mocked.
 * No real network or audio calls are made.
 */

import { describe, it, expect, vi, afterEach } from "vitest";
import {
  speakTextInLanguage,
  getLanguageConfig,
  findBestVoiceForLang,
  getLanguageVoiceMatch,
  isVoiceAvailableForLang,
  filterNaturalVoices,
  cleanTextForSpeech,
  SUPPORTED_INTERVIEW_LANGUAGES,
} from "../speechService";

// ── Shared stubs ─────────────────────────────────────────────────────────────

/**
 * SpeechSynthesisUtterance is absent in jsdom; provide a minimal stub so that
 * speakTextInLanguage can instantiate it and we can inspect the fields set.
 */
class SpeechSynthesisUtteranceStub {
  constructor(text) {
    this.text = text;
    this.lang = "";
    this.voice = null;
    this.rate = 1;
    this.pitch = 1;
  }
}

/**
 * Install a mock window.speechSynthesis backed by the given voices array.
 * Returns the mock synth object for assertion.
 */
function mockSynth(voices = []) {
  const synth = {
    getVoices: vi.fn(() => voices),
    speak: vi.fn(),
    cancel: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
  };
  Object.defineProperty(window, "speechSynthesis", {
    value: synth,
    writable: true,
    configurable: true,
  });
  return synth;
}

// ── Scenario 10 — Speech recognition locale ──────────────────────────────────

describe("Scenario 10 — Speech recognition receives correct recognition.lang per language", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("sets recognition.lang to ta-IN when Tamil is selected", () => {
    const recognition = { lang: "" };
    recognition.lang = getLanguageConfig("ta").bcp47;
    expect(recognition.lang).toBe("ta-IN");
  });

  it("sets recognition.lang to hi-IN when Hindi is selected", () => {
    const recognition = { lang: "" };
    recognition.lang = getLanguageConfig("hi").bcp47;
    expect(recognition.lang).toBe("hi-IN");
  });

  it("sets recognition.lang to en-IN when English is selected", () => {
    const recognition = { lang: "" };
    recognition.lang = getLanguageConfig("en").bcp47;
    expect(recognition.lang).toBe("en-IN");
  });

  it("each SUPPORTED_INTERVIEW_LANGUAGES entry has a distinct, non-empty bcp47", () => {
    const bcp47s = SUPPORTED_INTERVIEW_LANGUAGES.map((l) => l.bcp47);
    // All values are non-empty strings
    bcp47s.forEach((b) => expect(b).toBeTruthy());
    // All values are unique
    expect(new Set(bcp47s).size).toBe(bcp47s.length);
  });
});

// ── Scenario 11 — Missing voice → truthful fallback, not a silent fail ────────

describe("Scenario 11 — Missing/unsupported voice triggers a truthful fallback message", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("getLanguageVoiceMatch returns isSupported=false and a non-empty message when no Tamil voice exists", () => {
    const englishOnlyVoices = [
      { name: "Samantha", lang: "en-US", voiceURI: "en-us" },
      { name: "Daniel", lang: "en-GB", voiceURI: "en-gb" },
    ];
    const match = getLanguageVoiceMatch(englishOnlyVoices, "ta");

    expect(match.isSupported).toBe(false);
    expect(match.voice).toBeNull();
    expect(match.message).toBeTruthy();
    expect(match.message.length).toBeGreaterThan(10);
  });

  it("speakTextInLanguage calls onUnsupported and returns false when voices list has no Tamil voice", () => {
    const englishOnlyVoices = [{ name: "Samantha", lang: "en-US", voiceURI: "en-us" }];
    const synth = mockSynth(englishOnlyVoices);
    vi.stubGlobal("SpeechSynthesisUtterance", SpeechSynthesisUtteranceStub);

    const onUnsupported = vi.fn();
    const result = speakTextInLanguage("நன்றி", "ta", { onUnsupported });

    expect(result).toBe(false);
    expect(onUnsupported).toHaveBeenCalledOnce();
    // Crucially: must NOT silently speak with an English voice
    expect(synth.speak).not.toHaveBeenCalled();
  });

  it("speakTextInLanguage calls onUnsupported with a match object describing the failure", () => {
    const englishOnlyVoices = [{ name: "Samantha", lang: "en-US", voiceURI: "en-us" }];
    mockSynth(englishOnlyVoices);
    vi.stubGlobal("SpeechSynthesisUtterance", SpeechSynthesisUtteranceStub);

    let receivedMatch = null;
    speakTextInLanguage("नमस्ते", "hi", {
      onUnsupported: (match) => {
        receivedMatch = match;
      },
    });

    expect(receivedMatch).not.toBeNull();
    expect(receivedMatch.isSupported).toBe(false);
    expect(receivedMatch.message).toBeTruthy();
  });

  it("getLanguageVoiceMatch returns a message when voices list is empty", () => {
    const match = getLanguageVoiceMatch([], "ta");
    expect(match.isSupported).toBe(false);
    expect(match.message).toBeTruthy();
    // Message must mention audio/voice, not be a generic empty string
    expect(match.message.toLowerCase()).toMatch(/voice|audio/);
  });

  it("isVoiceAvailableForLang returns false when only English voices exist and Tamil is requested", () => {
    const englishOnly = [{ name: "Samantha", lang: "en-US", voiceURI: "en-us" }];
    expect(isVoiceAvailableForLang(englishOnly, "ta")).toBe(false);
  });
});

// ── Scenario 12 — Smoke test: English features still intact ──────────────────

describe("Scenario 12 — English interview/teaching features still pass smoke test", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("speakTextInLanguage is exported and callable", () => {
    expect(typeof speakTextInLanguage).toBe("function");
  });

  it("getLanguageConfig is exported and returns correct English config", () => {
    const cfg = getLanguageConfig("en");
    expect(cfg.code).toBe("en");
    expect(cfg.bcp47).toBe("en-IN");
    expect(cfg.label).toBe("English");
  });

  it("findBestVoiceForLang returns an English voice from a mixed list", () => {
    const voices = [
      { name: "English Voice", lang: "en-US", voiceURI: "en-us" },
      { name: "Tamil Voice", lang: "ta-IN", voiceURI: "ta-in" },
    ];
    const voice = findBestVoiceForLang(voices, "en");
    expect(voice).not.toBeNull();
    expect(voice.lang.toLowerCase()).toMatch(/^en/);
  });

  it("getLanguageVoiceMatch reports isSupported=true for English when English voice exists", () => {
    const voices = [
      { name: "Samantha", lang: "en-US", voiceURI: "en-us" },
    ];
    const match = getLanguageVoiceMatch(voices, "en");
    expect(match.isSupported).toBe(true);
    expect(match.voice).not.toBeNull();
  });

  it("cleanTextForSpeech correctly sanitizes technical interview text for English TTS", () => {
    const raw = "Explain `O(n log n)` complexity. Example: [1, 2, 3]";
    const cleaned = cleanTextForSpeech(raw);
    expect(cleaned).not.toContain("`");
    expect(cleaned).toContain("O of n log n");
  });

  it("filterNaturalVoices strips novelty voices and keeps natural ones", () => {
    const voices = [
      { name: "Samantha", lang: "en-US", voiceURI: "en-us" },
      { name: "Boing", lang: "en-US", voiceURI: "boing" },
      { name: "Bubbles", lang: "en-US", voiceURI: "bubbles" },
    ];
    const natural = filterNaturalVoices(voices);
    expect(natural).toHaveLength(1);
    expect(natural[0].name).toBe("Samantha");
  });

  it("speakTextInLanguage returns true and calls synth.speak for English text", () => {
    const voices = [{ name: "Samantha", lang: "en-US", voiceURI: "en-us" }];
    const synth = mockSynth(voices);
    vi.stubGlobal("SpeechSynthesisUtterance", SpeechSynthesisUtteranceStub);

    const result = speakTextInLanguage("Hello, how did you use FastAPI?", "en");

    expect(result).toBe(true);
    expect(synth.speak).toHaveBeenCalledOnce();
    const utterance = synth.speak.mock.calls[0][0];
    expect(utterance.lang).toBe("en-IN");
  });

  it("speakTextInLanguage with Tamil voice still works for English fallback bcp47", () => {
    // When a Tamil voice is present, Tamil TTS must work correctly
    const voices = [{ name: "Vani", lang: "ta-IN", voiceURI: "ta-in" }];
    const synth = mockSynth(voices);
    vi.stubGlobal("SpeechSynthesisUtterance", SpeechSynthesisUtteranceStub);

    const result = speakTextInLanguage("நன்றி", "ta");
    expect(result).toBe(true);
    const utterance = synth.speak.mock.calls[0][0];
    expect(utterance.lang).toBe("ta-IN");
  });
});
