import catalogueImages from './catalogue-images.json';
export type CatalogItem = {
  title: string; slug: string; path: string; description: string; image: string; detailImage?: string; introImage?: string;
  eyebrow?: string; category?: string; features?: string[]; type?: 'NexAge Solution' | 'Partner Product' | 'Integrated Solution';
  industry?: string; challenge?: string; solution?: string; application?: string; technology?: string; result?: string;
};


function withCatalogueImages<T extends { slug: string }>(items: T[], imageMap: Record<string, string>): Array<T & { image: string }> {
  return items.map(item => {
    const image = imageMap[item.slug];
    if (!image) throw new Error(`Missing catalogue image mapping for ${item.slug}`);
    return { ...item, image };
  });
}

export const solutions: CatalogItem[] = [
  { title: 'Industrial Automation', slug: 'industrial-automation', path: '/solutions/industrial-automation', description: 'Connect machines, control systems and production steps into reliable industrial workflows.', image: 'automation-line-ai.jpg', detailImage: 'robotic-inspection-ai.jpg', introImage: 'plc-monitoring-ai.jpg', features: ['Plant and assembly-line automation', 'PLC-based control integration', 'HMI / SCADA integration where applicable', 'Sensors, actuators and industrial networking', 'Commissioning and troubleshooting'] },
  { title: 'Conveyor & Material Handling', slug: 'conveyor-material-handling', path: '/solutions/conveyor-material-handling', description: 'Move products and components through production with engineered conveyor and lifting systems.', image: 'conveyor-transfer.webp', detailImage: 'lift-table-ai.jpg', introImage: 'conveyor-materials.webp', features: ['Automated conveyor systems', 'Lift tables and guided trolleys', 'XY / KBK rail systems and manipulators', 'Dock levelers, custom trolleys and industrial structures', 'Material-handling integration'] },
  { title: 'Smart Manufacturing & Industry 4.0', slug: 'smart-manufacturing', path: '/solutions/smart-manufacturing', description: 'Make production information more visible with connected monitoring and data-driven systems.', image: 'industrial-dashboard-ai.jpg', detailImage: 'condition-monitoring-ai.jpg', introImage: 'plc-monitoring-ai.jpg', features: ['Industrial IoT and PLC monitoring', 'Condition monitoring', 'Data-driven production visibility', 'LoRaWAN-related services'] },
  { title: 'Pick-to-Light & Smart Kitting', slug: 'pick-to-light', path: '/solutions/pick-to-light', description: 'Guide operators to the right component with illuminated picking points and clear workstation feedback.', image: 'pick-to-light-rack.jpg', detailImage: 'pick-to-light-detail.jpg', features: ['Guided material picking', 'Electronic shelf indicators', 'Operator guidance', 'Smart kitting and material identification'] },
  { title: 'Jidoka / Poka-Yoke', slug: 'jidoka-poka-yoke', path: '/solutions/jidoka-poka-yoke', description: 'Help prevent process errors with monitored workstations, controls, sensors and clear status feedback.', image: 'jidoka-poka-yoke-ai.jpg', detailImage: 'robotic-inspection-ai.jpg', introImage: 'plc-monitoring-ai.jpg', features: ['Process monitoring', 'Error-prevention logic', 'Torque-tool and sensor integration', 'Visual status indication'] },
  { title: 'Special Purpose Machines', slug: 'special-purpose-machines', path: '/solutions/special-purpose-machines', description: 'Custom machinery and fixtures designed around a defined production task and process need.', image: 'gantry-machine-ai.jpg', detailImage: 'pressing-machine.webp', introImage: 'custom-press-cell.webp', features: ['Customized production machines', 'Servo Cartesian systems', 'Tightening, sealing and pressing machines', 'Jigs, fixtures and custom automation'] },
  { title: 'Engineering & Design', slug: 'engineering', path: '/solutions/engineering', description: 'Take an engineering requirement from concept and layout through build, integration and commissioning.', image: 'engineering-team-ai.jpg', detailImage: 'engineering-design-ai.jpg', introImage: 'commissioning-team-ai.jpg', features: ['Conveyor and workstation design', 'Mechanical and process engineering', 'Turnkey project coordination', 'Manufacturing and commissioning support'] },
  { title: 'MRO & Industrial Services', slug: 'mro-services', path: '/solutions/mro-services', description: 'Support operating plants with maintenance, installation, relocation, refurbishment and troubleshooting.', image: 'maintenance-technician-ai.jpg', detailImage: 'machine-relocation-ai.jpg', introImage: 'commissioning-team-ai.jpg', features: ['Preventive maintenance and AMC', 'Machinery relocation', 'Machine refurbishment', 'Installation and commissioning'] },
];

