import assert from "node:assert/strict";
import { afterEach, test } from "node:test";
import { fetchDetections } from "./detectionApi.js";
import {
  classificationLabel,
  detectionStyle,
  detectionSummary,
  formatConfidence,
  formatCoordinates,
  formatDetectionTime,
} from "../utils/detectionFormat.js";

// #18: the map shows location, timestamp and confidence for each detection
// returned by GET /api/detections (#17). Server side: backend/tests/test_detection_pipeline.py.
const originalFetch = globalThis.fetch;
afterEach(() => { globalThis.fetch = originalFetch; });

const sample = {
  status: "success",
  source: "database",
  threshold: 20,
  detections: [
    { id: 1, latitude: 50.1, longitude: -120.3, timestamp: "2025-07-01T18:30:00Z", confidence: 80, classification: "potential_wildfire", meets_threshold: true },
    { id: 2, latitude: 50.2, longitude: -120.4, timestamp: "2025-07-01T18:35:00Z", confidence: 10, classification: "low_confidence", meets_threshold: false },
  ],
  gaps: [{ id: 3, reason: "Missing required field: latitude" }],
  counts: { total: 3, shown: 2, potential_wildfire: 1, low_confidence: 1, unavailable: 1 },
};

test("#18 fetches detections from Flask with the requested limit", async () => {
  let requestedUrl;
  globalThis.fetch = async (url) => {
    requestedUrl = url;
    return { ok: true, json: async () => sample };
  };
  const result = await fetchDetections(50);
  assert.equal(requestedUrl, "http://127.0.0.1:5000/api/detections?limit=50");
  assert.deepEqual(result.detections, sample.detections);
});

test("#18 rejects unsuccessful responses instead of showing stale detections", async () => {
  globalThis.fetch = async () => ({ ok: false, status: 503 });
  await assert.rejects(fetchDetections(), /503/);
});

test("#18 rejects malformed detection data", async () => {
  globalThis.fetch = async () => ({ ok: true, json: async () => ({ status: "success", detections: null }) });
  await assert.rejects(fetchDetections(), /Invalid detection data/);
});

test("#18 propagates network failures", async () => {
  globalThis.fetch = async () => { throw new TypeError("Failed to fetch"); };
  await assert.rejects(fetchDetections(), /Failed to fetch/);
});

test("#18 shows time with the zone labelled", () => {
  assert.match(formatDetectionTime("2025-07-01T18:30:00Z", "UTC"), /Jul 1, 2025.*UTC/);
  assert.match(formatDetectionTime("2025-07-01T18:30:00Z", "America/Toronto"), /2:30.*(EDT|GMT-4)/);
});

test("#18 reports unavailable time instead of inventing one", () => {
  assert.equal(formatDetectionTime("not a date"), "Time unavailable");
});

test("#18 formats location and confidence", () => {
  assert.equal(formatCoordinates(50.1, -120.3), "50.100, -120.300");
  assert.equal(formatConfidence(79.6), "80%");
  assert.equal(formatConfidence(null), "Unavailable");
});

test("#18 low-confidence detections look different from likely ones", () => {
  const likely = detectionStyle(sample.detections[0]);
  const low = detectionStyle(sample.detections[1]);
  assert.notEqual(likely.fillColor, low.fillColor);
  assert.ok(low.fillOpacity < likely.fillOpacity);
  assert.equal(classificationLabel(sample.detections[0]), "Potential wildfire");
  assert.equal(classificationLabel(sample.detections[1]), "Low confidence detection");
});

test("#18 summary mentions detections that could not be shown", () => {
  const text = detectionSummary(sample);
  assert.match(text, /2 detections shown: 1 potential wildfire, 1 low confidence \(threshold 20%\)/);
  assert.match(text, /1 could not be shown/);
});
