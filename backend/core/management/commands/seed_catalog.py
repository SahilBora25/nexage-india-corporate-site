from django.core.management.base import BaseCommand
from core.catalogue_images import CATALOGUE_IMAGE_MAPS
from core.models import Award, Industry, Partner, Product, ProductCategory, Project, ProjectCategory, Service

class Command(BaseCommand):
    help = 'Idempotently create missing starter catalogue records without overwriting existing edits.'

    def handle(self, *args, **options):
        product_categories = {}
        for name, slug in [('Smart Manufacturing','smart-manufacturing'),('Wireless Systems','wireless-systems'),('Material Handling','material-handling'),('Industrial Tools','industrial-tools'),('Custom Engineering','custom-engineering')]:
            obj, _ = ProductCategory.objects.get_or_create(slug=slug, defaults={'name': name})
            product_categories[name] = obj
        product_rows = [
            ('NexAge Jidoka System','jidoka','Smart Manufacturing','A process monitoring and error-prevention system for industrial assembly applications.','nexage',['Process monitoring','Error-prevention logic','Visual status indication']),
            ('NexAge Wireless TX/RX','wireless-tx-rx','Wireless Systems','A wireless transmitter and receiver concept for industrial signal triggering and integration.','nexage',['Pairing and signal-triggering workflow','Status indication','Industrial integration']),
            ('NexAge Pick-to-Light System','pick-to-light','Smart Manufacturing','Illuminated picking points support guided material identification and smart kitting.','nexage',['Guided material picking','Operator guidance','Smart kitting']),
            ('Cranes & Hoists','cranes-hoists','Material Handling','Lifting and material-handling solutions through authorized partner product offerings and integration.','partner',['Lifting equipment','Material handling','Application integration']),
            ('Industrial Assembly Tools','industrial-tools','Industrial Tools','Electric, battery-powered and precision tightening tools for industrial assembly applications.','partner',['Electric assembly tools','Battery tools','Precision tightening']),
            ('Custom Machines','custom-machines','Custom Engineering','Purpose-built machine concepts and integrated tooling for specific production processes.','integrated',['Custom machines','Process integration']),
            ('Torque Tools','torque-tools','Industrial Tools','Precision torque tools for industrial assembly applications, offered through documented partner relationships.','partner',['Precision torque tools','Industrial assembly']),
            ('Battery Tools','battery-tools','Industrial Tools','Battery-powered tools for industrial assembly and production applications.','partner',['Battery-powered assembly','Industrial applications']),
            ('Jigs & Fixtures','jigs-fixtures','Custom Engineering','Application-specific tooling concepts that help position and support components during production.','integrated',['Jigs and fixtures','Production support']),
            ('Material Handling Equipment','material-handling-equipment','Material Handling','Integrated systems and equipment for moving components and materials through industrial environments.','integrated',['Material movement','System integration']),
            ('Rail Systems','rail-systems','Material Handling','Rail-based movement and lifting arrangements, including integrated XY / KBK system applications.','partner',['Rail-based movement','Lifting integration']),
            ('Tightening Solutions','tightening-solutions','Industrial Tools','Industrial tightening machine and tool integration for defined assembly processes.','integrated',['Tightening machine integration','Assembly processes']),
        ]
        for title, slug, cat, desc, owner, features in product_rows:
            Product.objects.get_or_create(slug=slug, defaults={'title': title, 'category': product_categories[cat], 'description': desc, 'ownership': owner, 'image_path': CATALOGUE_IMAGE_MAPS['products'][slug], 'features': features, 'is_published': True})
        for name, rel, desc in [
            ('KITO CROSBY','Authorized Sales Partner & System Integrator','Material handling, hoists and lifting equipment solutions.'),
            ('DESOUTTER TOOLS','Authorized System Integrator','Industrial assembly and tightening tool solutions.'),
            ('TOHNICHI','Authorized Sales Partner','Precision torque tools and torque-related solutions.'),
            ('TONE TOOLS','Authorized Sales Partner','Industrial hand tools and related applications.'),
            ('DUROFIX BATTERY TOOLS','Authorized Sales Partner','Battery-powered industrial tool solutions.'),
        ]: Partner.objects.get_or_create(name=name, defaults={'relationship': rel, 'description': desc, 'is_published': True})
        project_categories = {}
        for name in ['Smart Manufacturing','Error Prevention','Industry 4.0','Material Handling','Assembly Automation','Special Purpose Machines','Industrial Services']:
            slug = name.lower().replace(' ','-').replace('&','and')
            category, _ = ProjectCategory.objects.get_or_create(slug=slug, defaults={'name': name})
            project_categories[name] = category
        project_rows = [
            ('Pick-to-Light for Smart Kitting','pick-to-light-kitting','Smart Manufacturing','A guided picking concept for organized component selection at assembly workstations.'),
            ('Jidoka / Poka-Yoke Workstation','jidoka-workstation','Error Prevention','A monitored workstation concept combining process indicators and connected tools.'),
            ('IoT / PLC Monitoring','iot-plc-monitoring','Industry 4.0','Centralized production visibility built around machine data and PLC monitoring.'),
            ('Conveyor & Lift Table Integration','conveyor-lift-table','Material Handling','A material transfer concept using conveyors and an engineered lift-table arrangement.'),
            ('Tightening Machine','tightening-machine','Assembly Automation','An industrial tightening application supported by a purpose-built machine arrangement.'),
            ('Servo Cartesian & SPM','servo-cartesian-spm','Special Purpose Machines','Custom automation concepts for specific industrial movement and production requirements.'),
            ('Hoist & Rail Installation','hoist-rail-installation','Material Handling','Overhead lifting and rail-based movement integrated into a factory environment.'),
            ('Machine Relocation Support','machine-relocation','Industrial Services','Planning and on-site assistance for industrial equipment movement and reinstallation.'),
            ('Condition Monitoring','condition-monitoring','Industry 4.0','Monitoring concepts that help provide visibility into the condition of industrial equipment.'),
            ('Automated Conveyor Systems','automated-conveyor-systems','Material Handling','Engineered conveyor-system concepts for material flow across production operations.'),
            ('Jigs & Fixtures','jigs-fixtures-project','Assembly Automation','Application-specific tooling concepts for industrial assembly and production tasks.'),
            ('Sealing & Pressing Solutions','sealing-pressing-solutions','Special Purpose Machines','Custom production-machine concepts for sealing and pressing applications.'),
            ('Machine Refurbishment','machine-refurbishment','Industrial Services','Industrial refurbishment and reconditioning support aligned with defined equipment needs.'),
            ('Material Handling Systems','material-handling-systems','Material Handling','Material movement and handling concepts integrated for manufacturing environments.'),
            ('Custom Industrial Solutions','custom-industrial-solutions','Industrial Services','Application-led industrial engineering and integration concepts based on project requirements.'),
        ]
        for title, slug, cat, desc in project_rows:
            Project.objects.get_or_create(slug=slug, defaults={'title': title, 'category': project_categories[cat], 'application': desc, 'solution': desc, 'image_path': CATALOGUE_IMAGE_MAPS['projects'][slug], 'is_published': True})
        for title, slug, desc in [
            ('Preventive Maintenance & AMC','preventive-maintenance','Planned maintenance and service support for industrial equipment and production processes.'),
            ('Installation & Commissioning','installation-commissioning','On-site installation, system integration checks and commissioning support.'),
            ('Machinery Relocation','machinery-relocation','Support for dismantling, shifting, reinstallation and line transition activities.'),
            ('Refurbishment & Troubleshooting','refurbishment-troubleshooting','Engineering assistance for machine refurbishment and identifying operational issues.'),
            ('Fabrication & Pipeline Jobs','fabrication-pipeline','Fabrication support for structures, tanks, columns, pipelines and related plant requirements.'),
            ('Line & Process Integration','line-process-integration','Integration of machining, production and assembly-line processes.'),
        ]: Service.objects.get_or_create(slug=slug, defaults={'title': title, 'description': desc, 'image_path': CATALOGUE_IMAGE_MAPS['services'][slug], 'is_published': True})
        for name, slug, desc in [
            ('Automotive','automotive','Assembly automation, material flow, tightening applications and production integration.'),
            ('Manufacturing & Machinery','manufacturing-machinery','Engineering, custom equipment, integration and industrial service support.'),
            ('Warehousing & Logistics','warehousing-logistics','Material handling, lifting systems, guided movement and workflow support.'),
            ('Assembly & Production','assembly-production','Workstation automation, smart kitting, process monitoring and assembly tools.'),
            ('Food & Beverage','food-beverage','Industrial automation and material movement applications for production environments.'),
            ('Engineering & Machinery','engineering-machinery','Engineering design, custom equipment, fabrication and industrial integration applications.'),
            ('Material Handling','material-handling','Lifting systems, rail-based movement, manipulators and conveyor integration.'),
            ('Industrial Services','industrial-services','Maintenance, relocation, refurbishment and commissioning support.'),
        ]: Industry.objects.get_or_create(slug=slug, defaults={'name': name, 'description': desc, 'image_path': CATALOGUE_IMAGE_MAPS['industries'][slug], 'is_published': True})
        for title, period, issuer in [('Tata Motors Safety Award','2020–21','Tata Motors'),('Tata Motors Safety Award','2022–23','Tata Motors'),('Tata Motors Award','2024–25','Tata Motors')]:
            Award.objects.get_or_create(title=title, period=period, defaults={'issuer': issuer, 'description': 'Award reference listed in the supplied NexAge company profile.', 'is_published': True})
        self.stdout.write(self.style.SUCCESS(
            'Ensured starter catalogue records exist; existing entries were preserved. '
            'Review all entries before publishing.'
        ))
