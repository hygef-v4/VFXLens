# Image Sequences: Importing Frames, FPS, and Channels Accurately

## Identification

An image sequence is an ordered series of numbered frames; PNG or EXR files may also be standalone stills. Group files by directory, prefix, frame number padding, suffix, and extension before concluding how many distinct animations exist in a folder.

## Pre-Import Checklist

- Is the frame numbering contiguous, or are there gaps, duplicate numbers, or copy suffixes?
- Do PNG and EXR folders share the same frame count and dimensions? Never assume they are interchangeable renders without checking.
- What is the intended playback FPS? Frame numbers and still image headers rarely encode frame rate on their own.
- Does a true alpha channel exist? A `.png` extension does not guarantee transparency, and an `.exr` file may store custom multi-channel layers rather than standard `RGBA`.
- Are channels, bit depth, and color space metadata interpreted accurately by the host?

## Application

Select the first frame and enable sequence import; verify the frame count and ordering recognized by the host. Set **Interpret Footage** to the verified source frame rate. Inspect start/end frames, alpha edges, and playback speed before compositing. When the native source FPS is unknown, record it as `unavailable` rather than picking an arbitrary rate and calling it native. See [Adobe: Preparing and importing still images and sequences](https://helpx.adobe.com/after-effects/desktop/import-files/import-still-images/preparing-importing-still-images.html).

OpenEXR files can contain named multi-part or grouped channels (such as `beauty` or nested `alpha`). Verify channel mapping/extraction when the host does not auto-bind them, and never rename or mutate original source files just to test an import. Reading `half`/`float` header types does not by itself confirm the working color space or successful pixel decoding. See [OpenEXR Technical Introduction](https://openexr.com/en/latest/TechnicalIntroduction.html).

## Common Pitfalls

Importing sequence frames as hundreds of individual still layers; inconsistent filename suffixes causing the host to truncate a sequence early; silently fabricating missing frames; assuming another preview video's FPS is the sequence's native rate; or using blending modes to hide channel interpretation errors. Always test on a working copy and document what was verified.

**Related:** [Compositing Foundations](../foundations/compositing.md), [Timing and Easing](../foundations/timing-and-easing.md), [Overlays](overlays.md).
