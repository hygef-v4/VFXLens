"""Pydantic schemas for After Effects Project Analyzer (.aep / .aepx)."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from .common import AnalysisWarning, DataAvailabilityStatus, FieldProvenance


class ProjectMetadataSchema(BaseModel):
    """Project-level metadata and settings."""

    file_path: str
    file_name: str
    file_format: str = Field(..., description="'aep' (binary RIFX/RIFF) or 'aepx' (XML)")
    file_size_bytes: int
    sha256: str
    ae_version: str | None = None
    bits_per_channel: int | None = None
    working_space: str | None = None
    working_gamma: float | None = None
    linearize_working_space: bool | None = None
    compensate_for_scene_referred_profiles: bool | None = None
    time_display_type: str | None = None
    frames_count_type: str | None = None
    feet_frames_film_type: str | None = None
    audio_sample_rate: float | None = None
    expression_engine: str | None = None
    gpu_accel_type: str | None = None
    total_items: int = 0
    total_compositions: int = 0
    total_precompositions: int = 0
    total_footage_items: int = 0
    total_folders: int = 0
    render_queue_items_count: int = 0
    field_status: dict[str, DataAvailabilityStatus] = Field(default_factory=dict)


class KeyframeEasingSchema(BaseModel):
    """Temporal ease speed and influence for a single dimension."""

    speed: float
    influence: float


class KeyframeSchema(BaseModel):
    """Single keyframe on an After Effects property."""

    index: int = Field(..., description="1-based keyframe index matching AE scripting")
    time: float = Field(..., description="Keyframe timestamp in seconds (composition/layer time)")
    frame: float | None = Field(default=None, description="Frame number corresponding to time * comp_fps")
    value: Any = Field(default=None, description="Keyframe value (number, vector, color, shape, text, marker)")
    in_interpolation: str = Field(default="LINEAR", description="LINEAR, BEZIER, or HOLD")
    out_interpolation: str = Field(default="LINEAR", description="LINEAR, BEZIER, or HOLD")
    in_temporal_ease: list[KeyframeEasingSchema] = Field(default_factory=list)
    out_temporal_ease: list[KeyframeEasingSchema] = Field(default_factory=list)
    in_spatial_tangent: list[float] | None = None
    out_spatial_tangent: list[float] | None = None
    temporal_continuous: bool | None = None
    temporal_auto_bezier: bool | None = None
    spatial_continuous: bool | None = None
    spatial_auto_bezier: bool | None = None
    roving: bool | None = None
    label: int | str | None = None


class PropertySchema(BaseModel):
    """Recursive representation of an After Effects Property or PropertyGroup."""

    name: str
    match_name: str
    property_path: str
    property_type: str = Field(default="PROPERTY", description="PROPERTY, IndexedGroup, or NamedGroup")
    property_value_type: str | None = None
    control_type: str | None = None
    enabled: bool = True
    is_modified: bool = False
    is_time_varying: bool = False
    value: Any = None
    default_value: Any = None
    min_value: Any = None
    max_value: Any = None
    units_text: str | None = None
    property_parameters: list[str] | None = None
    keyframes_count: int = 0
    keyframes: list[KeyframeSchema] = Field(default_factory=list)
    expression_enabled: bool = False
    expression: str | None = None
    expression_error: str | None = None
    expression_evaluated_value_status: DataAvailabilityStatus = DataAvailabilityStatus.OBSERVED
    dimensions_separated: bool = False
    is_spatial: bool = False
    status: DataAvailabilityStatus = DataAvailabilityStatus.OBSERVED
    children: list[PropertySchema] = Field(default_factory=list)


class EffectParameterSchema(BaseModel):
    """Single parameter inside an Effect on a layer's Effect Stack."""

    index: int
    name: str
    match_name: str
    property_path: str
    control_type: str | None = None
    property_value_type: str | None = None
    value: Any = None
    default_value: Any = None
    min_value: Any = None
    max_value: Any = None
    units_text: str | None = None
    dropdown_options: list[str] | None = None
    is_modified: bool = False
    is_time_varying: bool = False
    keyframes_count: int = 0
    keyframes: list[KeyframeSchema] = Field(default_factory=list)
    expression_enabled: bool = False
    expression: str | None = None
    status: DataAvailabilityStatus = DataAvailabilityStatus.OBSERVED


class EffectInstanceSchema(BaseModel):
    """An effect applied in a layer's Effect Stack (`ADBE Effect Parade`)."""

    index: int = Field(..., description="1-based order in the layer's Effect Stack")
    name: str = Field(..., description="Instance name on the layer (may be renamed by user)")
    match_name: str = Field(..., description="Canonical AE matchName (e.g. 'S_Shake', 'Deep Glow', 'ADBE Gaussian Blur 2')")
    display_name: str | None = Field(default=None, description="Original effect definition display name")
    enabled: bool = True
    is_third_party: bool = False
    plugin_vendor: str | None = None
    plugin_package: str | None = None
    category: str | None = None
    is_missing_or_uninstalled_note: str | None = None
    parameters_count: int = 0
    modified_parameters_count: int = 0
    animated_parameters_count: int = 0
    parameters: list[EffectParameterSchema] = Field(default_factory=list)
    status: DataAvailabilityStatus = DataAvailabilityStatus.OBSERVED


