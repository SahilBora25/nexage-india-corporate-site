# NexAge India image audit and correction report

Audit date: 2026-10-15

## Scope and method

Reviewed the website's static image catalogue in `src/data.ts`, direct homepage and content-page image assignments, image rendering and fallback logic in `src/components/Site.tsx`, CSS background image references, static assets under `public/images/`, and the public-image selection/fallback behavior in `src/hooks/usePublicList.ts`. Visual inspection covered the identified duplicate/mismatch groups and each newly generated replacement. Local file references were checked against files in `public/`.

The frontend uses `src/data.ts` for default product, solution, project, industry and service imagery. `usePublicList.ts` permits backend-managed `image_path` and `detail_image_path` values to override defaults. A live Django/database instance and admin-managed records were not available for visual inspection, so those dynamic values are outside this static audit.

## Corrected duplicate and mismatch groups

| Previous issue | Affected sections | Correction |
|---|---|---|
| Pick-to-Light, PLC, dashboard, electronics testing and control imagery had been reused across unlike topics. | Pick-to-Light solution, product and project; Jidoka solution/product/project; PLC monitoring; Industry 4.0; electronics testing. | Added distinct rack/operator and bin-detail images, a sensor-verified Poka-Yoke cell, an open PLC cabinet, a production dashboard and an electronics test bench. Updated the catalogue mappings to use the matching scene for each topic. |
| `fabrication.webp`, `jig-fixture.webp` and `smart-banner-background.webp` shared a pipework photograph. | Fabrication service; Jigs & Fixtures product/project; smart-manufacturing banners. | Retained the pipework photo for fabrication only. Added a dedicated assembly fixture. The smart banner now uses the industrial dashboard image; the broad solutions banner also uses the dashboard. |
| Torque-tool, tightening and precision pages reused similar generic equipment photography. | Home hero, industrial tools, torque tools, tightening solutions/project, precision manufacturing and Jigs & Fixtures. | Added separate tool-range, tool-in-use, and CMM inspection assets. Updated related product and project mappings. Battery Tools keeps its existing cordless-tool photograph. |
| Engineering-team and maintenance photographs were duplicated or showed only machinery. | Engineering solution, About, Contact, Quote, maintenance and refurbishment pages. | Added separate engineer CAD collaboration, CAD design and maintenance/pump inspection scenes. Updated static page and catalogue mappings. |
| The machine-relocation photo was a crane hook rather than a relocation operation. | MRO solution, machine-relocation project, service list and industrial-services industry. | Added a scene with the machine itself, rigging, machinery skates and a uniformed crew. The old hook image remains only for overhead lifting. |
| Automation-line, assembly-line and robotic-inspection entries reused robot/factory imagery. | Home hero, Industrial Automation solution, assembly/automotive content. | Added dedicated automotive robot-line and robotic machine-vision inspection scenes. Retained the existing assembly-line photo for Assembly & Production. |
| Engineering design, pump maintenance, food/beverage and condition monitoring shared unrelated stainless pipework. | Engineering, maintenance, Food & Beverage and Industry 4.0 pages. | Added distinct CAD, pump service, bottling-line and vibration-monitoring scenes. |
| Material handling, integration and commissioning reused conveyor photographs. | Material-handling capability, custom integration project and commissioning service. | Kept the appropriate conveyor image for material handling, added a distinct integrated machine-to-conveyor cell and added uniformed commissioning technicians. |
| Manipulator/cartesian/team imagery had incorrect subjects. | Material Handling Equipment detail; special-purpose machines; engineering pages. | Added a pneumatic manipulator scene and a true Cartesian gantry scene; engineering pages now use engineer imagery. |
| Factory, conveyor, poster and About imagery repeated the same production-line photograph. | Home hero, mobile poster fallback, About and industrial content. | Homepage About and hero now use the applicable generated subjects; the production-line poster remains only as a legacy responsive fallback. |

## Current corrected mappings

### Home and page-level images

