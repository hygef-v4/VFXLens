# Lemo toolkit dependencies

`pyproject.toml` and `uv.lock` install the upstream core, voice and music package families in an isolated Python 3.12 environment. The reviewed toolkit source is available through `references/lemo-opuscar`; its Node packages are installed in that checkout. Actual source revision and machine location belong in ignored setup status.

```powershell
uv sync --locked --directory studio/tools/lemo
uv run --directory studio/tools/lemo python -c "import kokoro_onnx, faster_whisper, scipy, soundfile, numba; print('Lemo package imports ready')"
```

The current environment is linked to the source checkout's `.venv` so its own tools can use the same packages. A new machine must create that environment/link for its selected tools directory before using checkout-relative commands.

This install does not fetch every style's external asset, instrument library or speech model. Kokoro's model/voice files must be supplied before local narration. Online `edge-tts` is installed; it was used with explicit authorization for one private Vietnamese production. That production's measured timing and review state are in its checkpoint; this does not authorize future online calls or establish pronunciation/mix quality. Renderer browser paths must point to a locally installed compatible Chrome or Chromium. Use only the tool branch required by the film and record any assets/weights still missing.
