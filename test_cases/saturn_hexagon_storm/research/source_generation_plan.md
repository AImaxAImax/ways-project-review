# Source and generation plan — Saturn hexagon storm

## Constraint
Do not spend credits. Prefer NASA/public-domain source options. Use paid generators only after explicit authorization; this packet intentionally does not invoke them.

## NASA/public-domain source candidates
NASA image/media is generally not subject to U.S. copyright for non-commercial use, but NASA endorsement/logo rules still apply. Use NASA/JPL credit in internal notes/descriptions where appropriate and avoid NASA logos in plates.

| Priority | NASA ID | Title | Why it matters | Source URLs | Notes |
|---|---|---|---|---|---|
| 1 | PIA21052 | Over Saturn's Turbulent North | Best fact proof: NASA says the view shows part of the giant hexagon-shaped jet stream around Saturn's north pole; each side is about as wide as Earth; a circular storm lies at the center. | https://science.nasa.gov/resource/over-saturns-turbulent-north/ ; http://photojournal.jpl.nasa.gov/catalog/PIA21052 ; http://images-assets.nasa.gov/image/PIA21052/PIA21052~orig.jpg | Hero reference/source for Shot 03 and Shot 04. Crop must preserve hexagon read at phone size. |
| 2 | PIA17122 | Stormy North | Shows the area within Saturn's north polar hexagon with many storms and the polar vortex. | https://science.nasa.gov/resource/stormy-north/ ; http://photojournal.jpl.nasa.gov/catalog/PIA17122 ; http://images-assets.nasa.gov/image/PIA17122/PIA17122~orig.jpg | Use as proof plate or texture reference; good for inside-hexagon storm detail. |
| 3 | PIA14646 | Hexagon and Rings | Hexagon plus rings; useful to connect familiar Saturn rings to the weird north-pole hook. | http://images-assets.nasa.gov/image/PIA14646/PIA14646~orig.jpg | Potential opening/closing source crop if hexagon remains readable. |
| 4 | PIA20507 | Saturn Watercolor Swirls | Beautiful north polar bands/swirls; describes hexagon circumscribing the northern polar vortex. | https://science.nasa.gov/resource/saturn-watercolor-swirls/ ; http://photojournal.jpl.nasa.gov/catalog/PIA20507 ; http://images-assets.nasa.gov/image/PIA20507/PIA20507~orig.jpg | Atmosphere/texture plate, not primary proof of hexagon. |

## Recommended no-credit production lanes
1. NASA-source proof lane: download original Cassini images, crop/reframe vertically, add subtle push/pan/rotation only. This is the safest for accuracy and copyright.
2. Motion-graphic emphasis lane: create a clean hexagon outline/ring overlay from local vector/PIL only for internal timing prototype. Final should avoid non-caption labels; a non-text outline is acceptable if it does not misrepresent the source.
3. Local cinematic still lane: generate/compose locally only if source crops are too documentary/flat. Keep outputs grounded in NASA references and reject any invented text, spacecraft UI, fake labels, or logo-like artifacts.
4. Local I2V/Wan lane: animate approved stills with slow orbital camera move, cloud drift, and parallax. Do not create extreme storms, explosions, lightning, surface land, or fake spacecraft cockpits.

## Download commands for later source pull
```bash
mkdir -p test_cases/saturn_hexagon_storm/assets/source_nasa
python3 - <<'PY'
from pathlib import Path
import urllib.request
urls = {
  'PIA21052_orig.jpg': 'http://images-assets.nasa.gov/image/PIA21052/PIA21052~orig.jpg',
  'PIA17122_orig.jpg': 'http://images-assets.nasa.gov/image/PIA17122/PIA17122~orig.jpg',
  'PIA14646_orig.jpg': 'http://images-assets.nasa.gov/image/PIA14646/PIA14646~orig.jpg',
  'PIA20507_orig.jpg': 'http://images-assets.nasa.gov/image/PIA20507/PIA20507~orig.jpg',
}
out = Path('test_cases/saturn_hexagon_storm/assets/source_nasa')
for name, url in urls.items():
    urllib.request.urlretrieve(url, out / name)
PY
```

## Source QA notes
- Verify source image dimensions and visual read after vertical crop before Gate 2.
- Preserve citation metadata next to any downloaded source file.
- Do not use NASA insignia, mission patches, or UI labels as design elements.
