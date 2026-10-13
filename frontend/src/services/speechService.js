/**
 * CareerVerse AI Speech Synthesis & Clarity Service
 * Provides high-clarity voice selection, text sanitization for spoken interview questions,
 * and natural pacing configuration.
 */

export const NOVELTY_VOICE_NAMES = [
  "bad news",
  "bahh",
  "bells",
  "boing",
  "bubbles",
  "cellos",
  "deranged",
  "good news",
  "grandma",
  "grandpa",
  "hysterical",
  "jester",
  "junior",
  "organ",
  "pipe organ",
  "ralph",
  "superstar",
  "trinoids",
  "whisper",
  "wobble",
  "zarvox",
  "albert",
  "fred",
  "princess",
  "rishi", // 15-year-old macOS legacy robotic voice that distorts speech
];

export const PREFERRED_VOICE_NAMES = [
  // Top tier natural macOS / iOS voices
  "samantha",
  "daniel",
  "ava",
  "allison",
  "karen",
  "serena",
  "oliver",
  "fiona",
  "moira",
  "tessa",
  // Google Chrome Web Speech voices
  "google us english",
  "google uk english female",
  "google uk english male",
  // Microsoft Edge voices
  "microsoft jenny",
  "microsoft aria",
  "microsoft guy",
  "microsoft david",
  "microsoft zira",
  // Generic neural/natural tag
  "natural",
  "neural",
  // Indian English & regional high quality voices (for Indian regional accents or Tamil/Hindi)
  "veena",
  "vani",
  "lekha",
  "swara",
  "madhur",
];

/**
 * Checks whether a voice is a natural human-like voice rather than a novelty/legacy sound effect.
 */
export const SUPPORTED_INTERVIEW_LANGUAGES = [
  { code: "en", bcp47: "en-IN", fallbackBcp47: "en-US", label: "English", flag: "🇮🇳", native: "English (India / US)" },
  { code: "ta", bcp47: "ta-IN", fallbackBcp47: "ta", label: "Tamil", flag: "🇮🇳", native: "தமிழ் / Tanglish" },
  { code: "hi", bcp47: "hi-IN", fallbackBcp47: "hi", label: "Hindi", flag: "🇮🇳", native: "हिन्दी / Hinglish" },
  { code: "te", bcp47: "te-IN", fallbackBcp47: "te", label: "Telugu", flag: "🇮🇳", native: "తెలుగు" },
  { code: "kn", bcp47: "kn-IN", fallbackBcp47: "kn", label: "Kannada", flag: "🇮🇳", native: "ಕನ್ನಡ" },
  { code: "es", bcp47: "es-ES", fallbackBcp47: "es", label: "Spanish", flag: "🇪🇸", native: "Español" },
  { code: "fr", bcp47: "fr-FR", fallbackBcp47: "fr", label: "French", flag: "🇫🇷", native: "Français" },
  { code: "de", bcp47: "de-DE", fallbackBcp47: "de", label: "German", flag: "🇩🇪", native: "Deutsch" },
];

export function getLanguageConfig(langCode = "en") {
  const code = (langCode || "en").toLowerCase().slice(0, 2);
  return (
    SUPPORTED_INTERVIEW_LANGUAGES.find((l) => l.code === code) ||
    SUPPORTED_INTERVIEW_LANGUAGES[0]
  );
}

/**
 * Checks whether a voice is a natural human-like voice rather than a novelty/legacy sound effect.
 */
export function isNaturalVoice(voice) {
  if (!voice || !voice.name) return false;
  const lower = voice.name.toLowerCase();
  return !NOVELTY_VOICE_NAMES.some((bad) => lower.includes(bad));
}

/**
 * Filters out novelty, distorted, or legacy sound effect voices.
 */
export function filterNaturalVoices(voices = []) {
  return (voices || []).filter(isNaturalVoice);
}