class MaskSchema(BaseModel):
    """Mask applied to an AVLayer (`ADBE Mask Parade`)."""

    index: int
    name: str
    match_name: str = "ADBE Mask Atom"
    enabled: bool = True
    inverted: bool = False
    locked: bool = False
    roto_bezier: bool = False
    mask_mode: str | None = None
    mask_motion_blur: str | None = None
    color: list[float] | None = None
    is_path_animated: bool = False
    vertices_count: int | None = None
    closed: bool | None = None
    feather: Any = None
    opacity: Any = None
    expansion: Any = None
    properties: list[PropertySchema] = Field(default_factory=list)


class TransformSchema(BaseModel):
    """Layer Transform group (`ADBE Transform Group`) summary + full property details."""

    anchor_point: Any = None
    position: Any = None
    x_position: Any = None
    y_position: Any = None
    z_position: Any = None
    dimensions_separated: bool = False
    scale: Any = None
    orientation: Any = None
    rotation: Any = None
    x_rotation: Any = None
    y_rotation: Any = None
    z_rotation: Any = None
    opacity: Any = None
    properties: dict[str, PropertySchema] = Field(default_factory=dict)


class TextAnimatorSchema(BaseModel):
    """Text Animator (`ADBE Text Animator`) with selectors and animated properties."""

    name: str
    match_name: str
    selectors: list[PropertySchema] = Field(default_factory=list)
    animator_properties: list[PropertySchema] = Field(default_factory=list)


class TextLayerDetailSchema(BaseModel):
    """Typography, source text, and text animators for a TextLayer."""

    source_text: str | None = None
    font: str | None = None
    font_family: str | None = None
    font_style: str | None = None
    font_size: float | None = None
    fill_color: list[float] | None = None
    stroke_color: list[float] | None = None
    stroke_width: float | None = None
    apply_fill: bool | None = None
    apply_stroke: bool | None = None
    justification: str | None = None
    tracking: float | None = None
    leading: float | None = None
    is_box_text: bool | None = None
    three_d_per_char: bool = False
    is_source_text_animated: bool = False
    source_text_keyframes: list[KeyframeSchema] = Field(default_factory=list)
    animators: list[TextAnimatorSchema] = Field(default_factory=list)
    status: DataAvailabilityStatus = DataAvailabilityStatus.OBSERVED


class LayerSchema(BaseModel):
    """Complete representation of a layer inside a Composition."""

    index: int = Field(..., description="1-based layer index in the composition")
    id: int | None = None
    name: str
    layer_type: str = Field(
        ...,
        description="PrecompLayer, AdjustmentLayer, SolidLayer, NullLayer, FootageLayer, TextLayer, ShapeLayer, CameraLayer, LightLayer, ThreeDModelLayer, ParametricMeshLayer",
    )
    enabled: bool = True
    solo: bool = False
    shy: bool = False
    locked: bool = False
    is_null: bool = False
    is_adjustment_layer: bool = False
    is_three_d: bool = False
    is_guide_layer: bool = False
    collapse_transformation: bool = False
    motion_blur: bool = False
    effects_active: bool = True
    frame_blending_type: str | None = None
    quality: str | None = None
    sampling_quality: str | None = None
    blending_mode: str | None = None
    preserve_transparency: bool = False
    auto_orient: str | None = None
    label: int | str | None = None
    comment: str | None = None
    parent_index: int | None = None
    parent_name: str | None = None
    has_track_matte: bool = False
    is_track_matte: bool = False
    track_matte_type: str | None = None
    track_matte_layer_index: int | None = None
    track_matte_layer_name: str | None = None
    in_point: float = 0.0
    out_point: float = 0.0
    start_time: float = 0.0
    stretch: float = 100.0
    source_item_id: int | None = None
    source_item_name: str | None = None
    source_comp_name: str | None = None
    time_remapping_enabled: bool = False
    time_remap_property: PropertySchema | None = None
    transform: TransformSchema | None = None
    masks: list[MaskSchema] = Field(default_factory=list)
    effects: list[EffectInstanceSchema] = Field(default_factory=list)
    text_detail: TextLayerDetailSchema | None = None
    shape_contents: list[PropertySchema] = Field(default_factory=list)
    camera_options: list[PropertySchema] = Field(default_factory=list)
    light_options: list[PropertySchema] = Field(default_factory=list)
    material_options: list[PropertySchema] = Field(default_factory=list)
    layer_styles: list[PropertySchema] = Field(default_factory=list)
    essential_properties: list[PropertySchema] = Field(default_factory=list)
    markers: list[KeyframeSchema] = Field(default_factory=list)
    expressions_summary: list[dict[str, Any]] = Field(default_factory=list)
    animated_properties_summary: list[str] = Field(default_factory=list)
    status: DataAvailabilityStatus = DataAvailabilityStatus.OBSERVED


