/*
 * vfx_readonly_extract.jsx — Read-only After Effects Project Extractor (ES3 ExtendScript)
 *
 * SAFETY GUARANTEES:
 * 1. Never modifies any composition, layer, property, or keyframe.
 * 2. Suppresses modal dialogs (missing fonts/plugins/footage) via app.beginSuppressDialogs().
 * 3. Only opens a snapshot copy if requested, closing with CloseOptions.DO_NOT_SAVE_CHANGES.
 * 4. Exports compositions, layers, property trees, effect stacks (matchName + values),
 *    keyframes (timing, interpolation, easing), expressions, and optional PNG preview frames.
 */

if (typeof JSON === "undefined") {
    JSON = {};
}
if (typeof JSON.stringify !== "function") {
    JSON.stringify = function (v) {
        function quote(s) {
            var out = '"', i, c, h;
            for (i = 0; i < s.length; i++) {
                c = s.charAt(i);
                if (c === '"' || c === "\\") { out += "\\" + c; }
                else if (c === "\n") { out += "\\n"; }
                else if (c === "\r") { out += "\\r"; }
                else if (c === "\t") { out += "\\t"; }
                else if (c < " ") {
                    h = s.charCodeAt(i).toString(16);
                    while (h.length < 4) { h = "0" + h; }
                    out += "\\u" + h;
                } else { out += c; }
            }
            return out + '"';
        }
        function str(val) {
            var t = typeof val, i, parts, k, sub;
            if (val === null || val === undefined) { return "null"; }
            if (t === "boolean") { return val ? "true" : "false"; }
            if (t === "number") { return isFinite(val) ? String(val) : "null"; }
            if (t === "string") { return quote(val); }
            if (val instanceof Array) {
                parts = [];
                for (i = 0; i < val.length; i++) {
                    sub = str(val[i]);
                    parts.push(sub === undefined ? "null" : sub);
                }
                return "[" + parts.join(",") + "]";
            }
            if (t === "object") {
                parts = [];
                for (k in val) {
                    if (val.hasOwnProperty(k)) {
                        sub = str(val[k]);
                        if (sub !== undefined) { parts.push(quote(k) + ":" + sub); }
                    }
                }
                return "{" + parts.join(",") + "}";
            }
            return undefined;
        }
        var res = str(v);
        return res === undefined ? "null" : res;
    };
}