/**
 * Checks if text contains Indic Unicode script (Tamil, Devanagari, Telugu, Kannada, etc.)
 */
export function containsIndicScript(text) {
  return /[\u0900-\u0D7F]/.test(text || "");
}

/**
 * Checks whether a genuine compatible voice exists for a given language code.
 */
export function isVoiceAvailableForLang(voices = [], langCode = "en") {
  if (!voices || voices.length === 0) return false;
  const target = (langCode || "en").toLowerCase().slice(0, 2);
  if (target === "ta") {
    return voices.some(
      (v) => (v.lang && v.lang.toLowerCase().startsWith("ta")) || /vani|tamil/i.test(v.name)
    );
  }
  if (target === "hi") {
    return voices.some(
      (v) => (v.lang && v.lang.toLowerCase().startsWith("hi")) || /lekha|swara|madhur|hindi/i.test(v.name)
    );
  }
  if (target === "en") {
    return voices.some((v) => v.lang && v.lang.toLowerCase().startsWith("en"));
  }
  return voices.some((v) => v.lang && v.lang.toLowerCase().startsWith(target));
}

/**
 * Resolves voice availability status and details for UI presentation.
 * Explicitly alerts when a requested language voice is absent.
 */
export function getLanguageVoiceMatch(voices = [], langCode = "en", preferredUri = "") {
  const cfg = getLanguageConfig(langCode);
  if (!voices || voices.length === 0) {
    return {
      voice: null,
      isSupported: false,
      isExactLanguageMatch: false,
      voiceName: null,
      bcp47: cfg.bcp47,
      message: `Audio voices are loading or unavailable in this browser. Text interaction is active.`,
    };
  }

  const voice = findBestVoiceForLang(voices, cfg.code, preferredUri);
  if (!voice) {
    return {
      voice: null,
      isSupported: false,
      isExactLanguageMatch: false,
      voiceName: null,
      bcp47: cfg.bcp47,
      message: `A compatible voice for ${cfg.label} (${cfg.bcp47}) is not installed on this system. Text display and keyboard interaction are active.`,
    };
  }

  return {
    voice,
    isSupported: true,
    isExactLanguageMatch: true,
    voiceName: voice.name,
    bcp47: cfg.bcp47,
    message: `${cfg.label} voice active: ${voice.name}`,
  };
}

/**
 * Finds the highest quality, most natural voice strictly matching the language code.
 * Will NEVER silently substitute an English voice when Tamil or Hindi is requested.
 */
export function findBestVoiceForLang(voices = [], langCode = "en", preferredUri = "", text = "") {
  if (!voices || voices.length === 0) return null;

  const target = (langCode || "en").toLowerCase().slice(0, 2);

  // 1. If user explicitly selected a voice URI that matches the target language
  if (preferredUri) {
    const userVoice = voices.find((v) => v.voiceURI === preferredUri);
    if (userVoice && isNaturalVoice(userVoice)) {
      const vLang = (userVoice.lang || "").toLowerCase();
      if (target === "ta" && (vLang.startsWith("ta") || /vani|tamil/i.test(userVoice.name))) {
        return userVoice;
      }
      if (target === "hi" && (vLang.startsWith("hi") || /lekha|swara|madhur|hindi/i.test(userVoice.name))) {
        return userVoice;
      }
      if (target === "en" && vLang.startsWith("en")) {
        return userVoice;
      }
    }
  }

  const natural = filterNaturalVoices(voices);
  const candidates = natural.length > 0 ? natural : voices;

  // 2. Strict Tamil Voice Matching
  if (target === "ta") {
    const tamilVoice = candidates.find(
      (v) => (v.lang && v.lang.toLowerCase().startsWith("ta")) || /vani|tamil/i.test(v.name)
    );
    return tamilVoice || null;
  }

  // 3. Strict Hindi Voice Matching
  if (target === "hi") {
    const hindiVoice = candidates.find(
      (v) => (v.lang && v.lang.toLowerCase().startsWith("hi")) || /lekha|swara|madhur|hindi/i.test(v.name)
    );
    return hindiVoice || null;
  }

  // 4. English Voice Matching (Prefer Indian English en-IN or preferred neural voices)
  if (target === "en") {
    const indianEnVoice = candidates.find(
      (v) => (v.lang && (v.lang.toLowerCase() === "en-in" || v.lang.toLowerCase().startsWith("en_in"))) || /veena|aman|tara/i.test(v.name)
    );
    if (indianEnVoice && isNaturalVoice(indianEnVoice)) return indianEnVoice;

    for (const pref of PREFERRED_VOICE_NAMES) {
      const match = candidates.find(
        (v) => v.lang && v.lang.toLowerCase().startsWith("en") && v.name.toLowerCase().includes(pref)
      );
      if (match) return match;
    }
    return candidates.find((v) => v.lang && v.lang.toLowerCase().startsWith("en")) || candidates[0];
  }

  // 5. Other Languages (es, fr, de, te, kn)
  const langVoices = candidates.filter(
    (v) => v.lang && v.lang.toLowerCase().startsWith(target)
  );
  if (langVoices.length > 0) return langVoices[0];

  return null;
}


