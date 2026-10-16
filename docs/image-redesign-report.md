# Image refresh report

## Implemented

- Replaced the four previous stock-photo homepage slides with six new profile-informed illustrative industrial images: automation conveyor, precision tightening, overhead crane, pump maintenance, Cartesian cell, and pick-to-light.
- Labeled hero visuals as illustrative concepts and updated the preload and social preview image.
- Removed the previous stock image files and the global hero-photo filter.
- Kept the images local as 1536 × 864 WebP files.
- Hid news cover photos in the homepage news preview so each CMS news photo is shown only on the news listing page.

## Source and limitations

The six new hero images were generated for this refresh. The company profile informed the visual themes; none of its original photographs were reused. The generated images are illustrative, not authentic NexAge project photography, and should not be presented as evidence of specific installations, products, people, awards, or customers.

## Site-wide image reuse

`image-inventory-before.csv` preserves the earlier inventory. `image-inventory-after.csv` lists local image files, byte sizes, source files that reference each filename, and source-level reference counts. This is not a complete rendered-placement audit. Shared catalog data and CMS-managed image URLs can still result in repeated photographs across other pages. The strict site-wide one-photo-per-placement requirement remains unverified and may require further catalog/page changes.

## Validation status

The last recorded frontend build passed before the fixes listed above. No build, browser, network, responsive, or backend check has been run after those fixes. The previous scan found no missing references among 64 local image files; runtime CMS URLs were not checked.
## Post-fix checks

- `npm run build` passed after the frontend fixes: TypeScript and Vite production build completed. Vite still reports an informational dynamic-import chunking warning for `src/api.ts`.
- The Python syntax-check command could not run because the configured Windows Python launcher was denied access to its target executable. No Django tests or runtime checks were run.
