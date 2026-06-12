#!/usr/bin/env node
/**
 * Capture docs/assets/basic-amm-dashboard.png from the running Vite dev server.
 * Usage: VITE_DEMO_MODE=true npm run dev  (in app/) then node scripts/capture-dashboard-screenshot.mjs
 */
import { chromium } from "playwright";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), "..");
const outDir = path.join(root, "docs", "assets");
const outFile = path.join(outDir, "basic-amm-dashboard.png");
const url = process.env.DASHBOARD_URL ?? "http://127.0.0.1:5173";

const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1280, height: 900 } });

try {
  await page.goto(url, { waitUntil: "networkidle", timeout: 60000 });
  await page.waitForSelector("text=Adaptive AMM Dashboard", { timeout: 30000 });
  await page.waitForSelector("text=Current Price", { timeout: 30000 });
  await page.waitForTimeout(2500);
  await mkdir(outDir, { recursive: true });
  await page.screenshot({ path: outFile, fullPage: true });
  console.log(`Saved ${outFile}`);
} finally {
  await browser.close();
}
