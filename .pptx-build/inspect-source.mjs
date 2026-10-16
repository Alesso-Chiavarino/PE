import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

async function writeBlob(path, blob) {
  await fs.writeFile(path, new Uint8Array(await blob.arrayBuffer()));
}

const source = "/Users/alesso/dev/ubp/PE/parcial_2/presentacion/Parcial-1-Programacion-Eficiente.pptx";
const output = "/Users/alesso/dev/ubp/PE/.pptx-build/source";
await fs.mkdir(output, { recursive: true });

const presentation = await PresentationFile.importPptx(await FileBlob.load(source));
const inspected = await presentation.inspect({
  select: "$.slides[*]",
  include: [
    "id",
    "index",
    "layout",
    "title",
    "elements.id",
    "elements.kind",
    "elements.text",
    "elements.position",
    "elements.style",
  ],
});
await fs.writeFile(`${output}/inspect.ndjson`, inspected.ndjson);

for (const [index, slide] of presentation.slides.items.entries()) {
  const png = await presentation.export({ slide, format: "png", scale: 1 });
  await writeBlob(`${output}/slide-${String(index + 1).padStart(2, "0")}.png`, png);
}

const montage = await presentation.export({ format: "webp", montage: true, scale: 0.5 });
await writeBlob(`${output}/montage.webp`, montage);

console.log(JSON.stringify({ slides: presentation.slides.items.length }));
