"""Third-party and built-in After Effects plugin/effect classifier.

Identifies plugin vendor, package suite, category, and third-party status from
effect `matchName` and display name without loading or executing any `.aex` binaries.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PluginClassification:
    """Classification metadata for an After Effects effect/plugin."""

    match_name: str
    display_name: str
    plugin_vendor: str
    plugin_package: str
    category: str
    is_third_party: bool
    is_builtin: bool


# Built-in Adobe After Effects matchName prefixes and specific non-ADBE built-in matchNames
_BUILTIN_EXACT_MATCH_NAMES: dict[str, tuple[str, str]] = {
    "CC Ball Action": ("Simulation", "Cycore FX (Bundled with AE)"),
    "CC Bender": ("Distort", "Cycore FX (Bundled with AE)"),
    "CC Bend It": ("Distort", "Cycore FX (Bundled with AE)"),
    "CC Blobbylize": ("Distort", "Cycore FX (Bundled with AE)"),
    "CC Block Load": ("Stylize", "Cycore FX (Bundled with AE)"),
    "CC Bubbles": ("Simulation", "Cycore FX (Bundled with AE)"),
    "CC Burn Film": ("Stylize", "Cycore FX (Bundled with AE)"),
    "CC Color Neutralizer": ("Color Correction", "Cycore FX (Bundled with AE)"),
    "CC Color Offset": ("Color Correction", "Cycore FX (Bundled with AE)"),
    "CC Composite": ("Channel", "Cycore FX (Bundled with AE)"),
    "CC Cross Blur": ("Blur & Sharpen", "Cycore FX (Bundled with AE)"),
    "CC Cylinder": ("Perspective", "Cycore FX (Bundled with AE)"),
    "CC Drizzle": ("Simulation", "Cycore FX (Bundled with AE)"),
    "CC Environment": ("Perspective", "Cycore FX (Bundled with AE)"),
    "CC Flo Motion": ("Distort", "Cycore FX (Bundled with AE)"),
    "CC Force Motion Blur": ("Time", "Cycore FX (Bundled with AE)"),
    "CC Glass": ("Stylize", "Cycore FX (Bundled with AE)"),
    "CC Glue Gun": ("Generate", "Cycore FX (Bundled with AE)"),
    "CC Griddler": ("Distort", "Cycore FX (Bundled with AE)"),
    "CC Hair": ("Simulation", "Cycore FX (Bundled with AE)"),
    "CC HexTile": ("Stylize", "Cycore FX (Bundled with AE)"),
    "CC Image Wipe": ("Transition", "Cycore FX (Bundled with AE)"),
    "CC Jaws": ("Transition", "Cycore FX (Bundled with AE)"),
    "CC Kaleida": ("Stylize", "Cycore FX (Bundled with AE)"),
    "CC Kernel": ("Color Correction", "Cycore FX (Bundled with AE)"),
    "CC Lens": ("Distort", "Cycore FX (Bundled with AE)"),
    "CC Light Burst 2.5": ("Generate", "Cycore FX (Bundled with AE)"),
    "CC Light Rays": ("Generate", "Cycore FX (Bundled with AE)"),
    "CC Light Sweep": ("Generate", "Cycore FX (Bundled with AE)"),
    "CC Line Sweep": ("Transition", "Cycore FX (Bundled with AE)"),
    "CC Mr. Mercury": ("Simulation", "Cycore FX (Bundled with AE)"),
    "CC Mr. Smoothie": ("Stylize", "Cycore FX (Bundled with AE)"),
    "CC Overbrights": ("Channel", "Cycore FX (Bundled with AE)"),
    "CC Page Turn": ("Distort", "Cycore FX (Bundled with AE)"),
    "CC Particle Systems II": ("Simulation", "Cycore FX (Bundled with AE)"),
    "CC Particle World": ("Simulation", "Cycore FX (Bundled with AE)"),
    "CC Pixel Polly": ("Simulation", "Cycore FX (Bundled with AE)"),
    "CC Plastic": ("Stylize", "Cycore FX (Bundled with AE)"),
    "CC Power Pin": ("Distort", "Cycore FX (Bundled with AE)"),
    "CC Radial Blur": ("Blur & Sharpen", "Cycore FX (Bundled with AE)"),
    "CC Radial Fast Blur": ("Blur & Sharpen", "Cycore FX (Bundled with AE)"),
    "CC Radial ScaleWipe": ("Transition", "Cycore FX (Bundled with AE)"),
    "CC Rain": ("Simulation", "Cycore FX (Bundled with AE)"),
    "CC Rainfall": ("Simulation", "Cycore FX (Bundled with AE)"),
    "CC RepeTile": ("Stylize", "Cycore FX (Bundled with AE)"),
    "CC Ripple Pulse": ("Distort", "Cycore FX (Bundled with AE)"),
    "CC Scale Wipe": ("Transition", "Cycore FX (Bundled with AE)"),
    "CC Scatterize": ("Simulation", "Cycore FX (Bundled with AE)"),
    "CC Simple Wire Removal": ("Keying", "Cycore FX (Bundled with AE)"),
    "CC Slant": ("Distort", "Cycore FX (Bundled with AE)"),
    "CC Smear": ("Distort", "Cycore FX (Bundled with AE)"),
    "CC Snow": ("Simulation", "Cycore FX (Bundled with AE)"),
    "CC Snowfall": ("Simulation", "Cycore FX (Bundled with AE)"),
    "CC Sphere": ("Perspective", "Cycore FX (Bundled with AE)"),
    "CC Split": ("Distort", "Cycore FX (Bundled with AE)"),
    "CC Split 2": ("Distort", "Cycore FX (Bundled with AE)"),
    "CC Spotlight": ("Perspective", "Cycore FX (Bundled with AE)"),
    "CC Star Burst": ("Simulation", "Cycore FX (Bundled with AE)"),
    "CC Threads": ("Generate", "Cycore FX (Bundled with AE)"),
    "CC Threshold": ("Stylize", "Cycore FX (Bundled with AE)"),
    "CC Threshold RGB": ("Stylize", "Cycore FX (Bundled with AE)"),
    "CC Time Blend": ("Time", "Cycore FX (Bundled with AE)"),
    "CC Time Blend FX": ("Time", "Cycore FX (Bundled with AE)"),
    "CC Toner": ("Color Correction", "Cycore FX (Bundled with AE)"),
    "CC Twister": ("Transition", "Cycore FX (Bundled with AE)"),
    "CC Vector Blur": ("Blur & Sharpen", "Cycore FX (Bundled with AE)"),
    "CC Vignette": ("Stylize", "Cycore FX (Bundled with AE)"),
    "CC WarpoMatic": ("Transition", "Cycore FX (Bundled with AE)"),
    "CC Wide Time": ("Time", "Cycore FX (Bundled with AE)"),
}


def _infer_builtin_category(match_name: str, display_name: str) -> str:
    label = f"{match_name} {display_name}".lower()
    if any(k in label for k in ("blur", "sharpen", "unsharp")):
        return "Blur & Sharpen"
    if any(k in label for k in ("glow", "threshold", "emboss", "find edges", "mosaic", "posterize", "roughen", "scatter", "strobe")):
        return "Stylize"
    if any(k in label for k in ("levels", "curves", "tint", "tritone", "hue", "lumetri", "vibrance", "exposure", "brightness", "contrast", "color")):
        return "Color Correction"
    if any(k in label for k in ("displacement", "turbulent", "warp", "twirl", "spherize", "optics", "mirror", "mesh", "liquify", "corner pin", "bezier", "bulge", "transform", "geometry", " magnify", "offset")):
        return "Distort"
    if any(k in label for k in ("slider control", "checkbox control", "color control", "point control", "angle control", "layer control", "dropdown menu")):
        return "Expression Controls"
    if any(k in label for k in ("keylight", "key", "spill", "matte")):
        return "Keying / Matte"
    if any(k in label for k in ("fill", "gradient", "ramp", "4-color", "beam", "checkerboard", "circle", "ellipse", "grid", "lens flare", "fractal", "noise", "stroke", "vegas", "write-on")):
        return "Generate / Noise"
    if any(k in label for k in ("time", "echo", "posterize time", "timewarp")):
        return "Time"
    if any(k in label for k in ("wipe", "iris", "venetian")):
        return "Transition"
    if any(k in label for k in ("channel", "invert", "shift channels", "minimax", "arithmetic", "calculations", "compound")):
        return "Channel"
    return "Built-in Effect"


def classify_effect(match_name: str, display_name: str | None = None) -> PluginClassification:
    """Classify an After Effects effect by its `matchName` and display name."""
    clean_mn = (match_name or "").strip()
    clean_dn = (display_name or clean_mn).strip()
    upper_mn = clean_mn.upper()
    lower_dn = clean_dn.lower()

    # 1. Standard Adobe Built-in Effects (ADBE *)
    if clean_mn.startswith("ADBE "):
        return PluginClassification(
            match_name=clean_mn,
            display_name=clean_dn,
            plugin_vendor="Adobe",
            plugin_package="After Effects Built-in",
            category=_infer_builtin_category(clean_mn, clean_dn),
            is_third_party=False,
            is_builtin=True,
        )

    # 2. Bundled Cycore FX (CC *) and Synthetic Aperture / Keylight / Mocha bundled plugins
    if clean_mn in _BUILTIN_EXACT_MATCH_NAMES or clean_mn.startswith("CS ") or clean_mn.startswith("CC "):
        cat, pkg = _BUILTIN_EXACT_MATCH_NAMES.get(
            clean_mn, (_infer_builtin_category(clean_mn, clean_dn), "Cycore FX (Bundled with AE)")
        )
        return PluginClassification(
            match_name=clean_mn,
            display_name=clean_dn,
            plugin_vendor="Adobe / Cycore FX",
            plugin_package=pkg,
            category=cat,
            is_third_party=False,
            is_builtin=True,
        )

    if upper_mn.startswith("KEYLIGHT"):
        return PluginClassification(
            match_name=clean_mn,
            display_name=clean_dn,
            plugin_vendor="Foundry (Bundled with AE)",
            plugin_package="Keylight",
            category="Keying",
            is_third_party=False,
            is_builtin=True,
        )

    # 3. Boris FX Sapphire (S_*)
    if clean_mn.startswith("S_") or lower_dn.startswith("s_"):
        sub_cat = "Stylize / VFX"
        if "shake" in lower_dn or "shake" in clean_mn.lower():
            sub_cat = "Distort / Shake"
        elif "glow" in lower_dn or "glint" in lower_dn or "rays" in lower_dn or "flare" in lower_dn:
            sub_cat = "Lighting / Glow"
        elif "blur" in lower_dn:
            sub_cat = "Blur & Sharpen"
        elif "distort" in lower_dn or "warp" in lower_dn:
            sub_cat = "Distort / Warp"
        elif "transition" in lower_dn or "wipe" in lower_dn or "swish" in lower_dn or "dissolve" in lower_dn:
            sub_cat = "Transitions"
        return PluginClassification(
            match_name=clean_mn,
            display_name=clean_dn,
            plugin_vendor="Boris FX",
            plugin_package="Sapphire",
            category=sub_cat,
            is_third_party=True,
            is_builtin=False,
        )

    # 4. Boris FX Continuum (BCC*)
    if upper_mn.startswith("BCC") or lower_dn.startswith("bcc "):
        return PluginClassification(
            match_name=clean_mn,
            display_name=clean_dn,
            plugin_vendor="Boris FX",
            plugin_package="Continuum (BCC)",
            category=_infer_builtin_category(clean_mn, clean_dn),
            is_third_party=True,
            is_builtin=False,
        )

    # 5. Deep Glow (Plugin Everything)
    if "deep glow" in lower_dn or "deepglow" in upper_mn.replace(" ", "").lower():
        return PluginClassification(
            match_name=clean_mn,
            display_name=clean_dn,
            plugin_vendor="Plugin Everything",
            plugin_package="Deep Glow",
            category="Glow / Stylize",
            is_third_party=True,
            is_builtin=False,
        )

    # 6. Maxon / Red Giant Trapcode Suite
    trapcode_keywords = (
        "tc ",
        "trapcode",
        "particular",
        "rg trapcode",
        "starglow",
        "3d stroke",
        "sound keys",
        "echospace",
    )
    if (
        clean_mn.startswith("tc")
        or clean_mn.startswith("RG ")
        or any(k in lower_dn for k in trapcode_keywords)
        or clean_mn in ("Particular", "Form", "Mir", "Tao", "Shine", "Starglow", "Lux", "3D Stroke")
    ):
        return PluginClassification(
            match_name=clean_mn,
            display_name=clean_dn,
            plugin_vendor="Maxon / Red Giant",
            plugin_package="Trapcode Suite",
            category="Particles / 3D / Light",
            is_third_party=True,
            is_builtin=False,
        )

    # 7. Maxon / Red Giant Universe & Magic Bullet
    if clean_mn.startswith("uni.") or lower_dn.startswith("uni."):
        return PluginClassification(
            match_name=clean_mn,
            display_name=clean_dn,
            plugin_vendor="Maxon / Red Giant",
            plugin_package="Universe",
            category=_infer_builtin_category(clean_mn, clean_dn),
            is_third_party=True,
            is_builtin=False,
        )
    if upper_mn.startswith("MBL") or "magic bullet" in lower_dn or "looks" == lower_dn or "optical compensation" not in lower_dn and "mojito" in lower_dn:
        return PluginClassification(
            match_name=clean_mn,
            display_name=clean_dn,
            plugin_vendor="Maxon / Red Giant",
            plugin_package="Magic Bullet Suite",
            category="Color / Looks",
            is_third_party=True,
            is_builtin=False,
        )

    # 8. Video Copilot (Element 3D, Optical Flares, Saber, Twitch, VC Color Vibrance, etc.)
    if (
        upper_mn.startswith("VIDEOCOPILOT")
        or upper_mn.startswith("VC ")
        or any(
            k in lower_dn
            for k in ("element", "optical flares", "saber", "color vibrance", "twitch", "sure target", "vc reflect")
        )
    ):
        pkg = "Video Copilot Plug-ins"
        cat = "3D / VFX"
        if "element" in lower_dn or "element" in clean_mn.lower():
            pkg = "Element 3D"
            cat = "3D Rendering / Objects"
        elif "flare" in lower_dn:
            pkg = "Optical Flares"
            cat = "Lighting / Flares"
        elif "saber" in lower_dn:
            pkg = "Saber"
            cat = "Energy / Glow Beams"
        elif "twitch" in lower_dn:
            pkg = "Twitch"
            cat = "Distort / Glitch / Shake"
        elif "vibrance" in lower_dn:
            pkg = "VC Color Vibrance"
            cat = "Color / Glow"
        return PluginClassification(
            match_name=clean_mn,
            display_name=clean_dn,
            plugin_vendor="Video Copilot",
            plugin_package=pkg,
            category=cat,
            is_third_party=True,
            is_builtin=False,
        )

    # 9. RE:Vision Effects (Twixtor, RSMB)
    if "twixtor" in lower_dn or "twixtor" in clean_mn.lower():
        return PluginClassification(
            match_name=clean_mn,
            display_name=clean_dn,
            plugin_vendor="RE:Vision Effects",
            plugin_package="Twixtor",
            category="Time / Optical Flow Retiming",
            is_third_party=True,
            is_builtin=False,
        )
    if "rsmb" in lower_dn or "rsmb" in clean_mn.lower() or "reelsmart" in lower_dn:
        return PluginClassification(
            match_name=clean_mn,
            display_name=clean_dn,
            plugin_vendor="RE:Vision Effects",
            plugin_package="ReelSmart Motion Blur (RSMB)",
            category="Blur / Motion Blur",
            is_third_party=True,
            is_builtin=False,
        )

    # 10. Rowbyte Plexus
    if "plexus" in lower_dn or "plexus" in clean_mn.lower():
        return PluginClassification(
            match_name=clean_mn,
            display_name=clean_dn,
            plugin_vendor="Rowbyte",
            plugin_package="Plexus",
            category="3D Particles / Lines",
            is_third_party=True,
            is_builtin=False,
        )

    # 11. Other third-party plugins (Frischluft, OLM, Signal, Newton, Lockdown, etc.)
    return PluginClassification(
        match_name=clean_mn,
        display_name=clean_dn,
        plugin_vendor="Third-Party / Custom Vendor",
        plugin_package=clean_dn if clean_dn else clean_mn,
        category=_infer_builtin_category(clean_mn, clean_dn),
        is_third_party=True,
        is_builtin=False,
    )