const productDefinitions: Array<Omit<CatalogItem, 'image'>> = [
  { title: 'NexAge Jidoka System', slug: 'jidoka', path: '/products/jidoka', description: 'A process monitoring and error-prevention system for industrial assembly applications.', detailImage: 'electronics-testing-ai.jpg', introImage: 'plc-monitoring-ai.jpg', type: 'NexAge Solution', category: 'Smart Manufacturing' },
  { title: 'NexAge Wireless TX/RX', slug: 'wireless-tx-rx', path: '/products/wireless-tx-rx', description: 'A wireless transmitter and receiver concept for industrial signal triggering and integration.', detailImage: 'plc-monitoring-ai.jpg', introImage: 'electronics-testing-ai.jpg', type: 'NexAge Solution', category: 'Wireless Systems' },
  { title: 'NexAge Pick-to-Light System', slug: 'pick-to-light', path: '/products/pick-to-light', description: 'Illuminated picking points support guided material identification and smart kitting.', detailImage: 'pick-to-light-rack.jpg', type: 'NexAge Solution', category: 'Smart Manufacturing' },
  { title: 'Cranes & Hoists', slug: 'cranes-hoists', path: '/products/cranes-hoists', description: 'Lifting and material-handling solutions through authorized partner product offerings and integration.', detailImage: 'overhead-crane.webp', introImage: 'lifting-hardware.webp', type: 'Partner Product', category: 'Material Handling' },
  { title: 'Industrial Assembly Tools', slug: 'industrial-tools', path: '/products/industrial-tools', description: 'Electric, battery-powered and precision tightening tools for industrial assembly applications.', detailImage: 'tool-in-use-ai.jpg', introImage: 'torque-tool-range-ai.jpg', type: 'Partner Product', category: 'Industrial Tools' },
  { title: 'Custom Machines', slug: 'custom-machines', path: '/products/custom-machines', description: 'Purpose-built machine concepts and integrated tooling for specific production processes.', detailImage: 'jig-fixture-ai.jpg', introImage: 'gantry-machine-ai.jpg', type: 'Integrated Solution', category: 'Custom Engineering' },
  { title: 'Torque Tools', slug: 'torque-tools', path: '/products/torque-tools', description: 'Precision torque tools for industrial assembly applications, offered through documented partner relationships.', detailImage: 'tool-in-use-ai.jpg', introImage: 'torque-tool-range-ai.jpg', type: 'Partner Product', category: 'Industrial Tools' },
  { title: 'Battery Tools', slug: 'battery-tools', path: '/products/battery-tools', description: 'Battery-powered tools for industrial assembly and production applications.', detailImage: 'tool-in-use-ai.jpg', introImage: 'torque-tool-range-ai.jpg', type: 'Partner Product', category: 'Industrial Tools' },
  { title: 'Jigs & Fixtures', slug: 'jigs-fixtures', path: '/products/jigs-fixtures', description: 'Application-specific tooling concepts that help position and support components during production.', detailImage: 'precision-inspection-ai.jpg', introImage: 'custom-press-cell.webp', type: 'Integrated Solution', category: 'Custom Engineering' },
  { title: 'Material Handling Equipment', slug: 'material-handling-equipment', path: '/products/material-handling-equipment', description: 'Integrated systems and equipment for moving components and materials through industrial environments.', detailImage: 'conveyor-materials.webp', introImage: 'manipulator-ai.jpg', type: 'Integrated Solution', category: 'Material Handling' },
  { title: 'Rail Systems', slug: 'rail-systems', path: '/products/rail-systems', description: 'Rail-based movement and lifting arrangements, including integrated XY / KBK system applications.', detailImage: 'overhead-crane.webp', introImage: 'chain-hoist.webp', type: 'Partner Product', category: 'Material Handling' },
  { title: 'Tightening Solutions', slug: 'tightening-solutions', path: '/products/tightening-solutions', description: 'Industrial tightening machine and tool integration for defined assembly processes.', detailImage: 'torque-tool-range-ai.jpg', introImage: 'jidoka-poka-yoke-ai.jpg', type: 'Integrated Solution', category: 'Assembly Automation' },
];