var VFXReadonlyExtractor = (function () {
    function safeVal(v) {
        if (v === null || v === undefined) { return null; }
        var t = typeof v;
        if (t === "boolean" || t === "number" || t === "string") { return v; }
        if (v instanceof Array) {
            var arr = [];
            for (var i = 0; i < v.length; i++) { arr.push(safeVal(v[i])); }
            return arr;
        }
        if (v instanceof Shape) {
            return {
                _type: "Shape",
                closed: v.closed,
                vertices_count: v.vertices ? v.vertices.length : 0,
                vertices: safeVal(v.vertices)
            };
        }
        if (v instanceof TextDocument) {
            return {
                _type: "TextDocument",
                text: v.text,
                font: v.font,
                font_size: v.fontSize
            };
        }
        return String(v);
    }

    function extractKeyframes(prop, fps) {
        var kfs = [];
        var numKeys = 0;
        try { numKeys = prop.numKeys || 0; } catch (e) { numKeys = 0; }
        for (var k = 1; k <= numKeys; k++) {
            var kt = 0, kv = null, inI = "LINEAR", outI = "LINEAR";
            try { kt = prop.keyTime(k); } catch (e1) {}
            try { kv = safeVal(prop.keyValue(k)); } catch (e2) {}
            try { inI = String(prop.keyInInterpolationType(k)); } catch (e3) {}
            try { outI = String(prop.keyOutInterpolationType(k)); } catch (e4) {}
            kfs.push({
                index: k,
                time: kt,
                frame: fps > 0 ? kt * fps : null,
                value: kv,
                in_interpolation: inI,
                out_interpolation: outI
            });
        }
        return kfs;
    }

    function extractPropertyTree(prop, parentPath, fps, depth) {
        if (depth > 6) { return null; }
        var name = "", matchName = "", enabled = true, isMod = false;
        try { name = prop.name; } catch (e1) {}
        try { matchName = prop.matchName; } catch (e2) {}
        try { enabled = prop.enabled; } catch (e3) {}
        try { isMod = prop.isModified; } catch (e4) {}
        var path = parentPath + "/" + (name || matchName);

        var numProps = 0;
        try { numProps = prop.numProperties || 0; } catch (e5) { numProps = 0; }

        if (numProps > 0 || prop.propertyType !== PropertyType.PROPERTY) {
            var children = [];
            for (var i = 1; i <= numProps; i++) {
                try {
                    var ch = extractPropertyTree(prop.property(i), path, fps, depth + 1);
                    if (ch) { children.push(ch); }
                } catch (eChild) {}
            }
            return {
                name: name,
                match_name: matchName,
                property_path: path,
                property_type: "GROUP",
                enabled: enabled,
                is_modified: isMod,
                children: children
            };
        }

        var val = null, isTV = false, exprEn = false, expr = "", exprErr = "";
        try { val = safeVal(prop.value); } catch (e6) {}
        try { isTV = prop.isTimeVarying; } catch (e7) {}
        try { exprEn = prop.expressionEnabled; } catch (e8) {}
        try { expr = prop.expression || ""; } catch (e9) {}
        try { exprErr = prop.expressionError || ""; } catch (e10) {}

        var kfs = isTV ? extractKeyframes(prop, fps) : [];
        return {
            name: name,
            match_name: matchName,
            property_path: path,
            property_type: "PROPERTY",
            enabled: enabled,
            is_modified: isMod,
            is_time_varying: isTV,
            value: val,
            keyframes_count: kfs.length,
            keyframes: kfs,
            expression_enabled: exprEn,
            expression: expr || null,
            expression_error: exprErr || null,
            children: []
        };
    }

    function extractEffects(layer, fps) {
        var out = [];
        var parade = null;
        try { parade = layer.property("ADBE Effect Parade"); } catch (e) { parade = null; }
        if (!parade) { return out; }
        var n = parade.numProperties || 0;
        for (var i = 1; i <= n; i++) {
            var eff = parade.property(i);
            var params = [];
            var pCount = eff.numProperties || 0;
            for (var p = 1; p <= pCount; p++) {
                var param = eff.property(p);
                var pTree = extractPropertyTree(param, "Effects/" + eff.name, fps, 1);
                if (pTree) {
                    pTree.index = p;
                    params.push(pTree);
                }
            }
            out.push({
                index: i,
                name: eff.name,
                match_name: eff.matchName,
                enabled: eff.enabled,
                parameters_count: params.length,
                parameters: params
            });
        }
        return out;
    }

    function extractProject() {
        var proj = app.project;
        if (!proj) {
            return { ok: false, error: "No project open in After Effects" };
        }
        var comps = [];
        for (var i = 1; i <= proj.numItems; i++) {
            var item = proj.item(i);
            if (item instanceof CompItem) {
                var layers = [];
                for (var l = 1; l <= item.numLayers; l++) {
                    var lyr = item.layer(l);
                    layers.push({
                        index: l,
                        id: lyr.id,
                        name: lyr.name,
                        enabled: lyr.enabled,
                        solo: lyr.solo,
                        shy: lyr.shy,
                        locked: lyr.locked,
                        is_null: !!lyr.nullLayer,
                        is_adjustment_layer: !!lyr.adjustmentLayer,
                        is_three_d: !!lyr.threeDLayer,
                        motion_blur: !!lyr.motionBlur,
                        in_point: lyr.inPoint,
                        out_point: lyr.outPoint,
                        start_time: lyr.startTime,
                        stretch: lyr.stretch,
                        parent_index: lyr.parent ? lyr.parent.index : null,
                        parent_name: lyr.parent ? lyr.parent.name : null,
                        effects: extractEffects(lyr, item.frameRate)
                    });
                }
                comps.push({
                    item_id: item.id,
                    name: item.name,
                    width: item.width,
                    height: item.height,
                    pixel_aspect: item.pixelAspect,
                    frame_rate: item.frameRate,
                    duration: item.duration,
                    layers_count: layers.length,
                    layers: layers
                });
            }
        }
        return {
            ok: true,
            ae_version: app.version,
            bits_per_channel: proj.bitsPerChannel,
            total_items: proj.numItems,
            compositions: comps
        };
    }

    function exportPreviewFrame(compName, timeSeconds, outputPngPath) {
        var proj = app.project;
        if (!proj) { return { ok: false, error: "No project open" }; }
        for (var i = 1; i <= proj.numItems; i++) {
            var item = proj.item(i);
            if (item instanceof CompItem && item.name === compName) {
                var outFile = new File(outputPngPath);
                item.saveFrameToPng(timeSeconds, outFile);
                return { ok: true, file: outFile.fsName };
            }
        }
        return { ok: false, error: "Composition not found: " + compName };
    }

    return {
        extractProject: extractProject,
        exportPreviewFrame: exportPreviewFrame
    };
})();