/**
 * Speak only with a voice that matches the requested language. Returns false
 * when the browser has no compatible voice, so callers can keep text active
 * and show an honest capability message.
 *
 * @param {string} text - The text to speak.
 * @param {string} [langCode='en'] - Two-character language code (e.g. 'ta', 'hi', 'en').
 * @param {object} [options={}]
 * @param {function} [options.onUnsupported] - Called with the voice-match object when no voice is available.
 * @param {function} [options.onStarted] - Called with `true` when speech actually starts (useful for async voice load).
 * @param {number} [options.rate=1] - Speech rate.
 * @param {number} [options.pitch=1] - Speech pitch.
 * @returns {boolean} true if speech started synchronously; false if voices were not yet loaded or no voice available.
 */
export function speakTextInLanguage(text, langCode = "en", options = {}) {
  if (typeof window === "undefined" || !("speechSynthesis" in window) || !text) return false;
  const { onUnsupported, onStarted, rate = 1, pitch = 1 } = options;
  const synth = window.speechSynthesis;
  const cfg = getLanguageConfig(langCode);
  const speak = () => {
    const match = getLanguageVoiceMatch(synth.getVoices() || [], cfg.code);
    if (!match.isSupported || !match.voice) {
      onUnsupported?.(match);
      return false;
    }
    synth.cancel();
    const utterance = new SpeechSynthesisUtterance(String(text));
    utterance.lang = cfg.bcp47;
    utterance.voice = match.voice;
    utterance.rate = rate;
    utterance.pitch = pitch;
    synth.speak(utterance);
    return true;
  };
  if ((synth.getVoices() || []).length === 0) {
    const retry = () => {
      synth.removeEventListener?.("voiceschanged", retry);
      const started = speak();
      if (started) onStarted?.(true);
    };
    synth.addEventListener?.("voiceschanged", retry);
    return false;
  }
  return speak();
}

/**
 * Sanitizes technical interview question text for natural speech synthesis.
 * Strips code blocks, curly braces, technical schemas, and replaces complexity notation
 * with human-spoken equivalents so TTS is crystal clear and conversational.
 */