export const products: CatalogItem[] = withCatalogueImages(productDefinitions, catalogueImages.products as Record<string, string>);

const projectDefinitions: Array<Omit<CatalogItem, 'image'>> = [
  { title: 'Pick-to-Light for Smart Kitting', slug: 'pick-to-light-kitting', path: '/projects/pick-to-light-kitting', description: 'A guided picking concept for organized component selection at assembly workstations.', detailImage: 'pick-to-light-detail.jpg', category: 'Smart Manufacturing' },
  { title: 'Jidoka / Poka-Yoke Workstation', slug: 'jidoka-workstation', path: '/projects/jidoka-workstation', description: 'A monitored workstation concept combining process indicators and connected tools.', detailImage: 'electronics-testing-ai.jpg', introImage: 'plc-monitoring-ai.jpg', category: 'Error Prevention' },
  { title: 'IoT / PLC Monitoring', slug: 'iot-plc-monitoring', path: '/projects/iot-plc-monitoring', description: 'Centralized production visibility built around machine data and PLC monitoring.', detailImage: 'industrial-dashboard-ai.jpg', introImage: 'condition-monitoring-ai.jpg', category: 'Industry 4.0' },
  { title: 'Conveyor & Lift Table Integration', slug: 'conveyor-lift-table', path: '/projects/conveyor-lift-table', description: 'A material transfer concept using conveyors and an engineered lift-table arrangement.', detailImage: 'roller-conveyor-detail.webp', introImage: 'conveyor-transfer.webp', category: 'Material Handling' },
  { title: 'Tightening Machine', slug: 'tightening-machine', path: '/projects/tightening-machine', description: 'An industrial tightening application supported by a purpose-built machine arrangement.', detailImage: 'torque-tool-range-ai.jpg', introImage: 'jidoka-poka-yoke-ai.jpg', category: 'Assembly Automation' },
  { title: 'Servo Cartesian & SPM', slug: 'servo-cartesian-spm', path: '/projects/servo-cartesian-spm', description: 'Custom automation concepts for specific industrial movement and production requirements.', detailImage: 'pressing-machine.webp', introImage: 'custom-press-cell.webp', category: 'Special Purpose Machines' },
  { title: 'Hoist & Rail Installation', slug: 'hoist-rail-installation', path: '/projects/hoist-rail-installation', description: 'Overhead lifting and rail-based movement integrated into a factory environment.', detailImage: 'chain-hoist.webp', introImage: 'lifting-hardware.webp', category: 'Material Handling' },
  { title: 'Machine Relocation Support', slug: 'machine-relocation', path: '/projects/machine-relocation', description: 'Planning and on-site assistance for industrial equipment movement and reinstallation.', detailImage: 'machine-relocation-ai.jpg', introImage: 'commissioning-team-ai.jpg', category: 'Industrial Services' },
  { title: 'Condition Monitoring', slug: 'condition-monitoring', path: '/projects/condition-monitoring', description: 'Monitoring concepts that help provide visibility into the condition of industrial equipment.', detailImage: 'industrial-dashboard-ai.jpg', introImage: 'plc-monitoring-ai.jpg', category: 'Industry 4.0' },
  { title: 'Automated Conveyor Systems', slug: 'automated-conveyor-systems', path: '/projects/automated-conveyor-systems', description: 'Engineered conveyor-system concepts for material flow across production operations.', detailImage: 'conveyor-materials.webp', introImage: 'conveyor-transfer.webp', category: 'Material Handling' },
  { title: 'Jigs & Fixtures', slug: 'jigs-fixtures-project', path: '/projects/jigs-fixtures-project', description: 'Application-specific tooling concepts for industrial assembly and production tasks.', detailImage: 'precision-inspection-ai.jpg', introImage: 'custom-press-cell.webp', category: 'Assembly Automation' },
  { title: 'Sealing & Pressing Solutions', slug: 'sealing-pressing-solutions', path: '/projects/sealing-pressing-solutions', description: 'Custom production-machine concepts for sealing and pressing applications.', detailImage: 'gantry-machine.webp', introImage: 'custom-press-cell.webp', category: 'Special Purpose Machines' },
  { title: 'Machine Refurbishment', slug: 'machine-refurbishment', path: '/projects/machine-refurbishment', description: 'Industrial refurbishment and reconditioning support aligned with defined equipment needs.', detailImage: 'hero-maintenance-pump-ai.jpg', introImage: 'condition-monitoring-ai.jpg', category: 'Industrial Services' },
  { title: 'Material Handling Systems', slug: 'material-handling-systems', path: '/projects/material-handling-systems', description: 'Material movement and handling concepts integrated for manufacturing environments.', detailImage: 'lifting-hardware.webp', introImage: 'lift-table-ai.jpg', category: 'Material Handling' },
  { title: 'Custom Industrial Solutions', slug: 'custom-industrial-solutions', path: '/projects/custom-industrial-solutions', description: 'Application-led industrial engineering and integration concepts based on project requirements.', detailImage: 'assembly-line-overview.webp', introImage: 'engineering-design-ai.jpg', category: 'Industrial Services' },
];

