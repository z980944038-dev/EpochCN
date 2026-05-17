#!/usr/bin/env node
"use strict";

const fs = require("fs");
const path = require("path");

const ROOT = path.resolve(__dirname, "..");
const CACHE = path.join(ROOT, "Tools", "cache", "epochhead_items");
const OUT = path.join(CACHE, "items.json");
const LIST_CACHE = path.join(CACHE, "list.json");
const SNAPSHOT = path.join(ROOT, "SourceData", "EpochHead", "items");
const SNAPSHOT_OUT = path.join(SNAPSHOT, "items.json");
const SNAPSHOT_LIST = path.join(SNAPSHOT, "list.json");
const SNAPSHOT_MANIFEST = path.join(SNAPSHOT, "manifest.json");
const BASE = "https://epochhead.com";
const LIST_URL = `${BASE}/items`;
const USER_AGENT = "EpochCN-all-item-sync/0.2";
let requestTimeoutMs = 12000;
let requestRetries = 2;
let requestDelayMs = 0;

const ITEM_ROW_RE = /data-item-id="(?<id>\d+)"[\s\S]{0,700}?alt="(?<name>[^"]+)"[\s\S]{0,1400}?<td>(?<category>[\s\S]*?)<\/td><td>(?<slot>[\s\S]*?)<\/td><td[^>]*>(?<ilevel>[\s\S]*?)<\/td>/g;
const PAGE_RE = /Page\s+<!-- -->\d+<!-- -->\s+of\s+<!-- -->(\d+)/;
const GREEN_RE = /<li class="text-green-400">([\s\S]*?)<\/li>/g;
const TOOLTIP_UL_RE = /<ul class="list-none space-y-1">([\s\S]*?)<\/ul>/;
const TOOLTIP_LI_RE = /<li class="([^"]*)">([\s\S]*?)<\/li>/g;
const TITLE_RE = /<title[^>]*>([\s\S]*?)<\/title>/i;
const META_DESC_RE = /<meta\s+name="description"\s+content="([^"]*)"/i;

function argValue(name, fallback) {
  const index = process.argv.indexOf(name);
  if (index >= 0 && process.argv[index + 1]) return process.argv[index + 1];
  return fallback;
}

function hasArg(name) {
  return process.argv.includes(name);
}

function decodeEntities(text) {
  return String(text || "")
    .replace(/\\u0026/g, "&")
    .replace(/&quot;/g, '"')
    .replace(/&#39;|&apos;/g, "'")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">")
    .replace(/&amp;/g, "&")
    .replace(/&#(\d+);/g, (_, n) => String.fromCodePoint(Number(n)))
    .replace(/&#x([0-9a-f]+);/gi, (_, n) => String.fromCodePoint(parseInt(n, 16)));
}

function cleanHtml(value) {
  return decodeEntities(value)
    .replace(/<script[\s\S]*?<\/script>/gi, " ")
    .replace(/<style[\s\S]*?<\/style>/gi, " ")
    .replace(/<!--[\s\S]*?-->/g, " ")
    .replace(/<.*?>/g, " ")
    .replace(/\s+/g, " ")
    .trim();
}

async function fetchText(url, retries = requestRetries) {
  let lastError = null;
  for (let attempt = 0; attempt < retries; attempt += 1) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), requestTimeoutMs);
    try {
      const response = await fetch(url, {
        headers: { "user-agent": USER_AGENT },
        redirect: "follow",
        signal: controller.signal,
      });
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.text();
    } catch (error) {
      lastError = error;
      await new Promise(resolve => setTimeout(resolve, 400 + attempt * 800));
    } finally {
      clearTimeout(timer);
    }
  }
  throw new Error(`fetch failed for ${url}: ${lastError && lastError.message}`);
}

async function politeDelay(workerIndex) {
  if (requestDelayMs <= 0) return;
  const jitter = (workerIndex % 7) * 137;
  await new Promise(resolve => setTimeout(resolve, requestDelayMs + jitter));
}

