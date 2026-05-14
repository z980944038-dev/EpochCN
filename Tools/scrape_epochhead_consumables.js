const fs = require("fs");
const path = require("path");
const { chromium } = require("/Users/macos/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");

const OUT_DIR = path.join(__dirname, "cache", "epochhead_consumables");
const OUT_FILE = path.join(OUT_DIR, "items.json");
const BASE = "https://epochhead.com/items?class=consumable";
const CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome";
const PROXY = process.env.EPOCHHEAD_PROXY && process.env.EPOCHHEAD_PROXY.trim() !== ""
  ? process.env.EPOCHHEAD_PROXY.trim()
  : undefined;
const WORKERS = Number(process.env.EPOCHHEAD_WORKERS || 4);
const DETAIL_LIMIT = Number(process.env.EPOCHHEAD_DETAIL_LIMIT || 0);
const USE_CACHE_LIST = process.env.EPOCHHEAD_USE_CACHE_LIST === "1";

fs.mkdirSync(OUT_DIR, { recursive: true });

function clean(text) {
  return String(text || "").replace(/\s+/g, " ").trim();
}

function decodeHtml(text) {
  return String(text || "")
    .replace(/&quot;/g, '"')
    .replace(/&#x27;/g, "'")
    .replace(/&#39;/g, "'")
    .replace(/&amp;/g, "&")
    .replace(/&lt;/g, "<")
    .replace(/&gt;/g, ">");
}

function loadExistingItems() {
  if (!fs.existsSync(OUT_FILE)) return new Map();
  try {
    const parsed = JSON.parse(fs.readFileSync(OUT_FILE, "utf8"));
    if (!Array.isArray(parsed)) return new Map();
    return new Map(parsed.filter((item) => item && item.id).map((item) => [Number(item.id), item]));
  } catch (error) {
    console.warn(`warn: failed to parse existing cache ${OUT_FILE}: ${error && error.message || error}`);
    return new Map();
  }
}

function isPlaceholderName(name) {
  return /^Item\s+\d+$/i.test(clean(name));
}

function isPlaceholderTooltip(tooltip) {
  const lines = Array.isArray(tooltip) ? tooltip.map((line) => clean(line)).filter(Boolean) : [];
  return lines.length === 1 && lines[0] === "Retrieving item information";
}

function isCompletedItem(item) {
  if (!item || item.error) return false;
  if (isPlaceholderName(item.name)) return false;
  if (!Array.isArray(item.tooltip) || item.tooltip.length === 0) return false;
  if (isPlaceholderTooltip(item.tooltip)) return false;
  return true;
}

function mergeItem(base, patch) {
  return {
    ...(base || {}),
    ...(patch || {}),
    id: Number((patch && patch.id) || (base && base.id)),
  };
}

function writeItems(items) {
  const out = Array.from(items.values()).sort((a, b) => a.id - b.id);
  fs.writeFileSync(OUT_FILE, JSON.stringify(out, null, 2), "utf8");
  return out;
}

function stripTags(html) {
  return decodeHtml(String(html || "").replace(/<script[\s\S]*?<\/script>/gi, "").replace(/<style[\s\S]*?<\/style>/gi, "").replace(/<[^>]+>/g, " "));
}

function pageUrl(pageNum) {
  return pageNum === 1 ? BASE : `${BASE}&page=${pageNum}`;
}

function itemUrl(id) {
  return `https://epochhead.com/?item=${id}`;
}

function parseTooltipLines(title, bodyText) {
  const lines = bodyText.split(/\r?\n/).map((line) => line.trim()).filter(Boolean);
  const indexes = [];
  lines.forEach((line, index) => {
    if (line === title) indexes.push(index);
  });

  let start = indexes.length ? indexes[0] : -1;
  for (const index of indexes) {
    const window = lines.slice(index + 1, index + 6).join("\n");
    if (/^(Consumable|Item Enhancement|Scroll|Food|Potion|Elixir|Flask|Bandage|Other)$/m.test(window) || /Item Level/.test(window)) {
      start = index;
      break;
    }
  }
  if (start < 0) return [];

  const result = [];
  for (let i = start + 1; i < lines.length; i++) {
    const line = clean(lines[i]);
    if (!line) continue;
    if (/^(Buy Price|Vendor Sell Price|AH Sell Price|Quick Facts|Copy In Game Link|Community Photos|Comments)$/.test(line)) break;
    if (/^Item Level\b/.test(line)) continue;
    if (line === "—") continue;
    if (/^(Consumable|Item Enhancement|Quest|Container|Projectile|Trade Goods)$/.test(line)) continue;
    result.push(line);
  }
  return result;
}

function parseMeta(html, name) {
  const titleMatch = html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);
  const metaMatch = html.match(/<meta\s+name="description"\s+content="([^"]*)"/i);
  const title = clean(decodeHtml(titleMatch ? titleMatch[1] : "").replace(/\s+—\s+EpochHead.*$/, "")) || name;
  const description = clean(decodeHtml(metaMatch ? metaMatch[1] : ""));
  return { title, description };
}