export const projects: CatalogItem[] = withCatalogueImages(projectDefinitions, catalogueImages.projects as Record<string, string>);

const industryDefinitions: Array<Omit<CatalogItem, 'image'>> = [
  { title: 'Automotive', slug: 'automotive', path: '/industries', description: 'Assembly automation, material flow, tightening applications and production integration.' },
  { title: 'Manufacturing & Machinery', slug: 'manufacturing-machinery', path: '/industries', description: 'Engineering, custom equipment, integration and industrial service support.' },
  { title: 'Warehousing & Logistics', slug: 'warehousing-logistics', path: '/industries', description: 'Material handling, lifting systems, guided movement and workflow support.' },
  { title: 'Assembly & Production', slug: 'assembly-production', path: '/industries', description: 'Workstation automation, smart kitting, process monitoring and assembly tools.' },
  { title: 'Food & Beverage', slug: 'food-beverage', path: '/industries', description: 'Industrial automation and material movement applications for production environments.' },
  { title: 'Industrial Services', slug: 'industrial-services', path: '/industries', description: 'Maintenance, relocation, refurbishment and commissioning support.' },
  { title: 'Engineering & Machinery', slug: 'engineering-machinery', path: '/industries', description: 'Engineering design, custom equipment, fabrication and industrial integration applications.' },
  { title: 'Material Handling', slug: 'material-handling', path: '/industries', description: 'Lifting systems, rail-based movement, manipulators and conveyor integration.' },
];

export const industries: CatalogItem[] = withCatalogueImages(industryDefinitions, catalogueImages.industries as Record<string, string>);

export const partners = [
  { name: 'KITO CROSBY', relationship: 'Authorized Sales Partner & System Integrator', text: 'Material handling, hoists and lifting equipment solutions.', mark: 'KC' },
  { name: 'DESOUTTER TOOLS', relationship: 'Authorized System Integrator', text: 'Industrial assembly and tightening tool solutions.', mark: 'D' },
  { name: 'TOHNICHI', relationship: 'Authorized Sales Partner', text: 'Precision torque tools and torque-related solutions.', mark: 'T' },
  { name: 'TONE TOOLS', relationship: 'Authorized Sales Partner', text: 'Industrial hand tools and related applications.', mark: 'TONE' },
  { name: 'DUROFIX BATTERY TOOLS', relationship: 'Authorized Sales Partner', text: 'Battery-powered industrial tool solutions.', mark: 'DF' },
];

export const awards = [
  { title: 'Tata Motors Safety Award', period: '2020–21', text: 'Documented recognition listed in the NexAge company profile.' },
  { title: 'Tata Motors Safety Award', period: '2022–23', text: 'Documented recognition listed in the NexAge company profile.' },
  { title: 'Tata Motors Award', period: '2024–25', text: 'Documented award reference listed in the company profile.' },
];

export const clientLocations = [
  { clients: ['Tata Motors', 'Ashok Leyland', 'Titan', 'Henkel', 'Nestlé'], location: 'Pantnagar', state: 'Uttarakhand', x: 39, y: 26 },
  { clients: ['Tata Motors', 'Ashok Leyland'], location: 'Lucknow', state: 'Uttar Pradesh', x: 44, y: 35 },
  { clients: ['Tata Motors'], location: 'Jamshedpur', state: 'Jharkhand', x: 62, y: 49 },
  { clients: ['Denso', 'Honda'], location: 'IMT Manesar', state: 'Haryana', x: 31, y: 28 },
  { clients: ['Honda'], location: 'Tapukheda / Neemrana', state: 'Rajasthan', x: 25, y: 34 },
  { clients: ['Tata Motors'], location: 'Pune', state: 'Maharashtra', x: 20, y: 64 },
  { clients: ['Tata Motors'], location: 'Sanand', state: 'Gujarat', x: 15, y: 48 },
  { clients: ['Kubota'], location: 'Faridabad', state: 'Haryana', x: 37, y: 34 },
  { clients: ['Mahindra & Mahindra Ltd.'], location: 'Mohali', state: 'Punjab', x: 30, y: 22 },
  { clients: ['Mahindra & Mahindra Ltd.'], location: 'Lalpur', state: 'Uttarakhand', x: 44, y: 30 },
];
export const selectedClients = [...new Set(clientLocations.flatMap(({ clients }) => clients))];
export const locations = [...new Set(clientLocations.map(({ location }) => location))];