function parseListPage(html) {
  const rows = [];
  for (const match of html.matchAll(ITEM_ROW_RE)) {
    const itemId = Number(match.groups.id);
    rows.push({
      id: itemId,
      name: cleanHtml(match.groups.name),
      category: cleanHtml(match.groups.category),
      slot: cleanHtml(match.groups.slot),
      ilevel: cleanHtml(match.groups.ilevel),
      url: `${BASE}/?item=${itemId}`,
    });
  }
  return rows;
}

function parsePageCount(html) {
  const match = PAGE_RE.exec(html);
  return match ? Number(match[1]) : 1;
}

function parseTitle(html, fallback) {
  const match = TITLE_RE.exec(html);
  if (!match) return fallback || "";
  return cleanHtml(match[1]).replace(/\s+—\s+EpochHead.*$/, "").trim() || fallback || "";
}

function parseMetaDescription(html) {
  const match = META_DESC_RE.exec(html);
  return match ? cleanHtml(match[1]) : "";
}

function parseGreenLines(html) {
  const seen = new Set();
  const lines = [];
  for (const match of html.matchAll(GREEN_RE)) {
    const line = cleanHtml(match[1]);
    if (line && !seen.has(line)) {
      seen.add(line);
      lines.push(line);
    }
  }
  return lines;
}

async function collectList(pageOverride) {
  const first = await fetchText(LIST_URL);
  const totalPages = pageOverride || parsePageCount(first);
  const found = new Map();
  for (const item of parseListPage(first)) found.set(item.id, item);
  console.log(`list page 1/${totalPages}: items=${found.size}`);

  const pages = [];
  for (let page = 2; page <= totalPages; page += 1) pages.push(page);
  let done = 1;
  await runQueue(pages, 12, async page => {
    const html = await fetchText(`${LIST_URL}?page=${page}`);
    for (const item of parseListPage(html)) found.set(item.id, item);
    done += 1;
    if (done % 25 === 0 || done === totalPages) {
      console.log(`list pages ${done}/${totalPages}: items=${found.size}`);
    }
  });

  const rows = [...found.entries()].sort((a, b) => a[0] - b[0]).map(([, item]) => item);
  writeJson(LIST_CACHE, rows);
  return rows;
}

function loadJson(file, fallback) {
  if (!fs.existsSync(file)) return fallback;
  try {
    return JSON.parse(fs.readFileSync(file, "utf8"));
  } catch {
    return fallback;
  }
}

function writeJson(file, rows) {
  fs.mkdirSync(path.dirname(file), { recursive: true });
  const tmp = `${file}.tmp`;
  fs.writeFileSync(tmp, `${JSON.stringify(rows, null, 2)}\n`);
  fs.renameSync(tmp, file);
}

function sha256(file) {
  const crypto = require("crypto");
  return crypto.createHash("sha256").update(fs.readFileSync(file)).digest("hex");
}

function writeSnapshotManifest() {
  if (!fs.existsSync(SNAPSHOT_LIST) || !fs.existsSync(SNAPSHOT_OUT)) return;
  const list = loadJson(SNAPSHOT_LIST, []);
  const items = loadJson(SNAPSHOT_OUT, []);
  const manifest = {
    source: LIST_URL,
    detailUrlPattern: `${BASE}/?item={id}`,
    capturedAt: new Date().toISOString().slice(0, 10),
    list: {
      file: "list.json",
      count: list.length,
      sha256: sha256(SNAPSHOT_LIST),
    },
    details: {
      file: "items.json",
      count: items.length,
      greenItemCount: items.filter(row => row.green && row.green.length).length,
      errorCount: items.filter(row => row.error).length,
      sha256: sha256(SNAPSHOT_OUT),
    },
    schema: {
      list: ["id", "name", "category", "slot", "ilevel", "url"],
      details: ["id", "name", "category", "slot", "ilevel", "url", "description", "tooltip", "green"],
    },
    notes: [
      "list.json is the complete 335-page EpochHead item index captured from /items.",
      "items.json is an incremental detail snapshot. It is intentionally committed so future localization work can reuse it without re-scraping completed items.",
      "Rows with fetch errors are excluded; missing detail rows should be resumed by Tools/scrape_epochhead_items.js.",
    ],
  };
  writeJson(SNAPSHOT_MANIFEST, manifest);
}