function parseMetaTooltip(title, description) {
  let text = clean(description);
  if (title && text.startsWith(title)) text = clean(text.slice(title.length));
  if (!text) return [];

  const marker = String.raw`(?=\s+(?:"|Use:|Equip:|Chance on hit:|Binds|Requires|Unique|Races:|Classes:|Artifact|Legendary|Epic|Rare|Uncommon|Common)\b|$)`;
  const pattern = new RegExp([
    String.raw`"[^"]*"`,
    String.raw`Use:.*?` + marker,
    String.raw`Equip:.*?` + marker,
    String.raw`Chance on hit:.*?` + marker,
    String.raw`Binds (?:to account|when picked up|when equipped|when used)`,
    String.raw`Requires Level \d+`,
    String.raw`Requires .*?` + marker,
    String.raw`Unique(?: \(\d+\))?`,
    String.raw`Races:.*?` + marker,
    String.raw`Classes:.*?` + marker,
    String.raw`Artifact|Legendary|Epic|Rare|Uncommon|Common`,
  ].join("|"), "gi");

  const result = [];
  let last = 0;
  let match;
  while ((match = pattern.exec(text))) {
    const before = clean(text.slice(last, match.index));
    if (before) result.push(before);
    result.push(clean(match[0]));
    last = pattern.lastIndex;
  }
  const tail = clean(text.slice(last));
  if (tail) result.push(tail);
  return result.filter(Boolean);
}

function parseListHtml(html) {
  const rows = new Map();
  const re = /<a[^>]+href="([^"]*[?&]item=(\d+)[^"]*)"[^>]*>([\s\S]*?)<\/a>/gi;
  let match;
  while ((match = re.exec(html))) {
    const id = Number(match[2]);
    const name = clean(stripTags(match[3]));
    if (!id || !name || /^Page \d+/i.test(name)) continue;
    const href = decodeHtml(match[1]);
    rows.set(id, { id, name, url: href.startsWith("http") ? href : `https://epochhead.com/${href.replace(/^\//, "")}` });
  }
  return Array.from(rows.values());
}

async function installRoutes(page) {
  await page.route("**/*", (route) => {
    const request = route.request();
    const type = request.resourceType();
    const url = request.url();
    if (type === "image" || type === "font" || type === "media") return route.abort();
    if (/doubleclick|googlesyndication|adservice|taboola|outbrain|meet.*single|singleflirt/i.test(url)) return route.abort();
    return route.continue();
  });
}

async function fetchViaPage(page, url) {
  return page.evaluate(async (target) => {
    const response = await fetch(target, { credentials: "include" });
    if (!response.ok) throw new Error(`${response.status} ${response.statusText}`);
    return response.text();
  }, url);
}

async function collectList(browser) {
  const page = await browser.newPage();
  await installRoutes(page);
  await page.goto("https://epochhead.com/", { waitUntil: "domcontentloaded", timeout: 60000 });
  const firstHtml = await fetchViaPage(page, BASE);
  const firstText = stripTags(firstHtml);
  const pageMatch = firstText.match(/Page\s+1\s+of\s+(\d+)/i);
  const totalPages = pageMatch ? Number(pageMatch[1]) : 22;
  const found = new Map();

  for (let pageNum = 1; pageNum <= totalPages; pageNum += 6) {
    const urls = [];
    for (let n = pageNum; n <= Math.min(totalPages, pageNum + 5); n++) urls.push(pageUrl(n));
    const htmls = await page.evaluate(async (targets) => Promise.all(targets.map(async (target) => {
      const response = await fetch(target, { credentials: "include" });
      if (!response.ok) throw new Error(`${response.status} ${target}`);
      return response.text();
    })), urls);
    htmls.forEach((html, offset) => {
      for (const item of parseListHtml(html)) found.set(item.id, item);
      console.log(`list page ${pageNum + offset}/${totalPages}: ${found.size}`);
    });
  }
  await page.close();
  return Array.from(found.values()).sort((a, b) => a.id - b.id);
}