const serviceDefinitions: Array<{ title: string; slug: string; text: string }> = [
  { title: 'Preventive Maintenance & AMC', slug: 'preventive-maintenance', text: 'Planned maintenance and service support for industrial equipment and production processes.' },
  { title: 'Installation & Commissioning', slug: 'installation-commissioning', text: 'On-site installation, system integration checks and commissioning support.' },
  { title: 'Machinery Relocation', slug: 'machinery-relocation', text: 'Support for dismantling, shifting, reinstallation and line transition activities.' },
  { title: 'Refurbishment & Troubleshooting', slug: 'refurbishment-troubleshooting', text: 'Engineering assistance for machine refurbishment and identifying operational issues.' },
  { title: 'Fabrication & Pipeline Jobs', slug: 'fabrication-pipeline', text: 'Fabrication support for structures, tanks, columns, pipelines and related plant requirements.' },
  { title: 'Line & Process Integration', slug: 'line-process-integration', text: 'Integration of machining, production and assembly-line processes.' },
];

export const services = withCatalogueImages(serviceDefinitions, catalogueImages.services as Record<string, string>);

export const processSteps = ['Understand', 'Design', 'Engineer', 'Manufacture', 'Integrate', 'Test', 'Commission', 'Support'];

export const pageMeta: Record<string, { title: string; description: string }> = {
  '/': { title: 'NexAge India | Industrial Automation & MRO', description: 'Engineering-led industrial automation, material handling, smart manufacturing and MRO solutions from NexAge India Pvt. Ltd.' },
  '/about': { title: 'About NexAge India | Engineering & Automation', description: 'Learn about NexAge India’s industrial engineering, automation, integration and MRO capabilities.' },
  '/solutions': { title: 'Industrial Solutions | NexAge India', description: 'Explore industrial automation, conveyor, smart manufacturing, custom machine, engineering and MRO solutions.' },
  '/products': { title: 'Industrial Products & Systems | NexAge India', description: 'Explore NexAge solutions and integrated partner products for smart manufacturing, assembly and material handling.' },
  '/industries': { title: 'Industries We Serve | NexAge India', description: 'Industrial engineering, automation and material handling support for manufacturing and production environments.' },
  '/projects': { title: 'Projects & Applications | NexAge India', description: 'Explore selected industrial applications and project categories aligned with NexAge’s company profile.' },
  '/partners': { title: 'Authorized Partners | NexAge India', description: 'View NexAge India’s documented partner relationships in tools and material handling.' },
  '/clients': { title: 'Clients & Locations | NexAge India', description: 'Explore client names and service locations documented in the NexAge India company profile.' },
  '/services': { title: 'Industrial Services & MRO | NexAge India', description: 'Maintenance, machinery relocation, refurbishment, installation and industrial service support.' },
  '/awards': { title: 'Awards & Recognition | NexAge India', description: 'View documented award and customer appreciation references listed in the NexAge company profile.' },
  '/contact': { title: 'Contact NexAge India | Industrial Enquiries', description: 'Contact NexAge India for industrial automation, engineering, material handling and MRO enquiries.' },
  '/quote': { title: 'Request a Quote | NexAge India', description: 'Share your application requirements with NexAge India and request an industrial engineering quote.' },
  '/news': { title: 'News & Updates | NexAge India', description: 'Company updates and news published by NexAge India Pvt. Ltd.' },
  '/privacy': { title: 'Privacy Notice | NexAge India', description: 'How NexAge India uses information submitted through its contact and quotation forms.' },
  '/terms': { title: 'Terms of Use | NexAge India', description: 'Terms for using the NexAge India website and its public information.' },
};
