
from flask import Flask, render_template, request, redirect, url_for, session, flash
from functools import wraps
from datetime import datetime
import uuid, re, os, sqlite3

app = Flask(__name__)

# Use a secret key from the environment.
# The fallback is only for local development.
app.secret_key = os.environ.get("SECRET_KEY") or "local-development-only-change-me"


PRODUCTS = []
SUBCATEGORIES = {}   # category -> [subcategory, ...] in display order

# ---------------- CUSTOMER FEEDBACK DATABASE ----------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FEEDBACK_DB = os.path.join(BASE_DIR, "feedback.db")


def get_feedback_db():
    conn = sqlite3.connect(FEEDBACK_DB)
    conn.row_factory = sqlite3.Row
    return conn


def init_feedback_db():
    conn = get_feedback_db()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            order_id TEXT NOT NULL UNIQUE,
            customer_name TEXT NOT NULL,
            customer_email TEXT NOT NULL,
            rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
            review TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
    """)

    conn.commit()
    conn.close()


init_feedback_db()


def slug(s):
    return re.sub(r'[^a-z0-9]+', '-', s.lower()).strip('-')


def add(cat, sub, name, price, emoji, desc, options):
    """Add a product. Its image file is static/images/<id>.jpg (id = slug of the name)."""
    pid = slug(name)
    if any(p['id'] == pid for p in PRODUCTS):
        pid = slug(sub + ' ' + name)
    PRODUCTS.append({'id': pid, 'name': name, 'category': cat, 'subcategory': sub, 'price': price,
                     'emoji': emoji, 'description': desc, 'options': options, 'image': pid + '.jpg'})
    SUBCATEGORIES.setdefault(cat, [])
    if sub not in SUBCATEGORIES[cat]:
        SUBCATEGORIES[cat].append(sub)


# ---------------- APPAREL ----------------
SIZES = ['S', 'M', 'L', 'XL', 'XXL']
for n, pr in [('Plain Long-Sleeve Shirt', 299), ('Breathable Quick-Dry Shirt', 349), ('Sun-Protection Shirt', 379),
              ('Camouflage Long-Sleeve Shirt', 349), ('Farm-Themed Graphic Shirt', 329), ('Minimalist Long-Sleeve Shirt', 299),
              ('Reflective Work Shirt', 399), ('Hooded Long-Sleeve Shirt', 389), ('Long-Sleeve Shirt with Face Cover', 369),
              ('Lightweight Outdoor Work Shirt', 319)]:
    add('Apparel', 'Shirts', n, pr, '👕', 'Long-sleeve shirt for outdoor farm work. Choose a color and size.',
        {'Color': ['Green', 'Navy', 'Brown', 'Black'], 'Size': SIZES})

for n, pr in [('Cargo Work Pants', 349), ('Waterproof Pants', 449), ('Quick-Dry Pants', 359), ('Reinforced Work Pants', 399),
              ('Stretchable Farm Pants', 379), ('Camouflage Pants', 369), ('Lightweight Outdoor Trousers', 339),
              ('Heavy-Duty Utility Pants', 429)]:
    add('Apparel', 'Pants', n, pr, '👖', 'Comfortable, durable pants for work in the field.',
        {'Color': ['Khaki', 'Green', 'Black', 'Navy'], 'Size': SIZES})

BOOT_SIZES = [str(i) for i in range(36, 45)]
for n, pr in [('Rubber Farm Boots', 499), ('Knee-High Boots', 549), ('Waterproof Work Boots', 599), ('Safety Boots', 699),
              ('Lightweight Outdoor Shoes', 449), ('Slip-Resistant Boots', 579)]:
    add('Apparel', 'Boots & Shoes', n, pr, '🥾', 'Footwear for muddy paths and wet fields.',
        {'Color': ['Black', 'Green', 'Brown'], 'Size': BOOT_SIZES})

for n, pr in [('Rubber Gloves', 99), ('Gardening Gloves', 129), ('Cut-Resistant Work Gloves', 199), ('Waterproof Gloves', 159),
              ('Heavy-Duty Farm Gloves', 189), ('Coated Grip Gloves', 149)]:
    add('Apparel', 'Gloves', n, pr, '🧤', 'Protective gloves for planting and everyday farm work.',
        {'Size': ['S', 'M', 'L', 'XL']})

for n, pr in [('Baseball Cap', 129), ('Wide-Brim Sun Hat', 149), ('Bucket Hat', 139), ('Neck-Flap Sun Hat', 159),
              ('Hat with Face Cover', 169), ('Breathable Outdoor Hat', 139), ('Waterproof Hat', 159)]:
    add('Apparel', 'Caps & Hats', n, pr, '🧢', 'Shade and sun protection while working outdoors.',
        {'Color': ['Green', 'Brown', 'Black', 'Beige']})

for n, pr in [('Raincoat', 399), ('Two-Piece Rain Suit', 549), ('Waterproof Jacket', 499), ('Reflective Raincoat', 549),
              ('Poncho', 199), ('Face-Covering Outdoor Jacket', 529)]:
    add('Apparel', 'Rainwear & Jackets', n, pr, '🧥', 'Rain protection for field work.',
        {'Color': ['Green', 'Yellow', 'Navy'], 'Size': SIZES})

for n, pr in [('Protective Coveralls', 599), ('High-Visibility Workwear', 449), ('Sun-Protection Arm Sleeves', 99)]:
    add('Apparel', 'Protective Wear', n, pr, '🦺', 'Protective workwear for safer farm work.',
        {'Color': ['Green', 'Orange', 'Navy', 'Black'], 'Size': SIZES})

# ---------------- SEEDS ----------------
SEED_OPT = {'Pack Size': ['Small Pack', 'Family Pack', 'Farm Pack']}
SEED_DESC = 'Seeds for home gardens and farms. Check packet variety and expiry details.'
for n in ['Eggplant', 'Ladyfinger (Okra)', 'Tomato', 'Beans', 'Chili', 'Squash', 'Carrot', 'Cabbage', 'Pechay', 'Ampalaya',
          'Cucumber', 'Lettuce', 'Onion', 'Radish', 'Mustard Greens']:
    add('Seeds', 'Vegetable Seeds', n + ' Seeds', 45, '🌱', SEED_DESC, SEED_OPT)
add('Seeds', 'Vegetable Seeds', 'Mixed Vegetable Seeds', 69, '🌱', SEED_DESC, SEED_OPT)
for n in ['Corn', 'Rice', 'Watermelon', 'Melon']:
    add('Seeds', 'Grain & Fruit Seeds', n + ' Seeds', 59, '🌾', SEED_DESC, SEED_OPT)

# ---------------- FERTILIZER & CROP CARE ----------------
FERT_DESC = 'Farm crop-care product listing. Read the official label, verify local registration, and follow safety instructions.'
FERT_OPT = {'Pack Size': ['Small', 'Medium', 'Large']}
for cat_sub, items in [
    ('Liquid Fertilizer', [('Fruit Fertilizer Juice', 199), ('Plant Fertilizer Juice', 179), ('Fish Fertilizer Juice', 219),
                           ('Organic Liquid Fertilizer', 229)]),
    ('Chemical Fertilizer', [('Urea 46-0-0', 399), ('Complete Fertilizer 14-14-14', 429), ('Ammonium Sulfate', 359),
                             ('Muriate of Potash', 449), ('Ammonium Phosphate', 459), ('Rice-Specific Fertilizer', 429)]),
    ('Organic & Soil', [('Vermicast', 249), ('Compost Fertilizer', 199), ('Soil Conditioner', 279)]),
    ('Crop Protection', [('Virtako Insecticide', 299), ('Nativo Fungicide', 289), ('2,4-D Herbicide', 259),
                         ('Frontier Herbicide', 329), ('Surekill Molluscicide', 189)]),
]:
    for n, pr in items:
        add('Fertilizer & Crop Care', cat_sub, n, pr, '🧴', FERT_DESC, FERT_OPT)

# ---------------- FARM SNACKS ----------------
SNACK_OPT = {'Flavor': ['Original', 'BBQ', 'Sour Cream', 'Chilli', 'Cheese'], 'Pack Size': ['Small', 'Regular', 'Family Pack']}
for n, pr in [('Banana Chips', 79), ('Taro Chips', 89), ('Kangkong Chips', 69), ('Ampalaya Chips', 79), ('Kamote Chips', 75),
              ('Jackfruit Chips', 99), ('Cassava Chips', 69), ('Ube Chips', 95), ('Mushroom Chips', 99), ('Coconut Chips', 89)]:
    add('Farm Snacks', 'Chips', n, pr, '🍌', 'Crunchy Filipino snack. Choose a flavor and pack size.', SNACK_OPT)
for n, pr in [('Dried Mangoes', 119), ('Dried Pineapple', 99)]:
    add('Farm Snacks', 'Dried Fruit', n, pr, '🥭', 'Sweet dried Filipino fruit. Choose a pack size.',
        {'Pack Size': ['Small', 'Regular', 'Family Pack']})

# ---------------- FARM EQUIPMENT ----------------
TYPE = {'Type': ['Standard', 'Heavy Duty']}
D = 'Useful tool for gardening and farm work.'
for sub, items in [
    ('Sprayers', [('Knapsack Sprayer', 899), ('Electric Sprayer', 1799), ('Hand Sprayer', 399), ('Sprayer Replacement Parts', 149),
                  ('Nozzles and Hoses', 199)]),
    ('Hand Tools', [('Garden Trowel', 99), ('Spade', 299), ('Sickle', 149), ('Pitchfork', 349), ('Shovel', 279), ('Hoe', 229),
                    ('Gardening Fork', 129), ('Rake', 249), ('Bolo', 299), ('Pruning Shears', 199), ('Grass Cutter', 2499),
                    ('Wheelbarrow', 1499)]),
    ('Water & Irrigation', [('Watering Can', 179), ('Garden Hose', 499), ('Water Pump', 2999), ('Irrigation Pipes', 349),
                            ('Drip Irrigation Kit', 899)]),
    ('Planting & Harvest', [('Seedling Tray', 89), ('Plant Pots', 79), ('Harvesting Basket', 159), ('Rice Harvesting Tools', 349),
                            ('Grain Tarpaulin', 599), ('Harvesting Sacks', 129), ('Farm Tool Storage Box', 699)]),
    ('Measuring Tools', [('Measuring Tape', 99), ('Soil pH Meter', 499), ('Portable Weighing Scale', 799)]),
    ('Safety Gear', [('Protective Goggles', 149), ('Respirator', 349), ('Safety Helmet', 299), ('Ear Protection', 199)]),
]:
    for n, pr in items:
        add('Farm Equipment', sub, n, pr, '🛠️', D, TYPE)


# ---------------- WORD DOCUMENT PRODUCT DESCRIPTIONS ----------------
# Product descriptions below are taken from Document (28).docx.
WORD_DESCRIPTIONS = {'Plain Long-Sleeve Shirt': 'This off-white long-sleeve tee features a central graphic depicting a '
                            'traditional farm scene with a carabao and the text"BUKID LIFE". It provides '
                            'light coverage suitable for outdoor farm work.',
 'Breathable Quick-Dry Shirt': 'A light blue button-down shirt designed with breathable side pmesh panels '
                               'for ventilation. It offers quick-drying performance during active farm '
                               'tasks.',
 'Sun-Protection Shirt': 'This tan, long-sleeve henley shirt includes built-in UPF 50+ sun protection and '
                         'thumbholes at the cuffs. It helps defend your skin against long hours under the '
                         'sun.',
 'Camouflage Long-Sleeve Shirt': 'A long-sleeve top featuring a classic woodland camo pattern. It provides '
                                 'full sleeve coverage for outdoor labor or hunting environments.',
 'Farm-Themed Graphic Shirt': 'An off-white long-sleeve top featuring a vibrant rooster graphic and '
                              '“PILIPINAS FARM LIFE” lettering. It offers a casual and comfortable fit for '
                              'daily wearing.',
 'Minimalist Long-Sleeve Shirt': 'A plain charcoal-gray long-sleeve shirt styled with a small, understated '
                                 'logo on the left chest. It delivers a simple, versatile look for any '
                                 'routine activity.',
 'Reflective Work Shirt': 'A bright orange high-visibility button-up shirt featuring silver reflective '
                          'safety stripes across the torso and sleeves. It is built to keep workers easily '
                          'visible in low-light conditions.',
 'Hooded Long-Sleeve Shirt': 'An olive green button-down shirt equipped with a lightweight hood and double '
                             'chest pockets. It features roll-up sleeve tabs for adjustable coverage during '
                             'outdoor work.',
 'Long-Sleeve Shirt with Face Cover': 'A dark olive long-sleeve shirt equipped with a built-in neck gaiter '
                                      'that pulls up to cover the lower face. It offers integrated '
                                      'protection from dust, wind, and harsh sunlight.',
 'Lightweight Outdoor Work Shirt': 'An olive green button-down work shirt crafted with durable front chest '
                                   'flap pockets. It provides a rugged design made for lightweight '
                                   'breathability in the field.',
 'Cargo Work Pants': 'Tan utility trousers featuring roomy cargo flap pockets on both sides and reinforced '
                     'knee panels. They are designed to withstand tough outdoor conditions while offering '
                     'plenty of storage space.',
 'Waterproof Pants': 'Dark green outdoor trousers constructed with zippered side pockets and elastic ankle '
                     'cuffs. They help repel water and moisture during wet weather or damp field work.',
 'Quick-Dry Pants': 'Black athletic-style pants designed with bright orange side stripes and an adjustable '
                    'drawstring waist. They feature gathered elastic cuffs for a secure, athletic fit.',
 'Reinforced Work Pants': 'Beige utility trousers designed with discrete side cargo pockets and reinforced '
                          'knee stitching. They provide durable, low-profile performance for tough tasks.',
 'Stretchable Farm Pants': 'Deep olive green trousers featuring a side zip pocket and flex fabric for easier '
                           'mobility. They offer enhanced comfort during bending and active farm labor.',
 'Camouflage Pants': 'Heavy-duty utility pants decorated in a traditional woodland camouflage pattern. They '
                     'come equipped with multiple cargo pockets for practical outdoor gear storage.',
 'Lightweight Outdoor Trousers': 'Light gray outdoor pants featuring secure vertical zip pockets along the '
                                 'thighs. They offer a lightweight build suitable for easy movement in '
                                 'warmer weather.',
 'Heavy-Duty Utility Pants': 'Brown work trousers constructed with dark reinforced knee patches and large '
                             'cargo flap pockets. They are built to withstand heavy abrasion and demanding '
                             'workloads.',
 'Rubber Farm Boots': 'Ankle-high black rubber slip-on boots featuring flexible side goring and heavy lugged '
                      'tread. They protect feet against mud and water while staying easy to slip on and off.',
 'Knee-High Boots': 'Tall black waterproof rubber boots styled with high contrast yellow non-slip soles. '
                    'They offer maximum leg protection when wading through deep mud or wet fields.',
 'Waterproof Work Boots': 'These sturdy, tan lace-up work boots feature thick, heavy-duty treaded soles and '
                          'padded black collar cushions. They are designed to keep feet dry and protected '
                          'during tough outdoor labor.',
 'Safety Boots': 'A pair of dark brown leather work boots featuring reinforced toe boxes and high-traction '
                 'rubber outsoles. They provide robust protection and stability on rugged surfaces.',
 'Lightweight Outdoor Shoes': 'These gray and olive mid-cut hiking boots combine breathable mesh paneling '
                              'with durable leather overlays. They offer flexible, lightweight support for '
                              'active trail or outdoor work.',
 'Slip-Resistant Boots': 'High-cut black utility boots designed with a deep-grooved slip-resistant outsole. '
                         'They provide strong ankle support and reliable traction on slick or hazardous '
                         'terrain.',
 'Rubber Gloves': 'Bright yellow, elbow-length rubber gloves designed for waterproof hand and forearm '
                  'protection. They keep hands clean and safe during wet farm chores or cleaning tasks.',
 'Gardening Gloves': 'Green knit work gloves fitted with textured rubber dot grippers across the palm and '
                     'fingers. They provide an enhanced grip while handling plants, soil, and garden tools.',
 'Cut-Resistant Work Gloves': 'Gray cut-resistant gloves featuring a black coated palm layer for high '
                              'abrasion resistance. They defend hands against sharp edges and rough '
                              'materials during work.',
 'Waterproof Gloves': 'Deep blue heavy-duty rubber gloves extending up past the wrist for extra coverage. '
                      'They offer complete liquid protection during messy or wet agricultural work.',
 'Heavy-Duty Farm Gloves': 'Dark green long-cuff work gloves built with reinforced palm patches for heavy '
                           'manual labor. They protect hands and forearms from thorns, abrasions, and rough '
                           'foliage.',
 'Coated Grip Gloves': 'Gray knit gloves equipped with textured, bright orange rubber palm coatings. They '
                       'combine breathable hand comfort with a firm, slip-resistant grip on equipment.',
 'Baseball Cap': 'A classic forest-green cotton baseball cap featuring an adjustable back closure and curved '
                 'brim. It delivers simple shade and sun protection for everyday outdoor wear.',
 'Wide-Brim Sun Hat': 'A woven straw-style sun hat styled with a broad brim and a brown accent band. It '
                      'offers generous shade for the face and neck under bright sunlight.',
 'Bucket Hat': 'A light tan canvas bucket hat designed with side ventilation grommets and an adjustable chin '
               'strap. It offers 360-degree shade coverage for casual outdoor work.   Neck-',
 'Flap Sun Hat': 'A tan baseball-style cap attached to a long fabric flap that hangs over the back of the '
                 'neck. It guards the ears and neck against direct sun exposure.',
 'Hat with Face Cover': 'An olive green wide-brim outdoor hat equipped with a detachable face mask and neck '
                        'flap. It provides complete sun and wind protection for the head, face, and neck.',
 'Breathable Outdoor Hat': 'A wide-brimmed beige sun hat designed with breathable side mesh panels and a '
                           'chin cord toggle. It keeps the head cool while offering full overhead shade.',
 'Waterproof Hat': 'A bright yellow rain hat featuring a wide downturned brim and a toggle chin strap. It '
                   'sheds water effectively to keep your head dry during wet weather.',
 'Raincoat': 'A dark green, full-length waterproof coat with a button-and-zip front closure and attached '
             'hood. It provides comprehensive protection against heavy downpours during field work.',
 'Two-Piece Rain Suit': 'A dark green rain outfit comprising a hooded waterproof jacket and matching pull-on '
                        'trousers. It offers complete top-to-bottom weather protection for wet outdoor '
                        'tasks.',
 'Waterproof Jacket': 'A dark navy blue hooded rain jacket featuring a front zip closure and side pockets. '
                      'It delivers reliable protection against wind and rain while remaining easy to wear.',
 'Reflective Raincoat': 'A bright yellow, mid-length raincoat featuring horizontal reflective safety stripes '
                        'around the chest and sleeves. It provides waterproof protection and high visibility '
                        'during wet outdoor work.',
 'Poncho': 'A light beige or tan hooded rain garment shown as a simple protective outer layer. It offers '
           'lightweight coverage to keep you dry during sudden downpours.',
 'Face-Covering Outdoor Jacket': 'A tan zip-up jacket equipped with a built-in hood and face mask '
                                 'attachment. It delivers comprehensive protection against wind, rain, and '
                                 'direct sunlight.',
 'Protective Coveralls': 'A white, lightweight full-body protective jumpsuit with elastic cuffs at the '
                         'wrists and ankles. It is designed to shield clothing and skin from dust, sprays, '
                         'and debris.',
 'High-Visibility Workwear': 'A bright neon-orange safety vest lined with horizontal reflective strips '
                             'across the body. It enhances worker visibility in dark or high-traffic field '
                             'environments.',
 'Sun-Protection Arm Sleeves': 'A pair of tan elastic compression sleeves designed to cover the arms from '
                               'wrist to bicep. They block harmful UV rays while keeping arms cool during '
                               'sunny labor.',
 'Eggplant Seeds': 'A kraft paper seed packet illustrated with a detailed purple eggplant graphic and loose '
                   'seeds scattered in front. It contains non-GMO seeds ideal for home vegetable gardens or '
                   'farm planting.',
 'Ladyfinger (Okra) Seeds': 'A paper seed pouch featuring a botanical illustration of an okra plant '
                            'alongside dark seeds. It provides quality seeds for growing fresh okra pods.',
 'Tomato Seeds': 'A craft paper seed packet printed with a cluster of ripe red tomatoes and small seeds '
                 'lined up below. It contains heirloom seeds ready for garden planting.',
 'Beans Seeds': 'A sealed brown paper seed envelope featuring an illustration of green bean pods and '
                'scattered bean seeds. It offers high-yield seeds for planting string beans.',
 'Chili Seeds': 'A seed packet displaying a vibrant illustration of a red chili plant with pale seeds spread '
                'beneath. It is packaged for growing hot chili peppers at home or on the farm.',
 'Squash Seeds': 'A brown paper seed package depicting a ripe yellow squash and flat white seeds lying in '
                 'front. It includes heirloom seeds for cultivating winter squash.',
 'Carrot Seeds': 'A seed envelope printed with a central orange carrot illustration and tiny seeds spilled '
                 'in front. It contains non-GMO seeds suitable for root vegetable cultivation.',
 'Cabbage Seeds': 'A paper packet featuring a detailed drawing of a leafy green cabbage head and dark round '
                  'seeds. It supplies quality seeds for growing fresh cabbage crops.',
 'Pechay Seeds': 'A craft paper pouch illustrating a green bok choy plant with small black seeds resting '
                 'below. It is designed for planting fast-growing leafy pechay greens.',
 'Ampalaya Seeds': 'A paper seed packet displaying an illustration of bitter gourd vines alongside dark, '
                   'textured seeds. It provides seeds for growing traditional ampalaya vegetables.',
 'Cucumber Seeds': 'A resealable kraft paper pouch featuring a cucumber vine illustration and pale oval '
                   'seeds. It is packed with seeds for growing crisp garden cucumbers.',
 'Lettuce Seeds': 'A seed packet showing a head of crisp green lettuce alongside tiny grayish seeds. It '
                  'offers reliable seeds for cultivating home-grown salad greens.',
 'Onion Seeds': 'A paper seed envelope featuring a graphic of red onions and a pile of small black seeds. It '
                'contains quality seeds for planting red onion crops.',
 'Radish Seeds': 'A paper pouch decorated with an illustration of white daikon radishes and round dark '
                 'seeds. It supplies heirloom seeds for growing crisp radish roots.',
 'Mustard Greens Seeds': 'A kraft paper seed packet illustrated with a flowering mustard plant and small '
                         'dark seeds scattered below. It provides quality seeds for growing fresh mustard '
                         'greens in home gardens or farms.',
 'Mixed Vegetable Seeds': 'A resealable seed pouch featuring a colorful assortment illustration of a tomato, '
                          'eggplant, and carrot alongside various mixed seeds. It offers a convenient '
                          'combination of seeds for planting a diverse vegetable garden.',
 'Corn Seeds': 'A paper seed pouch depicting three golden corn cobs with a small pile of yellow corn kernels '
               'spread out in front. It is packaged for cultivating sweet corn or field corn crops.',
 'Rice Seeds': 'A paper seed packet displaying an illustration of mature rice stalks with unhusked rice '
               'grains resting below. It contains seeds intended for planting and growing rice crops.',
 'Watermelon Seeds': 'A resealable kraft paper pouch featuring an illustration of a sliced watermelon with '
                     'dark, flat seeds spread around. It supplies non-GMO seeds for growing sweet garden '
                     'watermelons.',
 'Melon Seeds': 'A paper seed packet decorated with a botanical drawing of a cantaloupe alongside pale melon '
                'seeds. It contains seeds selected for cultivating fresh cantaloupe melons.',
 'Fruit Fertilizer Juice': 'An amber bottle of liquid fertilizer featuring a mango illustration on its '
                           'natural kraft label. It is formulated as a fermented fruit extract to boost '
                           'plant nutrients.',
 'Plant Fertilizer Juice': 'A dark green liquid fertilizer bottle with a plant leaf design on the front '
                           'label. It supplies an organic fermented plant juice formula to support general '
                           'plant health.',
 'Fish Fertilizer Juice': 'A dark amber bottle labeled “Fish Fertilizer Juice” with a detailed fish '
                          'illustration on the front. It contains fish amino acids that act as a natural '
                          'nutrient boost for crop growth.',
 'Organic Liquid Fertilizer': 'A heavy-duty olive-green jug featuring an organic liquid fertilizer label '
                              'with an N-P-K 4-1-3 rating. It offers a concentrated organic formula for '
                              'nourishing garden plants and crops.',
 'Urea 46-0-0': 'A 50 kg white woven sack clearly printed with green “UREA 46-0-0 NITROGEN FERTILIZER” '
                'lettering. It provides high-nitrogen chemical fertilizer for field crop development.',
 'Complete Fertilizer 14-14-14': 'A 50 kg white bag with blue branding labeled “COMPLETE FERTILIZER 14-14-14 '
                                 'NPK”. It delivers a balanced formula of nitrogen, phosphorus, and '
                                 'potassium for overall plant growth.',
 'Ammonium Sulfate': 'A 50 kg white fertilizer sack labeled “AMMONIUM SULFATE 21-0-0” with orange and black '
                     'text. It provides an essential source of nitrogen and sulfur for crop nutrition.',
 'Muriate of Potash': 'A natural burlap sack with a white label printed “POTASSIUM FERTILIZER 0-0-60”. It '
                      'supplies high-potash nutrients to enhance plant strength and fruit development.',
 'Ammonium Phosphate': 'A white woven fertilizer bag with green accents labeled “AMMONIUM PHOSPHATE '
                       '16-20-0”. It offers a balanced blend of nitrogen and phosphate for early root '
                       'growth.',
 'Rice-Specific Fertilizer': 'A large white sack featuring a green panel with “RICE FERTILIZER” and a rice '
                             'grain illustration. It is specifically formulated to meet the nutrient '
                             'requirements of rice crops.',
 'Vermicast': 'A brown paper bag labeled “VERMICAST ORGANIC SOIL AMENDMENT” featuring an earthworm graphic '
              'on the front. It supplies worm castings to enrich soil structure and plant health '
              'organically.',
 'Compost Fertilizer': 'A tied burlap bag labeled “COMPOST FERTILIZER” with text highlighting nature’s rich '
                       'soil nutrients. It contains organic compost to improve soil fertility and moisture '
                       'retention.',
 'Soil Conditioner': 'A kraft standing pouch with a clear window labeled “SOIL CONDITIONER”. It helps '
                     'enhance soil structure and nutrient absorption for healthier plant root growth.',
 'Virtako Insecticide': 'A box and foil sachet labeled “VIRTAKO 40 WG INSECTICIDE” by Syngenta. It provides '
                        'crop protection against destructive agricultural pests.',
 'Nativo Fungicide': 'A bottle of "NATIVO 75 WG" crop protection fungicide featuring a red cap and clear '
                     'hazard warnings on the label. It is designed to control fungal diseases and safeguard '
                     'crop health.',
 '2,4-D Amine Herbicide': 'A white bottle of broadleaf weed killer equipped with a yellow cap and detailed '
                          'usage instructions. It is formulated to target unwanted broadleaf weeds in farm '
                          'fields.',
 'Frontier Herbicide': 'A sturdy white jug with a black cap labeled "FRONTIER HERBICIDE pre-emergence". It '
                       'helps prevent target weeds from sprouting around crops during early stages.',
 'Surekill Molluscicide': 'A white bottle labeled "SUREKILL MOLLUSCICIDE" with a purple cap, specially '
                          'designated for golden snail snail control. It protects agricultural fields by '
                          'controlling snail infestations effectively.',
 'Banana Chips': 'A clear pouch filled with crunchy, golden-yellow sliced banana chips. It offers a sweet '
                 'and crispy traditional Filipino snack option.',
 'Taro Chips': 'A resealable stand-up pouch containing crisp, lightly speckled taro root chips. It provides '
               'a savory root-vegetable snack packed in a practical clear pouch.',
 'Kangkong Chips': 'A pouch packed with crispy, seasoned water spinach leaves. It delivers a flavorful green '
                   'veggie chip experience.',
 'Ampalaya Chips': 'A clear snack bag containing crispy fried bitter gourd slices. It offers a unique, '
                   'crunchy snack option derived from bitter melon.',
 'Kamote Chips': 'A clear pouch displaying vibrant orange sweet potato chips under the “SUN-CRISP SNACKS” '
                 'label. It provides a crunchy, natural sweet potato snack.',
 'Jackfruit Chips': 'A stand-up bag filled with bright yellow dried jackfruit pieces. It offers a naturally '
                    'sweet and crispy tropical fruit snack.',
 'Cassava Chips': 'A pouch containing light golden cassava root chips. It serves as a crisp and satisfying '
                  'root-crop snack.',
 'Ube Chips': 'A clear bag displaying deep purple yam chips. It provides a colorful and crunchy Filipino ube '
              'snack.',
 'Mushroom Chips': 'A stand-up pouch filled with lightly salted, crispy oyster mushroom chips. It offers a '
                   'savory and earthy plant-based snack.',
 'Coconut Chips': 'A clear bag packed with toasted coconut flakes. It provides a crunchy, aromatic tropical '
                  'snack.',
 'Dried Mangoes': 'A pouch filled with golden, Cebu-style dried mango slices. It offers a chewy and sweet '
                  'tropical fruit treat.',
 'Dried Pineapple': 'A transparent pouch showcasing round dried pineapple rings. It delivers a sweet and '
                    'tangy dried fruit snack.',
 'Knapsack Sprayer': 'A green 16-liter manual backpack sprayer featuring padded shoulder straps and a long '
                     'spray wand attachment. It provides a portable solution for applying liquid treatments '
                     'across large crop areas.',
 'Electric Sprayer': 'Listed as an electric sprayer tool for automated garden and farm spraying tasks. It '
                     'facilitates effortless chemical or water application.',
 'Hand Sprayer': 'A white 2-liter handheld pressure sprayer featuring a green pump handle and adjustable '
                 'brass nozzle. It is ideal for targeted spraying in small gardens or greenhouses.',
 'Sprayer Replacement Parts': 'A collection of black and brass spray nozzles, connectors, hoses, and filter '
                              'fittings. It provides necessary replacement components to maintain '
                              'agricultural spray equipment.',
 'Nozzles and Hoses': 'Listed under sprayers as functional replacement nozzles and liquid delivery hoses. '
                      'They help customize and maintain fluid application systems.',
 'Garden Trowel': 'A polished stainless steel hand trowel crafted with an ergonomic wooden handle and '
                  'hanging loop. It is designed for digging, scooping soil, and transplanting small plants.',
 'Spade': 'A straight-edged metal spade fitted with a durable wooden shaft and D-shaped handle. It is built '
          'for edging, slicing roots, and digging clean trenches.',
 'Sickle': 'Two curved agricultural sickles featuring sharp serrated blades and wooden handles. They are '
           'built for harvesting crops and clearing thick weeds or tall grasses.',
 'Pitchfork': 'Listed under hand tools as a durable pitchfork for farm and garden tasks. It is designed for '
              'lifting, pitching, and moving loose agricultural materials like hay or compost.',
 'Shovel': 'A heavy-duty metal shovel featuring a pointed blade and a sturdy wooden handle with a grip. It '
           'is made for scooping, moving heavy soil, and general digging tasks.',
 'Hoe': 'A traditional farm hoe with a broad metal blade angled on a long wooden handle. It is ideal for '
        'weeding, chopping soil, and shaping crop rows.',
 'Gardening Fork': 'A metal hand fork with long sharp tines and a comfortable wooden handle. It helps '
                   'aerate, loosen, and turn soil around growing plants.',
 'Rake': 'A long-handled metal garden rake fitted with rigid steel tines. It is designed for leveling soil, '
         'gathering debris, and smoothing garden beds.',
 'Bolo': 'A large Filipino bolo knife featuring a heavy steel blade alongside its woven sheath. It is '
         'crafted for clearing brush, cutting branches, and general farm utility work.',
 'Pruning Shears': 'A pair of ergonomic green bypass pruning shears equipped with a spring-loaded mechanism. '
                   'They make clean cuts when trimming plant stems and small branches.',
 'Grass Cutter': 'A gas-powered string trimmer featuring an orange engine, shoulder harness, and cutting '
                 'head. It provides powered clearing of tough weeds, tall grass, and overgrown vegetation.',
 'Watering Can': 'Listed as a watering can designed for manual irrigation tasks. It provides gentle water '
                 'delivery for garden plants and seed beds.',
 'Garden Hose': 'A tightly coiled green garden hose fitted with a heavy-duty brass spray nozzle attachment. '
                'It provides reliable water delivery for various garden and farm irrigation needs.',
 'Water Pump': 'Listed under water and irrigation equipment as a functional water pump. It supports '
               'efficient water movement for agricultural fields or gardens.',
 'Irrigation Pipes': 'Listed under water and irrigation supplies as essential piping components. They help '
                     'construct durable water distribution lines across garden beds or fields.',
 'Drip Irrigation Kit': 'Listed as a drip irrigation setup for target watering. It delivers water directly '
                        'to plant roots to conserve moisture and optimize growth.',
 'Seedling Tray': 'A stacked set of black plastic seed starter trays filled with small soil cells holding '
                  'young plant seedlings. It provides a controlled setup for germinating and nurturing young '
                  'crops before transplanting.',
 'Plant Pots': 'A collection of various terracotta clay pots and black plastic plant containers of different '
               'sizes. They offer flexible potting options for growing plants and flowers.',
 'Harvesting Basket': 'A woven rattan tote basket featuring double top handles and a flat bottom. It '
                      'provides a sturdy, traditional container for collecting harvested produce.',
 'Rice Harvesting Tools': 'Listed under planting and harvest tools for traditional rice gathering tasks. '
                          'They facilitate manual harvesting activities out in the fields.',
 'Grain Tarpaulin': 'A heavy-duty blue waterproof tarp reinforced with an orange border and metallic '
                    'grommets. It helps shield harvested grains from rain, moisture, and ground debris.',
 'Harvesting Sacks': 'Listed under harvesting gear as essential storage sacks for farm yields. They offer '
                     'reliable containment for transporting produce and grains.',
 'Farm Tool Storage Box': 'Listed under planting and harvest gear as a functional farm tool organizer. It '
                          'keeps hand tools neatly organized and easily accessible for outdoor labor.',
 'Measuring Tape': 'A measuring kit featuring a long yellow open-reel tape, a pocket tape measure, and a '
                   'wooden folding ruler. It provides accurate length measurement for field mapping and '
                   'garden layout tasks.',
 'Soil pH Meter': 'A green analog soil tester equipped with a dual-metal probe and a clear reading dial. It '
                  'allows farmers to quickly check soil acidity and moisture levels directly in the ground.',
 'Portable Weighing Scale': 'A digital weighing setup featuring a hanging digital scale with a metal hook '
                            'alongside a compact precision bench scale. It enables precise weight '
                            'measurements for harvested crops or fertilizers.',
 'Protective Goggles': 'Clear, wide-vision safety goggles equipped with a black elastic headband. They '
                       'protect eyes from flying dust, debris, and chemical splashes during farm work.',
 'Respirator': 'Listed under safety gear as essential respiratory protection for agricultural tasks. It '
               'helps filter out airborne dust, organic vapors, and chemical mists during spraying or field '
               'work.',
 'Safety Helmet': 'A bright yellow hard hat featuring an inner suspension harness and an adjustable chin '
                  'strap. It protects the head from impact hazards in construction or heavy farm '
                  'environments.',
 'Ear Protection': 'Listed under safety gear as noise-reducing ear protection equipment. It guards hearing '
                   'against high-decibel noise generated by heavy machinery and power tools',
 'Wheelbarrow': 'A deep green wheelbarrow constructed with a sturdy wooden frame and a single heavy-duty '
                'tire. It enables easy transport of soil, fertilizers, and heavy garden loads.'}

DESCRIPTION_ALIASES = {
    'Neck-Flap Sun Hat': 'Flap Sun Hat',
    '2,4-D Herbicide': '2,4-D Amine Herbicide',
}

for product_item in PRODUCTS:
    description_name = DESCRIPTION_ALIASES.get(product_item['name'], product_item['name'])
    if description_name in WORD_DESCRIPTIONS:
        product_item['description'] = WORD_DESCRIPTIONS[description_name]

CATEGORIES = ['All', 'Apparel', 'Seeds', 'Fertilizer & Crop Care', 'Farm Snacks', 'Farm Equipment']


def get_product(pid): return next((p for p in PRODUCTS if p['id'] == pid), None)


def get_cart():
    result = []; total = 0
    for entry in session.get('cart', []):
        p = get_product(entry['id'])
        if p:
            qty = max(1, int(entry.get('qty', 1))); line = p['price'] * qty; total += line
            result.append({'product': p, 'qty': qty, 'options': entry.get('options', {}), 'line': line})
    return result, total


@app.context_processor
def globals_for_templates():
    items, _ = get_cart()
    return {'cart_count': sum(x['qty'] for x in items), 'categories': CATEGORIES}


def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get('user'):
            flash('Please create an account or log in first.', 'warning'); return redirect(url_for('login'))
        return fn(*args, **kwargs)
    return wrapper


@app.route('/')
def home(): return render_template('home.html', products=PRODUCTS[:8])


@app.route('/shop')
def shop():
    category = request.args.get('category', 'All')
    sub = request.args.get('type', 'All')
    q = request.args.get('q', '').lower().strip()
    products = PRODUCTS
    if category != 'All': products = [p for p in products if p['category'] == category]
    subs = SUBCATEGORIES.get(category, [])
    if sub not in subs: sub = 'All'
    if sub != 'All': products = [p for p in products if p['subcategory'] == sub]
    if q: products = [p for p in products if q in p['name'].lower() or q in p['description'].lower()]
    return render_template('shop.html', products=products, selected_category=category, selected_sub=sub,
                           subcategories=subs, q=q)


@app.route('/product/<pid>')
def product(pid):
    p = get_product(pid)
    if not p: return 'Product not found', 404
    return render_template('product.html', p=p)


@app.post('/add-to-cart')
def add_to_cart():
    p = get_product(request.form.get('product_id'))
    if not p: flash('Product not found.', 'danger'); return redirect(url_for('shop'))
    try: qty = max(1, int(request.form.get('qty', 1)))
    except ValueError: qty = 1
    options = {k[7:]: v for k, v in request.form.items() if k.startswith('option_') and v}
    cart = session.get('cart', []); found = next((x for x in cart if x['id'] == p['id'] and x.get('options', {}) == options), None)
    if found: found['qty'] += qty
    else: cart.append({'id': p['id'], 'qty': qty, 'options': options})
    session['cart'] = cart; flash(f"{p['name']} added to Ani!", 'success')
    return redirect(request.referrer or url_for('shop'))


@app.route('/cart')
def cart():
    items, total = get_cart(); return render_template('cart.html', items=items, total=total)


@app.post('/remove-cart')
def remove_cart():
    pid = request.form.get('product_id'); session['cart'] = [x for x in session.get('cart', []) if x['id'] != pid]; return redirect(url_for('cart'))


@app.route('/checkout', methods=['GET', 'POST'])
@login_required
def checkout():
    items, total = get_cart()
    if not items: flash('Your Ani is empty. Add products first.', 'warning'); return redirect(url_for('shop'))
    if request.method == 'POST':
        name = request.form.get('name', '').strip(); phone = request.form.get('phone', '').strip(); address = request.form.get('address', '').strip(); payment = request.form.get('payment', 'COD')
        if not name or not phone or not address: flash('Complete all delivery details.', 'danger'); return redirect(url_for('checkout'))
        order = {'id': 'ANI-' + uuid.uuid4().hex[:8].upper(), 'created': datetime.now().strftime('%b %d, %Y %I:%M %p'), 'name': name, 'phone': phone, 'address': address, 'payment': payment, 'items': items, 'total': total, 'status': 'Processing', 'timeline': ['Processing'], 'notification': 'Order received and is being prepared.'}
        orders = session.get('orders', []); orders.insert(0, order); session['orders'] = orders; session['cart'] = []
        flash('Order placed. This is a simulated payment; no money was charged.', 'success'); return redirect(url_for('order_detail', order_id=order['id']))
    return render_template('checkout.html', items=items, total=total)


@app.route('/orders')
@login_required
def orders(): return render_template('orders.html', orders=session.get('orders', []))



@app.route('/order/<order_id>')
@login_required
def order_detail(order_id):
    order = next(
        (
            item for item in session.get('orders', [])
            if item.get('id') == order_id
        ),
        None
    )

    if not order:
        return 'Order not found in this browser session.', 404

    conn = get_feedback_db()

    feedback = conn.execute(
        'SELECT * FROM feedback WHERE order_id = ?',
        (order_id,)
    ).fetchone()

    conn.close()

    return render_template(
        'order.html',
        order=order,
        feedback=feedback
    )



@app.route('/notifications')
@login_required
def notifications(): return render_template('notifications.html', orders=session.get('orders', []))


@app.route('/about')
def about(): return render_template('about.html')


@app.route('/contact')
def contact(): return render_template('contact.html')


@app.route('/anisays')
def anisays(): return render_template('anisays.html')


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        name = request.form.get('name', '').strip(); email = request.form.get('email', '').strip().lower(); password = request.form.get('password', '')
        if not name or not email or len(password) < 6: flash('Enter your name, email, and a password of at least 6 characters.', 'danger'); return redirect(url_for('signup'))
        users = session.get('demo_users', {})
        if email in users: flash('Account already exists in this demo session. Log in instead.', 'warning'); return redirect(url_for('login'))
        users[email] = {'name': name, 'password': password}; session['demo_users'] = users; session['user'] = {'name': name, 'email': email}; flash('Demo account created!', 'success'); return redirect(url_for('home'))
    return render_template('login.html', mode='signup')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower(); password = request.form.get('password', ''); users = session.get('demo_users', {})
        if email in users and users[email]['password'] == password:
            session['user'] = {'name': users[email]['name'], 'email': email}; flash('Welcome back!', 'success'); return redirect(url_for('home'))
        flash('Demo login failed. Create an account first in this browser session.', 'warning')
    return render_template('login.html', mode='login')


@app.route('/logout')
def logout(): session.pop('user', None); flash('You have logged out.', 'success'); return redirect(url_for('home'))


@app.route('/admin')
def admin(): return render_template('admin.html', orders=session.get('orders', []))


@app.post('/admin/update-status')
def update_status():
    oid = request.form.get('order_id'); status = request.form.get('status'); allowed = ['Processing', 'Shipped', 'Out for Delivery', 'Delivered']
    if status not in allowed: flash('Invalid status.', 'danger'); return redirect(url_for('admin'))
    orders = session.get('orders', []); order = next((x for x in orders if x['id'] == oid), None)
    if order:
        order['status'] = status
        if status not in order['timeline']: order['timeline'].append(status)
        order['notification'] = f'Order {oid} status updated to {status}.'; session['orders'] = orders; flash('Order status updated.', 'success')
    else: flash('Order not found in this session.', 'warning')
    return redirect(url_for('admin'))
    
# ---------------- CUSTOMER FEEDBACK ----------------

@app.route('/feedback/<order_id>', methods=['GET', 'POST'])
@login_required
def submit_feedback(order_id):
    order = next(
        (
            item for item in session.get('orders', [])
            if item.get('id') == order_id
        ),
        None
    )

    if not order:
        flash('Order not found in your session.', 'warning')
        return redirect(url_for('orders'))

    if order.get('status') != 'Delivered':
        flash('You can review an order only after it is delivered.', 'warning')
        return redirect(url_for('order_detail', order_id=order_id))

    conn = get_feedback_db()

    existing = conn.execute(
        'SELECT id FROM feedback WHERE order_id = ?',
        (order_id,)
    ).fetchone()

    conn.close()

    if existing:
        flash('Feedback has already been submitted for this order.', 'info')
        return redirect(url_for('order_detail', order_id=order_id))

    if request.method == 'POST':
        try:
            rating = int(request.form.get('rating', '0'))
        except (ValueError, TypeError):
            rating = 0

        review = request.form.get('review', '').strip()

        if rating not in range(1, 6):
            flash('Please select a rating from 1 to 5 stars.', 'danger')
            return render_template('feedback.html', order=order)

        if not review:
            flash('Please write a review before submitting.', 'danger')
            return render_template('feedback.html', order=order)

        if len(review) > 2000:
            flash('Your review must be 2,000 characters or fewer.', 'danger')
            return render_template('feedback.html', order=order)

        user = session.get('user', {})
        customer_name = user.get('name', order.get('name', 'Customer'))
        customer_email = user.get('email', '')

        conn = get_feedback_db()

        try:
            conn.execute("""
                INSERT INTO feedback (
                    order_id, customer_name, customer_email,
                    rating, review, created_at
                )
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                order_id,
                customer_name,
                customer_email,
                rating,
                review,
                datetime.now().strftime('%b %d, %Y %I:%M %p')
            ))

            conn.commit()
            flash('Thank you! Your feedback has been submitted.', 'success')

        except sqlite3.IntegrityError:
            flash('Feedback has already been submitted for this order.', 'info')

        finally:
            conn.close()

        return redirect(url_for('order_detail', order_id=order_id))

    return render_template('feedback.html', order=order)


@app.route('/admin/feedback')
def admin_feedback():
    conn = get_feedback_db()

    reviews = conn.execute("""
        SELECT *
        FROM feedback
        ORDER BY id DESC
    """).fetchall()

    conn.close()

    return render_template(
        'admin_feedback.html',
        reviews=reviews
    )



if __name__ == '__main__': app.run(debug=True)
