import { readdir, readFile, writeFile } from 'node:fs/promises';
import { resolve } from 'path';
import { minify } from 'terser';

async function getFiles(directory) {
  const directoryEntries = await readdir(resolve(directory), { withFileTypes: true });
  const fileDirectoryEntries = directoryEntries.filter((x) => x.isFile());
  const files = fileDirectoryEntries.map(x => resolve(directory, x.name));
  return files;
}

async function getFilesRecursively(directory) {
  const directoryEntries = await readdir(resolve(directory), { withFileTypes: true });

  const files = [];

  for (const directoryEntry of directoryEntries) {
    const directoryEntryPath = resolve(directory, directoryEntry.name);
    if (directoryEntry.isFile()) {
      files.push(directoryEntryPath);
    } else if (directoryEntry.isDirectory()) {
      files.push(...(await getFilesRecursively(directoryEntryPath)));
    }
  }

  return files;
}

async function getAllFiles() {
  const regauthProtectedStatic = await getFiles("../protected_static/");
  const regauthProtectedStaticComponents = await getFilesRecursively("../protected_static/components/");

  const sharedProtectedStatic = await getFiles("../../fxweb/js/shared/protected_static/");
  const sharedProtectedStaticComponents = await getFilesRecursively("../../fxweb/js/shared/protected_static/components/");
  const sharedProtectedStaticDirectives = await getFilesRecursively("../../fxweb/js/shared/protected_static/directives/");

  return [
    regauthProtectedStatic,
    regauthProtectedStaticComponents,
    sharedProtectedStatic,
    sharedProtectedStaticComponents,
    sharedProtectedStaticDirectives,
  ].flat(Number.POSITIVE_INFINITY);
}

async function outputBuild() {
  let output = "";
  const files = await getAllFiles();
  for (const file of files) {
    if (file.endsWith(".js")) {
      output += await readFile(file, { encoding: 'utf8' });
    }
  }
  const minifiedOutput = (await minify(output)).code;
  const outputFilePath = "dist/regauth.js";
  await writeFile(outputFilePath, minifiedOutput);
  console.log(`Output saved at ${resolve(outputFilePath)}`);
}

async function main () {
  await outputBuild();
}

main();
