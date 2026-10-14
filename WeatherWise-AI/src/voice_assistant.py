"""Browser-native voice helpers; optional and graceful when unavailable."""
def browser_voice_guidance() -> str:
    return ("Voice input is browser-dependent. Use the microphone button if your Streamlit/browser build exposes it, "
            "or dictate into your device's operating-system speech input. The app always supports typing. "
            "Spoken output uses browser speech synthesis when supported; audio stays in the browser for speech playback.")