| Affected page/slot | Previous image or problem | Current asset |
|---|---|---|
| Home hero â€” automation | Shared robot-line image | `automation-line-ai.jpg` |
| Home hero â€” precision assembly | CNC scene without a tightening task | `tool-in-use-ai.jpg` |
| Home hero â€” lifting | Crane-hook scene, still relevant to lifting | `hero-overhead-crane.webp` retained |
| Home hero â€” industrial service | Generic pipework | `hero-maintenance-pump-ai.jpg` |
| Home hero â€” custom automation | Generic robot arm rather than Cartesian motion | `gantry-machine-ai.jpg` |
| Home hero â€” smart kitting | Control/status close-up | `pick-to-light-rack.jpg` |
| Home About | Production-line photo, no engineers | `engineering-team-ai.jpg` |
| Home smart banner / Solutions landing | Repeated generic factory photo | `industrial-dashboard-ai.jpg` |
| About, Contact | Machinery image under team/company copy | `engineering-team-ai.jpg` |
| Quote | Generic factory/robot image | `engineering-design-ai.jpg` |
| Services landing | Generic factory image | `maintenance-technician-ai.jpg` |

### Solutions (`src/data.ts` image / detail / intro fields)

| Solution | Corrected image mapping |
|---|---|
| Industrial Automation | `automation-line-ai.jpg` / `robotic-inspection-ai.jpg` / `plc-monitoring-ai.jpg` |
| Conveyor & Material Handling | `conveyor-transfer.webp` / `lift-table-ai.jpg` / `conveyor-materials.webp` |
| Smart Manufacturing & Industry 4.0 | `industrial-dashboard-ai.jpg` / `condition-monitoring-ai.jpg` / `plc-monitoring-ai.jpg` |
| Pick-to-Light & Smart Kitting | `pick-to-light-rack.jpg` / `pick-to-light-detail.jpg` |
| Jidoka / Poka-Yoke | `jidoka-poka-yoke-ai.jpg` / `robotic-inspection-ai.jpg` / `plc-monitoring-ai.jpg` |
| Special Purpose Machines | `gantry-machine-ai.jpg` / `pressing-machine.webp` / `custom-press-cell.webp` |
| Engineering & Design | `engineering-team-ai.jpg` / `engineering-design-ai.jpg` / `commissioning-team-ai.jpg` |
| MRO & Industrial Services | `maintenance-technician-ai.jpg` / `machine-relocation-ai.jpg` / `commissioning-team-ai.jpg` |

### Products (`src/data.ts` image / detail / intro fields)

| Product | Final image mapping |
|---|---|
| NexAge Jidoka System | `jidoka-poka-yoke-ai.jpg` / `electronics-testing-ai.jpg` / `plc-monitoring-ai.jpg` |
| NexAge Wireless TX/RX | `wireless-tx-rx.webp` / `plc-monitoring-ai.jpg` / `electronics-testing-ai.jpg` |
| NexAge Pick-to-Light System | `pick-to-light-detail.jpg` / `pick-to-light-rack.jpg` |
| Cranes & Hoists | `chain-hoist.webp` / `overhead-crane.webp` / `lifting-hardware.webp` (retained) |
| Industrial Assembly Tools | `torque-tool-range-ai.jpg` / `tool-in-use-ai.jpg` / `torque-tool-range-ai.jpg` |
| Custom Machines | `custom-press-cell.webp` / `jig-fixture-ai.jpg` / `gantry-machine-ai.jpg` |
| Torque Tools | `torque-tool-range-ai.jpg` / `tool-in-use-ai.jpg` / `torque-tool-range-ai.jpg` |
| Battery Tools | `industrial-tools.webp` / `tool-in-use-ai.jpg` / `torque-tool-range-ai.jpg` |
| Jigs & Fixtures | `jig-fixture-ai.jpg` / `precision-inspection-ai.jpg` / `custom-press-cell.webp` |
| Material Handling Equipment | `guided-trolley.webp` / `conveyor-materials.webp` / `manipulator-ai.jpg` |
| Rail Systems | `lifting-hardware.webp` / `overhead-crane.webp` / `chain-hoist.webp` (retained) |
| Tightening Solutions | `tool-in-use-ai.jpg` / `torque-tool-range-ai.jpg` / `jidoka-poka-yoke-ai.jpg` |

### Projects (`src/data.ts` image / detail / intro fields)

