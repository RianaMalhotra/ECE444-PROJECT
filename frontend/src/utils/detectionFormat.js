// #18: wording and styling helpers for detection markers.
// Kept out of App.jsx so they can be unit tested without a browser.

export const LOW_CONFIDENCE = "low_confidence";

// Timestamps are stored in UTC and shown in the viewer's local time with the
// zone labelled (docs/requirements.md, Data Sources and Provenance).
export function formatDetectionTime(isoString, timeZone) {
  const date = new Date(isoString);
  if (Number.isNaN(date.getTime())) return "Time unavailable";

  return new Intl.DateTimeFormat("en-CA", {
    // dateStyle/timeStyle can't be combined with timeZoneName, so spell out the fields.
    year: "numeric",
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
    timeZoneName: "short",
    ...(timeZone ? { timeZone } : {}),
  }).format(date);
}

export function formatCoordinates(latitude, longitude) {
  return `${latitude.toFixed(3)}, ${longitude.toFixed(3)}`;
}

export function formatConfidence(confidence) {
  return typeof confidence === "number" ? `${Math.round(confidence)}%` : "Unavailable";
}

// Low-confidence detections must look different from the rest, not identical.
export function detectionStyle(detection) {
  if (detection.classification === LOW_CONFIDENCE) {
    return { color: "#6b7280", fillColor: "#9ca3af", fillOpacity: 0.25, dashArray: "3 3", radius: 5 };
  }
  return { color: "#b91c1c", fillColor: "#ef4444", fillOpacity: 0.85, dashArray: null, radius: 7 };
}

export function classificationLabel(detection) {
  return detection.classification === LOW_CONFIDENCE
    ? "Low confidence detection"
    : "Potential wildfire";
}

// One line for the status banner, including rows that could not be shown.
export function detectionSummary(result) {
  const counts = result.counts || {};
  const shown = counts.shown ?? result.detections.length;
  const likely = counts.potential_wildfire ?? 0;
  const low = counts.low_confidence ?? 0;
  const unavailable = counts.unavailable ?? 0;

  let text = `${shown} detections shown: ${likely} potential wildfire, ${low} low confidence (threshold ${result.threshold}%).`;
  if (unavailable > 0) {
    text += ` ${unavailable} could not be shown because their data is missing or invalid.`;
  }
  return text;
}