function writeDurableJson(cacheFile, snapshotFile, rows) {
  writeJson(cacheFile, rows);
  writeJson(snapshotFile, rows);
  writeSnapshotManifest();
}

function loadExistingDetails() {
  const merged = new Map();
  for (const rows of [loadJson(SNAPSHOT_OUT, []), loadJson(OUT, [])]) {
    for (const row of rows) {
      if (row && row.id && !row.error) merged.set(Number(row.id), row);
    }
  }
  const rows = [...merged.entries()].sort((a, b) => a[0] - b[0]).map(([, row]) => row);
  const details = new Map();
  for (const row of rows) {
    if (row && row.id && !row.error) details.set(Number(row.id), row);
  }
  return details;
}

function classifyTooltipText(text) {
  if (/^\(\d+\)\s*Set:/.test(text)) return "green";
  if (/^(Use|Equip|Chance on hit):/.test(text)) return "green";
  if (/^"[^"]+"$/.test(text)) return "yellow";
  return "normal";
}

function tooltipColor(className) {
  if (/text-green-400/.test(className)) return "green";
  if (/text-yellow|text-amber/.test(className)) return "yellow";
  if (/text-gray|text-neutral|muted/.test(className)) return "gray";
  if (/text-red/.test(className)) return "red";
  return "normal";
}

function parseTooltipLines(html) {
  const match = TOOLTIP_UL_RE.exec(html);
  if (!match) return [];
  const result = [];
  for (const lineMatch of match[1].matchAll(TOOLTIP_LI_RE)) {
    const className = lineMatch[1] || "";
    const text = cleanHtml(lineMatch[2]);
    if (!text) continue;
    result.push({
      text,
      color: tooltipColor(className),
      className,
    });
  }
  if (result.some(line => /Retrieving item information/i.test(line.text))) return [];
  return result;
}

function parseMetaTooltip(title, description) {
  let text = cleanHtml(description || "");
  if (title && text.startsWith(title)) text = cleanHtml(text.slice(title.length));
  if (!text || /Retrieving item information/i.test(text)) return [];

  const marker = String.raw`(?=\s+(?:"|Use:|Equip:|Chance on hit:|Binds|Requires|Unique|Races:|Classes:|Item Level|Speed|[0-9,.]+ - [0-9,.]+ Damage|\([0-9,.]+ damage per second\)|\+[0-9,.]+ )\b|$)`;
  const pattern = new RegExp([
    String.raw`"[^"]*"`,
    String.raw`Use:.*?` + marker,
    String.raw`Equip:.*?` + marker,
    String.raw`Chance on hit:.*?` + marker,
    String.raw`Binds (?:to account|when picked up|when equipped|when used)`,
    String.raw`Unique(?:-Equipped)?(?: \(\d+\))?`,
    String.raw`One-Hand|Two-Hand|Main Hand|Off Hand|Held In Off-hand|Ranged|Thrown`,
    String.raw`Speed [0-9.]+`,
    String.raw`[0-9,.]+ - [0-9,.]+ Damage`,
    String.raw`\([0-9,.]+ damage per second\)`,
    String.raw`\+[0-9,.]+ [A-Za-z ]+`,
    String.raw`Requires Level \d+`,
    String.raw`Requires .*?` + marker,
    String.raw`Item Level \d+`,
    String.raw`Races:.*?` + marker,
    String.raw`Classes:.*?` + marker,
  ].join("|"), "gi");

  const rows = [];
  const seen = new Set();
  let match;
  while ((match = pattern.exec(text))) {
    const line = cleanHtml(match[0]);
    if (line && !seen.has(line)) {
      seen.add(line);
      rows.push({ text: line, color: classifyTooltipText(line), className: "" });
    }
  }
  return rows;
}

