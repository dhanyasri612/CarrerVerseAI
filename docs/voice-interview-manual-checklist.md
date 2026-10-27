# Voice Interview Manual Verification

Voice interview is not currently exposed by the CareerVerse frontend. Do not mark this workflow complete until the following is verified in a supported browser such as Chrome or Edge over localhost or HTTPS.

- [ ] Microphone permission is requested and granted.
- [ ] Speech recognition starts from the interview microphone control.
- [ ] Recognized speech appears in the answer transcript.
- [ ] The recognized transcript is submitted through `submitInterviewAnswer`.
- [ ] The backend returns an evaluation and adaptive follow-up question.
- [ ] The follow-up question is rendered in the interview conversation.
- [ ] Text-to-speech reads the follow-up question aloud.
- [ ] Recognition can be stopped, restarted, and cancelled without duplicating an answer.
- [ ] Permission denial and unsupported-browser errors are shown as user-friendly messages.
- [ ] No microphone audio or credentials are sent outside the configured application flow.