async function fetchDetails(browser, list, existingItems) {
  async function newFetchPage() {
    const page = await browser.newPage();
    await installRoutes(page);
    await page.goto("https://epochhead.com/", { waitUntil: "domcontentloaded", timeout: 60000 });
    return page;
  }

  async function fetchChunk(page, chunk) {
    return page.evaluate(async (targets) => Promise.all(targets.map(async (target) => {
      const controller = new AbortController();
      const timer = setTimeout(() => controller.abort(), 20000);
      try {
        const response = await fetch(target.url, { credentials: "include", signal: controller.signal });
        if (!response.ok) return { error: `${response.status} ${response.statusText}` };
        return { html: await response.text() };
      } catch (error) {
        return { error: String(error && error.message || error) };
      } finally {
        clearTimeout(timer);
      }
    })), chunk);
  }

  const items = new Map();
  for (const item of list) {
    const cached = existingItems.get(item.id);
    items.set(item.id, mergeItem(item, cached ? mergeItem(item, cached) : item));
  }

  let queue = list.filter((item) => !isCompletedItem(items.get(item.id)));
  const resumed = list.length - queue.length;
  if (DETAIL_LIMIT > 0) queue = queue.slice(0, DETAIL_LIMIT);

  console.log(`detail queue: ${queue.length}/${list.length} (resumed ${resumed})`);
  if (!queue.length) return writeItems(items);

  let page = await newFetchPage();
  let processed = 0;
  for (let start = 0; start < queue.length; start += WORKERS) {
    const chunk = queue.slice(start, start + WORKERS);
    let htmls;
    try {
      htmls = await fetchChunk(page, chunk);
    } catch (error) {
      await page.close().catch(() => {});
      page = await newFetchPage();
      htmls = await fetchChunk(page, chunk);
    }
    for (let i = 0; i < chunk.length; i++) {
      const item = chunk[i];
      const payload = htmls[i];
      if (payload.error) {
        items.set(item.id, mergeItem(items.get(item.id), { ...item, tooltip: [], error: payload.error }));
        continue;
      }
      const meta = parseMeta(payload.html, item.name);
      let tooltip = parseMetaTooltip(meta.title, meta.description);
      if (!tooltip.length) {
        tooltip = parseTooltipLines(meta.title, stripTags(payload.html));
      }
      items.set(item.id, mergeItem(items.get(item.id), { ...item, name: meta.title || item.name, tooltip, error: undefined }));
    }
    processed += chunk.length;
    if (processed % 50 === 0 || processed >= queue.length) {
      console.log(`detail ${processed}/${queue.length}`);
    }
    writeItems(items);
  }
  await page.close();
  return writeItems(items);
}

async function main() {
  const existingItems = loadExistingItems();
  const browser = await chromium.launch({
    headless: true,
    executablePath: CHROME,
    proxy: PROXY ? { server: PROXY } : undefined,
  });

  if (existingItems.size) {
    console.log(`loaded cache: ${existingItems.size}`);
  }
  const list = USE_CACHE_LIST && existingItems.size
    ? Array.from(existingItems.values()).sort((a, b) => a.id - b.id)
    : await collectList(browser);
  if (USE_CACHE_LIST && existingItems.size) {
    console.log(`using cache list: ${list.length}`);
  }
  const out = await fetchDetails(browser, list, existingItems);
  await browser.close().catch(() => {});
  fs.writeFileSync(OUT_FILE, JSON.stringify(out, null, 2), "utf8");
  console.log(`wrote ${OUT_FILE}`);
}

main().then(() => process.exit(0)).catch((error) => {
  console.error(error);
  process.exit(1);
});