async function fetchDetail(item) {
  const html = await fetchText(item.url);
  const title = parseTitle(html, item.name || "");
  const description = parseMetaDescription(html);
  let tooltip = parseTooltipLines(html);
  if (!tooltip.length) tooltip = parseMetaTooltip(title, description);
  return {
    ...item,
    name: title,
    description,
    tooltip,
    green: tooltip.filter(line => line.color === "green" || classifyTooltipText(line.text) === "green").map(line => line.text).concat(parseGreenLines(html))
      .filter((line, index, lines) => line && lines.indexOf(line) === index),
  };
}

async function runQueue(items, workers, task) {
  let next = 0;
  async function worker(workerIndex) {
    while (next < items.length) {
      const index = next;
      next += 1;
      await task(items[index], index, workerIndex);
    }
  }
  await Promise.all(Array.from({ length: Math.max(1, workers) }, (_, index) => worker(index)));
}

async function main() {
  const workers = Number(argValue("--workers", "64"));
  requestTimeoutMs = Number(argValue("--timeout-ms", String(requestTimeoutMs)));
  requestRetries = Number(argValue("--retries", String(requestRetries)));
  requestDelayMs = Number(argValue("--delay-ms", "0"));
  const pageOverride = argValue("--pages", null);
  fs.mkdirSync(CACHE, { recursive: true });

  const existing = loadExistingDetails();
  if (existing.size) {
    const rows = [...existing.entries()].sort((a, b) => a[0] - b[0]).map(([, value]) => value);
    writeDurableJson(OUT, SNAPSHOT_OUT, rows);
  }
  if (hasArg("--prune-only")) {
    console.log(`pruned cache: items=${existing.size}`);
    return;
  }

  const items = hasArg("--reuse-list") && (fs.existsSync(LIST_CACHE) || fs.existsSync(SNAPSHOT_LIST))
    ? loadJson(LIST_CACHE, loadJson(SNAPSHOT_LIST, []))
    : await collectList(pageOverride ? Number(pageOverride) : null);
  if (items.length) writeDurableJson(LIST_CACHE, SNAPSHOT_LIST, items);

  const details = loadExistingDetails();
  const todo = items.filter(item => {
    const row = details.get(Number(item.id));
    return !row || row.error || !row.tooltip;
  });
  console.log(`detail queue: ${todo.length}/${items.length}`);

  let done = 0;
  let failed = 0;
  await runQueue(todo, workers, async (item, _index, workerIndex) => {
    let row;
    try {
      await politeDelay(workerIndex);
      row = await fetchDetail(item);
      details.set(Number(row.id), row);
    } catch (error) {
      failed += 1;
    }
    done += 1;
    if (done % 100 === 0 || done === todo.length) {
      const rows = [...details.entries()].sort((a, b) => a[0] - b[0]).map(([, value]) => value);
      writeDurableJson(OUT, SNAPSHOT_OUT, rows);
      console.log(`detail ${done}/${todo.length} complete=${details.size}/${items.length} failed=${failed}`);
    }
  });

  const rows = [...details.entries()].sort((a, b) => a[0] - b[0]).map(([, value]) => value);
  writeDurableJson(OUT, SNAPSHOT_OUT, rows);
  const greenItems = rows.filter(row => row.green && row.green.length).length;
  console.log(`wrote ${OUT}`);
  console.log(`items=${rows.length} green_items=${greenItems} pending=${items.length - rows.length}`);
}

main().catch(error => {
  console.error(error);
  process.exit(1);
});
