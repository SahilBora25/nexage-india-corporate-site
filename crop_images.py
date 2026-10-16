from PIL import Image
from pathlib import Path

root = Path('/mnt/data')
out = Path('/mnt/data/nexage-site/public/images')
out.mkdir(parents=True, exist_ok=True)
collages = [
 'a_four_panel_industrial_collage_quad_layout_scene.png',
 'a_wide_collage_quad_panel_image_of_a_modern_indust.png',
 'a_high_resolution_collage_quad_panel_industrial_ma.png',
 'a_crisp_industrial_collage_quad_split_image_of_a_m.png',
 'a_clean_high_resolution_collage_quad_panel_indust.png',
 'a_clean_industrial_collage_photograph_in_a_2_2_gri.png',
 'a_high_resolution_realistic_industrial_factory_co.png',
 'a_clean_collage_quad_split_industrial_scene_a_sin.png',
 'a_clean_high_resolution_collage_image_in_a_2x2_gr.png',
 'a_clean_high_resolution_composite_collage_image_o.png',
]
names = [
 ['hero-factory','engineering-team','conveyor-line','pick-to-light'],
 ['conveyor-materials','overhead-crane','lift-table','manipulator'],
 ['automated-cell','jig-fixture','gantry-machine','fabrication'],
 ['condition-monitoring','industrial-dashboard','machine-vision','control-cabinet'],
 ['wireless-tx-rx','jidoka-poka-yoke','electric-torque-tool','electronics-testing'],
 ['industrial-tools','chain-hoist','lifting-hardware','tool-station'],
 ['maintenance-technician','machine-relocation','machine-refurbishment','commissioning-team'],
 ['automotive-industry','food-beverage','warehouse-logistics','precision-manufacturing'],
 ['engineering-design','guided-trolley','pressing-machine','industrial-integration'],
 ['cta-factory','robotic-cell-inspection','roller-conveyor-detail','assembly-line-overview'],
]
# Use safe inner edges to remove the thin collage gutters. All generated composites are 1536x1024.
for collage_name, labels in zip(collages, names):
    src = root / collage_name
    if not src.exists():
        raise FileNotFoundError(src)
    img = Image.open(src).convert('RGB')
    w, h = img.size
    # detect split at central axis; inset 5 px on either side of the divider
    xmid, ymid = w // 2, h // 2
    boxes = [
        (0, 0, xmid - 5, ymid - 5),
        (xmid + 5, 0, w, ymid - 5),
        (0, ymid + 5, xmid - 5, h),
        (xmid + 5, ymid + 5, w, h),
    ]
    for label, box in zip(labels, boxes):
        panel = img.crop(box)
        # Save two optimized modern web formats for responsive loading.
        target = out / f'{label}.webp'
        panel.save(target, 'WEBP', quality=84, method=6)
        print(target.name, panel.size, target.stat().st_size)
# Copy supplied logo as asset (not a company-profile photograph).
logo_src = root / 'WhatsApp Image 2026-09-26 at 1.48.29 PM.jpeg'
logo = Image.open(logo_src).convert('RGB')
logo.save(out / 'nexage-logo.webp', 'WEBP', quality=90, method=6)
print('logo', (out/'nexage-logo.webp').stat().st_size)
