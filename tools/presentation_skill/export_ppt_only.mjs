import fs from "node:fs/promises";
import path from "node:path";

import {
  createSlideContext,
  ensureArtifactToolWorkspace,
  importArtifactTool,
  importModuleFresh,
  parseArgs,
  parseSlideSize,
  requireArg,
  resolveSlideFunction,
  slideNumberFromModuleName,
} from "./artifact_tool_utils.mjs";

async function discoverSlideModules(slidesDir) {
  const entries = await fs.readdir(slidesDir);
  return entries
    .filter((entry) => /^slide[-_]?\d+\.mjs$/i.test(entry))
    .map((entry) => ({
      path: path.join(slidesDir, entry),
      slideNumber: slideNumberFromModuleName(entry),
    }))
    .sort((a, b) => a.slideNumber - b.slideNumber);
}

async function main() {
  const args = parseArgs(process.argv.slice(2));
  const slidesDir = path.resolve(requireArg(args, "slides-dir"));
  const out = path.resolve(requireArg(args, "out"));
  const workspace = path.resolve(args.workspace || path.dirname(slidesDir));
  const slideSize = parseSlideSize(args["slide-size"]);

  await ensureArtifactToolWorkspace(workspace);
  const artifact = await importArtifactTool(workspace);
  const { Presentation, PresentationFile } = artifact;
  const presentation = Presentation.create({ slideSize });
  const modules = await discoverSlideModules(slidesDir);

  for (const slideModule of modules) {
    const mod = await importModuleFresh(slideModule.path);
    const { fn } = resolveSlideFunction(mod, undefined, slideModule.slideNumber);
    const beforeCount = presentation.slides.count;
    const ctx = createSlideContext(artifact, {
      slideSize,
      slideNumber: slideModule.slideNumber,
      outputDir: path.dirname(out),
      assetDir: path.join(workspace, "assets"),
      workspaceDir: workspace,
    });
    await fn(presentation, ctx);
    if (presentation.slides.count !== beforeCount + 1) {
      throw new Error(`${path.basename(slideModule.path)} must add exactly one slide`);
    }
  }

  await fs.mkdir(path.dirname(out), { recursive: true });
  const pptx = await PresentationFile.exportPptx(presentation);
  await pptx.save(out);
  const stat = await fs.stat(out);
  console.log(JSON.stringify({ output: out, slideCount: presentation.slides.count, bytes: stat.size }, null, 2));
}

main().catch((error) => {
  console.error(error.stack || error.message || String(error));
  process.exit(1);
});