export function cleanTextForSpeech(rawText) {
  if (!rawText) return "";
  let text = String(rawText);

  // If there is an "Example Schema:", "Example Scenario:", "Example:", "Example 1:", split and only speak the main question prompt
  const exampleMatch = text.search(
    /\b(?:Example(?:\s+Schema|\s+Scenario|\s+1|\s*:)?:|Input:|Goal:)/i
  );
  let mainPrompt = text;
  let hasExample = false;
  if (exampleMatch > 30) {
    mainPrompt = text.slice(0, exampleMatch).trim();
    hasExample = true;
  }

  // Remove code blocks and inline code ticks
  mainPrompt = mainPrompt.replace(/```[\s\S]*?```/g, " ");
  mainPrompt = mainPrompt.replace(/`([^`]+)`/g, "$1");

  // Remove URLs, paths, endpoints
  mainPrompt = mainPrompt.replace(/https?:\/\/\S+/g, "");
  mainPrompt = mainPrompt.replace(/\/api\/v\d+\/\S+/g, "API endpoint");

  // Replace math / complexity notation
  mainPrompt = mainPrompt.replace(/\$O\((.*?)\)\$/gi, "O of $1");
  mainPrompt = mainPrompt.replace(/\$n\$/gi, "n");
  mainPrompt = mainPrompt.replace(/O\(\s*1\s*\)/gi, "O of 1");
  mainPrompt = mainPrompt.replace(/O\(\s*n\s*\)/gi, "O of n");
  mainPrompt = mainPrompt.replace(/O\(\s*log\s*n\s*\)/gi, "O of log n");
  mainPrompt = mainPrompt.replace(/O\(\s*n\s*\^?\s*2\s*\)/gi, "O of n squared");
  mainPrompt = mainPrompt.replace(/O\(\s*n\s*log\s*n\s*\)/gi, "O of n log n");

  // Replace common acronyms and underscores for natural speech
  mainPrompt = mainPrompt.replace(/\bDSA\b/g, "Data Structures and Algorithms");
  mainPrompt = mainPrompt.replace(/\bSQL\b/g, "S Q L");
  mainPrompt = mainPrompt.replace(/\bNoSQL\b/g, "No S Q L");
  mainPrompt = mainPrompt.replace(/\bAPI\b/g, "A P I");
  mainPrompt = mainPrompt.replace(/\bAPIs\b/g, "A P I s");
  mainPrompt = mainPrompt.replace(/\bDB\b/g, "database");
  mainPrompt = mainPrompt.replace(/([a-zA-Z])_([a-zA-Z])/g, "$1 $2"); // user_id -> user id

  // Remove markdown headers, list markers, and bullets
  mainPrompt = mainPrompt.replace(/^#{1,6}\s+/gm, "");
  mainPrompt = mainPrompt.replace(/^\s*[-*•]\s+/gm, "");
  mainPrompt = mainPrompt.replace(/^\s*\d+\.\s+/gm, "");

  // Strip emojis (symbols, pictographs, transport, misc)
  mainPrompt = mainPrompt.replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{26FF}\u{2700}-\u{27BF}]/gu, " ");

  // Strip disruptive punctuation and symbols
  mainPrompt = mainPrompt.replace(/[{}\[\]()<>\\\/_~*#•$]/g, " ");
  mainPrompt = mainPrompt.replace(/['"]/g, "");
  mainPrompt = mainPrompt.replace(/\s+/g, " ").trim();

  // Deduplicate consecutive repeated words ("the the", "Design Design")
  mainPrompt = mainPrompt.replace(/\b([a-zA-Z]{2,})\s+\1\b/gi, "$1");

  // Clean trailing punctuation
  mainPrompt = mainPrompt.replace(/[.:,;]+$/, "");

  if (hasExample && !mainPrompt.toLowerCase().includes("screen") && !mainPrompt.includes("திரையில்") && !mainPrompt.includes("स्क्रीन")) {
    if (/[\u0B80-\u0BFF]/.test(mainPrompt)) {
      mainPrompt += ". ஒரு மாதிரி உதாரணம் திரையில் காட்டப்பட்டுள்ளது.";
    } else if (/[\u0900-\u097F]/.test(mainPrompt)) {
      mainPrompt += ". एक उदाहरण कोड स्क्रीन पर प्रदर्शित है.";
    } else {
      mainPrompt += ". A code example is displayed on your screen.";
    }
  } else {
    mainPrompt += ".";
  }

  return mainPrompt;
}
