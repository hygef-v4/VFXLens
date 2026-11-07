# Sound Effects: Sonic Roles, Synchronization, and Mixing

## Identifying by Ear and Waveform

| Suggested Role | Waveform / Sonic Cues | Typical Editorial Use |
| --- | --- | --- |
| Whoosh / flyby | Smooth rise-peak-decay envelope with directional sweep | Camera whips, spins, and directional transitions |
| Hit / impact | Sharp initial transient followed by low-end body/tail | Physical contact, hard cuts, and title slams |
| Reverse / suck / riser | Energy building toward an abrupt cutoff | Pre-cut anticipation leading into a beat or impact |
| Click / typewriter | Short, crisp impulse with distinct rhythmic attack | Kinetic typography, UI callouts, and counters |
| Ambience / room tone | Sustained texture without aggressive transients | Scene bed and smoothing across cuts |
| Glitch / static | Stuttering rhythmic bursts or frequency tears | Deliberate analog/digital distortion accents |

Filenames are only an initial clue; measuring peak amplitude alone never confirms timbre, audio quality, or category.

## Selection and Application

1. Audition the asset solo and identify the usable section; inspect the waveform to locate the lead-in, primary transient, and decay tail.
2. Align the **audible transient peak** (not the start of the audio file) with the visual point of impact or motion peak.
3. Trim on the timeline, apply short micro-fades at cut boundaries to prevent clicks, and let the tail decay naturally into the space.
4. Balance against music and dialogue, monitor the master bus after stacking layers, and check peak headroom.
5. Prefer a few distinct sonic layers with clear frequency roles over stacking an identical impact hit on every single text frame or cut.

## Measurements vs. Unknowns

Sample peak, true peak, RMS, and integrated LUFS measure different physical quantities. When reporting audio metrics, state the measurement method, channel layout, sample rate, and time window. A sample peak touching `0 dBFS` warrants checking headroom but does not by itself prove audible clipping, and measuring a short slice does not characterize the entire file. Higher sample rates or bit depths do not automatically make a sound effect fit a scene better.

Never hardcode a universal gain offset for all SFX without auditioning in the mix. Clearly distinguish filenames/signal measurements from subjective mix decisions.

**Related:** [Audio Filters and Reverb](../techniques/sound-design/filters-and-reverb.md), [Impact Style](../styles/impact.md), [AE Notes: audio processing examples](../case-studies/ae-notes.md).