class CompositionSchema(BaseModel):
    """Composition or Precomposition item in the project."""

    item_id: int | None = None
    name: str
    comment: str | None = None
    parent_folder_path: str = "/"
    width: int
    height: int
    pixel_aspect: float = 1.0
    frame_rate: float
    duration: float
    work_area_start: float = 0.0
    work_area_duration: float = 0.0
    bg_color: list[float] = Field(default_factory=list)
    shutter_angle: int | float | None = None
    shutter_phase: int | float | None = None
    motion_blur: bool = False
    motion_blur_samples_per_frame: int | None = None
    motion_blur_adaptive_sample_limit: int | None = None
    frame_blending: bool = False
    preserve_nested_frame_rate: bool = False
    preserve_nested_resolution: bool = False
    drop_frame: bool = False
    hide_shy_layers: bool = False
    renderer: str | None = None
    is_precomp: bool = False
    used_in_compositions: list[str] = Field(default_factory=list)
    referenced_precomps: list[str] = Field(default_factory=list)
    layers_count: int = 0
    layers: list[LayerSchema] = Field(default_factory=list)
    markers: list[KeyframeSchema] = Field(default_factory=list)


class FootageDependencySchema(BaseModel):
    """Footage, Solid, Image Sequence, or Placeholder dependency in the project."""

    item_id: int | None = None
    name: str
    parent_folder_path: str = "/"
    asset_type: str = Field(..., description="file, image_sequence, solid, placeholder")
    file_path: str | None = None
    exists_on_disk: bool | None = None
    is_missing: bool = False
    missing_footage_path: str | None = None
    width: int | None = None
    height: int | None = None
    duration: float | None = None
    frame_rate: float | None = None
    has_alpha: bool | None = None
    solid_color: list[float] | None = None
    used_in_compositions: list[str] = Field(default_factory=list)


class PluginInventoryItemSchema(BaseModel):
    """Summary of an Effect/Plugin referenced anywhere in the project."""

    match_name: str
    display_name: str
    plugin_vendor: str
    plugin_package: str
    category: str
    is_third_party: bool
    is_builtin: bool
    occurrences_count: int = 0
    used_in_compositions: list[str] = Field(default_factory=list)
    used_on_layers: list[str] = Field(default_factory=list)
    note: str | None = None
    status: DataAvailabilityStatus = DataAvailabilityStatus.OBSERVED


class CompositionGraphEdgeSchema(BaseModel):
    """Directed edge in the composition/precomposition dependency graph."""

    parent_comp: str
    child_comp: str
    layer_index: int
    layer_name: str


class LayerRelationshipEdgeSchema(BaseModel):
    """Directed relationship between layers inside a composition."""

    composition_name: str
    source_layer_index: int
    source_layer_name: str
    target_layer_index: int | None = None
    target_layer_name: str
    relationship_type: str = Field(
        ...,
        description="parenting, track_matte, precomp_source, or effect_layer_param",
    )
    detail: str | None = None


class ProjectComparisonDiffSchema(BaseModel):
    """Difference entry when comparing Offline Parser output with Live AE Bridge output."""

    field_path: str
    offline_value: Any = None
    live_value: Any = None
    offline_status: DataAvailabilityStatus = DataAvailabilityStatus.OBSERVED
    live_status: DataAvailabilityStatus = DataAvailabilityStatus.OBSERVED
    comparison_result: str = Field(
        ...,
        description="matched, value_mismatch, only_in_offline, only_in_live, expected_runtime_difference",
    )
    explanation: str


class ProjectAnalysisResult(BaseModel):
    """Top-level normalized output schema for `project-analysis.json`."""

    schema_version: str = "1.0.0"
    analysis_id: str
    analyzed_at: str
    extraction_method: str = Field(
        ...,
        description="offline_py_aep, offline_aepx, live_ae_bridge, or hybrid_compared",
    )
    live_bridge_tested: bool = False
    live_bridge_status_note: str = ""
    rerun_command: str
    metadata: ProjectMetadataSchema
    compositions: list[CompositionSchema] = Field(default_factory=list)
    composition_hierarchy: list[CompositionGraphEdgeSchema] = Field(default_factory=list)
    layer_relationships: list[LayerRelationshipEdgeSchema] = Field(default_factory=list)
    plugin_inventory: list[PluginInventoryItemSchema] = Field(default_factory=list)
    dependencies: list[FootageDependencySchema] = Field(default_factory=list)
    missing_assets: list[FootageDependencySchema] = Field(default_factory=list)
    missing_effects: list[str] = Field(default_factory=list)
    expressions_inventory: list[dict[str, Any]] = Field(default_factory=list)
    warnings: list[AnalysisWarning] = Field(default_factory=list)
    unsupported_fields: list[FieldProvenance] = Field(default_factory=list)
    raw_summary: dict[str, Any] = Field(
        default_factory=dict,
        description="Raw chunk/item statistics for auditability and re-verification",
    )
    comparison_with_live: list[ProjectComparisonDiffSchema] | None = None


PropertySchema.model_rebuild()