| Project category | Final image mapping |
|---|---|
| Pick-to-Light for Smart Kitting | `pick-to-light-rack.jpg` / `pick-to-light-detail.jpg` |
| Jidoka / Poka-Yoke Workstation | `jidoka-poka-yoke-ai.jpg` / `electronics-testing-ai.jpg` / `plc-monitoring-ai.jpg` |
| IoT / PLC Monitoring | `plc-monitoring-ai.jpg` / `industrial-dashboard-ai.jpg` / `condition-monitoring-ai.jpg` |
| Conveyor & Lift Table Integration | `lift-table-ai.jpg` / `roller-conveyor-detail.webp` / `conveyor-transfer.webp` |
| Tightening Machine | `tool-in-use-ai.jpg` / `torque-tool-range-ai.jpg` / `jidoka-poka-yoke-ai.jpg` |
| Servo Cartesian & SPM | `gantry-machine-ai.jpg` / `pressing-machine.webp` / `custom-press-cell.webp` |
| Hoist & Rail Installation | `overhead-crane.webp` / `chain-hoist.webp` / `lifting-hardware.webp` (retained) |
| Machine Relocation Support | `machine-relocation-ai.jpg` / `machine-relocation-ai.jpg` / `commissioning-team-ai.jpg` |
| Condition Monitoring | `condition-monitoring-ai.jpg` / `industrial-dashboard-ai.jpg` / `plc-monitoring-ai.jpg` |
| Automated Conveyor Systems | `roller-conveyor-detail.webp` / `conveyor-materials.webp` / `conveyor-transfer.webp` (retained) |
| Jigs & Fixtures | `jig-fixture-ai.jpg` / `precision-inspection-ai.jpg` / `custom-press-cell.webp` |
| Sealing & Pressing Solutions | `pressing-machine.webp` / `gantry-machine.webp` / `custom-press-cell.webp` (retained) |
| Machine Refurbishment | `maintenance-technician-ai.jpg` / `hero-maintenance-pump-ai.jpg` / `condition-monitoring-ai.jpg` |
| Material Handling Systems | `conveyor-transfer.webp` / `lifting-hardware.webp` / `lift-table-ai.jpg` (retained) |
| Custom Industrial Solutions | `industrial-integration-ai.jpg` / `assembly-line-overview.webp` / `engineering-design-ai.jpg` |

### Industries and services

Automotive now uses `automation-line-ai.jpg`; Manufacturing & Machinery uses `gantry-machine-ai.jpg`; Food & Beverage uses `food-beverage-ai.jpg`; Industrial Services uses `machine-relocation-ai.jpg`; Engineering & Machinery uses `engineering-design-ai.jpg`. The warehouse, assembly and material-handling cards retain relevant warehouse/assembly/conveyor imagery.

Service cards now use: Preventive Maintenance `condition-monitoring-ai.jpg`; Installation & Commissioning `commissioning-team-ai.jpg`; Machinery Relocation `machine-relocation-ai.jpg`; Refurbishment & Troubleshooting `maintenance-technician-ai.jpg`; Fabrication & Pipeline Jobs `fabrication.webp` (retained because it shows industrial pipework); Line & Process Integration `industrial-integration-ai.jpg`.

## Verification and remaining limitations

- 24 generated JPEG files are present locally and recorded in `AI_IMAGE_GENERATION_LOG.md` and `public/IMAGE_SOURCES.md`.
- Source scan found 55 unique image filenames; all local assets resolved, including partner logos in `public/images/partners/`. The TONE partner logo remains externally referenced from the vendor site and was not availability-tested.
- The exact byte-duplicate stock files from the earlier asset set remain on disk under legacy names. Corrected page mappings now use distinct subject-specific assets for the affected pages; legacy files were left in place rather than removed.
- Pexels images documented in `public/IMAGE_SOURCES.md` remain generic stock photography. Generated scenes are visibly illustrative and are labeled as such on the homepage; they are not actual NexAge installations or people.
- Screenshot review later exposed stale database image paths overriding the corrected static images for known catalog entries. The frontend now prioritizes the local canonical image for known product, project, industry and service records while retaining API images for unknown entries. The local API was inspected and confirmed to still return the older image paths; the database itself was left unchanged.
- The frontend production build passes. A Django `manage.py check` was attempted, but the configured Python 3.14 executable was denied by the environment, so the backend check could not run. A complete browser screenshot review of every route and backend image override remains unverified; static mappings, local asset existence and the production build were checked.
