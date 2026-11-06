import fs from "node:fs/promises";
import { FileBlob, PresentationFile } from "@oai/artifact-tool";

const input = "/Users/alesso/dev/ubp/PE/parcial_2/presentacion/Parcial-2-Mejoras-Programacion-Eficiente.pptx";
const output = "/Users/alesso/dev/ubp/PE/.pptx-build/parcial2-final-render";
await fs.mkdir(output, { recursive: true });
const presentation = await PresentationFile.importPptx(await FileBlob.load(input));
for (const [index, slide] of presentation.slides.items.entries()) {
  const png = await presentation.export({ slide, format: "png", scale: 1 });
  await fs.writeFile(`${output}/slide-${String(index + 1).padStart(2, "0")}.png`, new Uint8Array(await png.arrayBuffer()));
}
const montage = await presentation.export({ format: "webp", montage: true, scale: 0.4 });
await fs.writeFile(`${output}/montage.webp`, new Uint8Array(await montage.arrayBuffer()));
console.log(JSON.stringify({ slides: presentation.slides.items.length }));
