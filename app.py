import os
import time
from flask import Flask, request, render_template, send_from_directory, Response, redirect, url_for
from ultralytics import YOLO
import cv2
from gtts import gTTS
from deep_translator import GoogleTranslator
import json
from datetime import datetime

app = Flask(__name__)

# CONFIGURATION
UPLOAD_FOLDER = 'static/uploads'
AUDIO_FOLDER = 'static/audio'
MODEL_PATH = 'best.pt'

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['AUDIO_FOLDER'] = AUDIO_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(AUDIO_FOLDER, exist_ok=True)

# LOAD MODEL
print("Loading AI Model...")
try:
    model = YOLO(MODEL_PATH)
    # Check if names exist, then print them clearly
    if hasattr(model, 'names'):
        print("\n" + "="*30)
        print("ACTUAL MODEL BREED NAMES:")
        print(model.names)
        print("="*30 + "\n")
except Exception as e:
    print(f"ERROR LOADING MODEL: {e}")

# ==========================================
# MASTER DATABASE (42 BREEDS)
# ==========================================
cattle_database = {
    'alambadi': {
        'sci_name': 'Bos indicus',
        'origin': 'Tamil Nadu (Dharmapuri)',
        'status': 'Vulnerable',
        'type': 'Draft Breed',
        'specs': 'Dark Grey | 350kg',
        'milk_stats': 'Yield: Negligible',
        'features': ['Backward curving horns', 'White markings on forehead', 'Very hardy nature', 'Excellent for ploughing'],
        'bio': {'lifespan': '15-18 Years', 'climate': 'Hilly/Forest', 'gestation': '280 Days', 'behavior': 'Alert & Active'},
        'desc': 'A hardy draft breed native to the hilly regions of Tamil Nadu, historically used for hauling carts.'
    },
    'amritmahal': {
        'sci_name': 'Bos indicus',
        'origin': 'Karnataka (Mysore)',
        'status': 'Secure',
        'type': 'Draft (Warfare)',
        'specs': 'Lean | Grey/White',
        'milk_stats': 'Yield: Poor',
        'features': ['Long sharp horns', 'Incredible endurance', 'Compact muscular body', 'Historic military breed'],
        'bio': {'lifespan': '20 Years', 'climate': 'Dry/Semi-Arid', 'gestation': '280 Days', 'behavior': 'Fiery & Aggressive'},
        'desc': 'Famous for their speed and endurance, these cattle were historically used by armies to transport heavy artillery.'
    },
    'ayrshire': {
        'sci_name': 'Bos taurus',
        'origin': 'Scotland',
        'status': 'Commercial',
        'type': 'Dairy Breed',
        'specs': 'Red & White | Medium',
        'milk_stats': 'Yield: 5000kg | Fat: 4.0%',
        'features': ['Distinct red and white spots', 'Curved lyre-shaped horns', 'Excellent udder conformation', 'Efficient forager'],
        'bio': {'lifespan': '15-17 Years', 'climate': 'Temperate', 'gestation': '279 Days', 'behavior': 'Active & Dominant'},
        'desc': 'An exotic dairy breed known for its ability to convert grass into milk efficiently and survive in tough climates.'
    },
    'banni': {
        'sci_name': 'Bubalus bubalis',
        'origin': 'Gujarat (Kutch)',
        'status': 'Secure',
        'type': 'Dairy Buffalo',
        'specs': 'Black | Coiled Horns',
        'milk_stats': 'Yield: High',
        'features': ['Double coiled horns', 'Nocturnal grazing habit', 'Black coat', 'Extreme heat tolerance'],
        'bio': {'lifespan': '18 Years', 'climate': 'Desert', 'gestation': '310 Days', 'behavior': 'Independent'},
        'desc': 'A unique buffalo breed that grazes at night to avoid the desert heat and returns home on its own.'
    },
    'bargur': {
        'sci_name': 'Bos indicus',
        'origin': 'Tamil Nadu (Erode)',
        'status': 'Endangered',
        'type': 'Draft (Hill)',
        'specs': 'Small | Brown/Spotted',
        'milk_stats': 'Yield: Low',
        'features': ['Forest-dwelling breed', 'Brown coat with white spots', 'Extremely sure-footed', 'Semi-wild nature'],
        'bio': {'lifespan': '15 Years', 'climate': 'Forest/Hills', 'gestation': '280 Days', 'behavior': 'Shy & Wary'},
        'desc': 'Bred in the Bargur hills, these cattle are known for their speed and agility in uneven forest terrains.'
    },
    'bhadawari': {
        'sci_name': 'Bubalus bubalis',
        'origin': 'Uttar Pradesh (Agra)',
        'status': 'Secure',
        'type': 'Dairy Buffalo',
        'specs': 'Copper Color',
        'milk_stats': 'Yield: High Fat (13%)',
        'features': ['Copper/Light brown coat', 'Two white lines (Chevron)', 'Wedge shaped body', 'Highest butterfat content'],
        'bio': {'lifespan': '18 Years', 'climate': 'Hot/Ravines', 'gestation': '310 Days', 'behavior': 'Docile'},
        'desc': 'Famous for producing milk with the highest butterfat content (up to 13%) among all Indian buffalo breeds.'
    },
    'brown_swiss': {
        'sci_name': 'Bos taurus',
        'origin': 'Switzerland (Alps)',
        'status': 'Common',
        'type': 'Dairy Breed',
        'specs': 'Large | 600-700kg',
        'milk_stats': 'High Yield | High Protein',
        'features': ['Light brown to grey coat', 'Black muzzle with white ring', 'Large fuzzy ears', 'Very strong legs and hooves'],
        'bio': {'lifespan': '12-15 Years', 'climate': 'Cold/Mountainous', 'gestation': '290 Days', 'behavior': 'Docile'},
        'desc': 'One of the oldest dairy breeds, known for their longevity, strong legs, and milk that is excellent for making cheese.'
    },
    'dangi': {
        'sci_name': 'Bos indicus',
        'origin': 'Maharashtra (Nashik)',
        'status': 'Secure',
        'type': 'Draft Breed',
        'specs': 'Spotted Black/White',
        'milk_stats': 'Yield: Low',
        'features': ['Oily skin (Rain proof)', 'Distinct spotted coat', 'Strong black hooves', 'Heavy rainfall tolerance'],
        'bio': {'lifespan': '16 Years', 'climate': 'Heavy Rain/Ghats', 'gestation': '280 Days', 'behavior': 'Energetic'},
        'desc': 'Specially adapted to the Western Ghats, their oily skin helps them work tirelessly in heavy rainfall areas.'
    },
    'deoni': {
        'sci_name': 'Bos indicus',
        'origin': 'Maharashtra (Latur)',
        'status': 'Secure',
        'type': 'Dual Purpose',
        'specs': 'Black & White Spots',
        'milk_stats': 'Yield: Moderate',
        'features': ['Drooping ears', 'Prominent bulging forehead', 'Black and white spotting', 'Thick loose skin'],
        'bio': {'lifespan': '15 Years', 'climate': 'Tropical', 'gestation': '280 Days', 'behavior': 'Calm & Gentle'},
        'desc': 'Often called the "Dongari", this breed resembles the Gir but is adapted to the rocky terrain of the Deccan plateau.'
    },
    'gir': {
        'sci_name': 'Bos indicus',
        'origin': 'Gujarat (Gir Forest)',
        'status': 'High Value',
        'type': 'Dairy Breed',
        'specs': 'Red | Convex Head',
        'milk_stats': 'Yield: 2500kg | Fat: 4.5%',
        'features': ['Domed forehead', 'Long pendulous ears', 'Curved horns', 'Very gentle nature'],
        'bio': {'lifespan': '15-18 Years', 'climate': 'Tropical/Hot', 'gestation': '280 Days', 'behavior': 'Very Gentle'},
        'desc': 'A world-famous Indian dairy breed, highly prized for its A2 milk and used globally to improve tropical herds.'
    },
    'guernsey': {
        'sci_name': 'Bos taurus',
        'origin': 'Guernsey (UK)',
        'status': 'Commercial',
        'type': 'Dairy Breed',
        'specs': 'Fawn & White',
        'milk_stats': 'Yield: 4500kg | High Beta-Carotene',
        'features': ['Golden-yellow milk', 'Fawn and white markings', 'Fine bone structure', 'High feed efficiency'],
        'bio': {'lifespan': '14 Years', 'climate': 'Cool/Temperate', 'gestation': '280 Days', 'behavior': 'Docile'},
        'desc': 'Known as "The Golden Guernsey", their milk is rich in beta-carotene, giving it a distinctive golden color.'
    },
    'hallikar': {
        'sci_name': 'Bos indicus',
        'origin': 'Karnataka',
        'status': 'Secure',
        'type': 'Draft Breed',
        'specs': 'Dark Grey | Muscular',
        'milk_stats': 'Yield: Negligible',
        'features': ['Long vertical backward horns', 'Compact muscular body', 'Fast trotting gait', 'Long slender legs'],
        'bio': {'lifespan': '18-20 Years', 'climate': 'Semi-Arid', 'gestation': '280 Days', 'behavior': 'Spirited'},
        'desc': 'Considered the "Thoroughbred" of draft cattle, Hallikars are the progenitors of many South Indian breeds.'
    },
    'hariana': {
        'sci_name': 'Bos indicus',
        'origin': 'Haryana',
        'status': 'Secure',
        'type': 'Dual Purpose',
        'specs': 'White | Compact',
        'milk_stats': 'Yield: 1000kg',
        'features': ['High prominent hump', 'Compact symmetric body', 'Long narrow face', 'Short horns'],
        'bio': {'lifespan': '15 Years', 'climate': 'Dry/Arid', 'gestation': '280 Days', 'behavior': 'Active'},
        'desc': 'The premier dual-purpose breed of North India, valued equally for powerful bullocks and milk production.'
    },
    'holstein_friesian': {
        'sci_name': 'Bos taurus',
        'origin': 'Netherlands',
        'status': 'Commercial',
        'type': 'Dairy Breed',
        'specs': 'Black & White | Large',
        'milk_stats': 'Yield: 8000kg+ (Highest)',
        'features': ['Distinct black and white patches', 'Largest dairy breed size', 'Large developed udder', 'High food intake'],
        'bio': {'lifespan': '10-12 Years', 'climate': 'Cool/Temperate', 'gestation': '280 Days', 'behavior': 'Calm'},
        'desc': 'The world\'s most popular dairy breed, unmatchable in sheer volume of milk production.'
    },
    'jaffrabadi': {
        'sci_name': 'Bubalus bubalis',
        'origin': 'Gujarat (Saurashtra)',
        'status': 'Secure',
        'type': 'Dairy Buffalo',
        'specs': 'Massive | Black',
        'milk_stats': 'Yield: High',
        'features': ['Heavy drooping horns', 'Massive domed forehead', 'Largest buffalo breed', 'Black color'],
        'bio': {'lifespan': '18-20 Years', 'climate': 'Hot/Coastal', 'gestation': '310 Days', 'behavior': 'Slow & Heavy'},
        'desc': 'The heaviest buffalo breed in India, known for high milk yields and its massive physical presence.'
    },
    'jersey': {
        'sci_name': 'Bos taurus',
        'origin': 'Jersey (UK)',
        'status': 'Commercial',
        'type': 'Dairy Breed',
        'specs': 'Small | Fawn',
        'milk_stats': 'Yield: 4000kg | Fat: 5.5%',
        'features': ['High butterfat content', 'Concave face', 'Light brown color', 'Adaptable to climates'],
        'bio': {'lifespan': '15 Years', 'climate': 'Adaptable', 'gestation': '278 Days', 'behavior': 'Curious & Docile'},
        'desc': 'A small breed famous for its rich, creamy milk and high adaptability to different climates.'
    },
    'kangayam': {
        'sci_name': 'Bos indicus',
        'origin': 'Tamil Nadu (Erode)',
        'status': 'Secure',
        'type': 'Draft Breed',
        'specs': 'Grey | Stout',
        'milk_stats': 'Yield: 540kg',
        'features': ['Thick sturdy horns', 'Short strong neck', 'Grey coat', 'Compact body'],
        'bio': {'lifespan': '18 Years', 'climate': 'Dry/Hot', 'gestation': '280 Days', 'behavior': 'Alert & Strong'},
        'desc': 'The "Designated Draft Breed" of Tamil Nadu, historically associated with the Korangadu pasture lands.'
    },
    'kankrej': {
        'sci_name': 'Bos indicus',
        'origin': 'Gujarat (Kutch)',
        'status': 'Secure',
        'type': 'Dual Purpose',
        'specs': 'Silver Grey | Tall',
        'milk_stats': 'Yield: 1700kg',
        'features': ['Heaviest Indian breed', 'Large lyre-shaped horns', 'Unique Sawai gait', 'Broad forehead'],
        'bio': {'lifespan': '20 Years', 'climate': 'Desert/Arid', 'gestation': '290 Days', 'behavior': 'Powerful'},
        'desc': 'A majestic and powerful breed known for its unique smooth gait and massive curved horns.'
    },
    'kasargod': {
        'sci_name': 'Bos indicus',
        'origin': 'Kerala (Kasargod)',
        'status': 'Rare',
        'type': 'Draft / Milk',
        'specs': 'Dwarf | Black/Red',
        'milk_stats': 'Yield: Low | Nutritious',
        'features': ['Extremely small stature', 'High mineral content milk', 'Dark skin tone', 'Low feed requirement'],
        'bio': {'lifespan': '15 Years', 'climate': 'Humid/Coastal', 'gestation': '280 Days', 'behavior': 'Docile'},
        'desc': 'A rare dwarf cattle breed from Northern Kerala, capable of surviving on kitchen scraps and jungle forage.'
    },
    'kenkatha': {
        'sci_name': 'Bos indicus',
        'origin': 'Bundelkhand (UP/MP)',
        'status': 'Secure',
        'type': 'Draft Breed',
        'specs': 'Small | Grey',
        'milk_stats': 'Yield: Poor',
        'features': ['Small sturdy build', 'Short broad head', 'Grey color', 'Strong feet'],
        'bio': {'lifespan': '15 Years', 'climate': 'Rocky/Arid', 'gestation': '280 Days', 'behavior': 'Hardy'},
        'desc': 'A hardy breed that thrives on poor quality fodder in the rocky terrain of the Bundelkhand region.'
    },
    'kherigarh': {
        'sci_name': 'Bos indicus',
        'origin': 'Uttar Pradesh',
        'status': 'Secure',
        'type': 'Draft Breed',
        'specs': 'White | Medium',
        'milk_stats': 'Yield: Low',
        'features': ['White coat color', 'Thin upturned horns', 'Active worker', 'Small narrow face'],
        'bio': {'lifespan': '15 Years', 'climate': 'Sub-humid', 'gestation': '280 Days', 'behavior': 'Active'},
        'desc': 'Primarily used for light draft work, this breed is known for its stamina in field operations.'
    },
    'khillari': {
        'sci_name': 'Bos indicus',
        'origin': 'Maharashtra (Satara)',
        'status': 'Secure',
        'type': 'Draft Breed',
        'specs': 'Grey-White | Muscular',
        'milk_stats': 'Yield: Low',
        'features': ['Long pointed horns', 'Lean athletic body', 'Very fast pace', 'Pinkish muzzle'],
        'bio': {'lifespan': '18 Years', 'climate': 'Dry', 'gestation': '280 Days', 'behavior': 'Hot Tempered'},
        'desc': 'Known as the "Race Car" of cattle, they are prized for their speed and ability to work without pause.'
    },
    'krishna_valley': {
        'sci_name': 'Bos indicus',
        'origin': 'Karnataka',
        'status': 'Vulnerable',
        'type': 'Draft Breed',
        'specs': 'Massive | Grey',
        'milk_stats': 'Yield: Moderate',
        'features': ['Massive heavy build', 'Deep broad chest', 'Small curved horns', 'Short legs'],
        'bio': {'lifespan': '18 Years', 'climate': 'Riverine', 'gestation': '280 Days', 'behavior': 'Slow & Strong'},
        'desc': 'Specifically bred for ploughing the sticky black cotton soil found along the Krishna River valley.'
    },
    'malnad_gidda': {
        'sci_name': 'Bos indicus',
        'origin': 'Karnataka (Western Ghats)',
        'status': 'Secure',
        'type': 'Draft / Milk',
        'specs': 'Dwarf | Black/Brown',
        'milk_stats': 'Yield: Low | Medicinal Value',
        'features': ['Small compact body', 'Ability to jump fences', 'High disease resistance', 'Tail touches ground'],
        'bio': {'lifespan': '15 Years', 'climate': 'Rainy/Forest', 'gestation': '280 Days', 'behavior': 'Agile & Smart'},
        'desc': 'A smart, agile dwarf breed from the Western Ghats, known for yielding small amounts of highly nutritious milk.'
    },
    'mehsana': {
        'sci_name': 'Bubalus bubalis',
        'origin': 'Gujarat (Mehsana)',
        'status': 'Commercial',
        'type': 'Dairy Buffalo',
        'specs': 'Black | Medium',
        'milk_stats': 'Yield: 1500kg',
        'features': ['Intermediate of Murrah/Surti', 'Persistent milker', 'Longer body', 'Black skin'],
        'bio': {'lifespan': '18 Years', 'climate': 'Semi-Arid', 'gestation': '310 Days', 'behavior': 'Docile'},
        'desc': 'Developed by crossing Murrah and Surti breeds, it is prized for its long lactation period and steady production.'
    },
    'murrah': {
        'sci_name': 'Bubalus bubalis',
        'origin': 'Haryana',
        'status': 'Top Tier',
        'type': 'Dairy Buffalo',
        'specs': 'Jet Black',
        'milk_stats': 'Yield: 2500kg+',
        'features': ['Tightly curled horns', 'Jet black skin', 'Short lean neck', 'Long tail'],
        'bio': {'lifespan': '20 Years', 'climate': 'Hot/Dry', 'gestation': '310 Days', 'behavior': 'Docile'},
        'desc': 'Known as the "Black Gold" of India, Murrah is the premier milking buffalo breed globally.'
    },
    'nagori': {
        'sci_name': 'Bos indicus',
        'origin': 'Rajasthan (Nagaur)',
        'status': 'Secure',
        'type': 'Draft Breed',
        'specs': 'White | Tall',
        'milk_stats': 'Yield: Low',
        'features': ['Long powerful legs', 'Flat forehead', 'White coat', 'Large eyes'],
        'bio': {'lifespan': '15 Years', 'climate': 'Desert', 'gestation': '280 Days', 'behavior': 'Fast'},
        'desc': 'One of the most famous trotting breeds, extensively used for fast transport in the sandy desert terrain.'
    },
    'nagpuri': {
        'sci_name': 'Bubalus bubalis',
        'origin': 'Maharashtra (Vidarbha)',
        'status': 'Secure',
        'type': 'Dual Purpose',
        'specs': 'Black | Long Horns',
        'milk_stats': 'Yield: Moderate',
        'features': ['Long sword-shaped horns', 'Black coat', 'Light white markings', 'Adapted to harsh climate'],
        'bio': {'lifespan': '18 Years', 'climate': 'Central Plateau', 'gestation': '310 Days', 'behavior': 'Active'},
        'desc': 'Also called Ellichpuri, this breed is versatile, used for both milk and heavy draft work in Central India.'
    },
    'nili_ravi': {
        'sci_name': 'Bubalus bubalis',
        'origin': 'Punjab',
        'status': 'Secure',
        'type': 'Dairy Buffalo',
        'specs': 'Black & White',
        'milk_stats': 'Yield: High',
        'features': ['Panch Kalyani markings', 'Wall eyes (White iris)', 'Black body', 'Curled horns'],
        'bio': {'lifespan': '18 Years', 'climate': 'Riverine', 'gestation': '310 Days', 'behavior': 'Docile'},
        'desc': 'Easily identified by its "Panch Kalyani" (5 white markings) and unique white iris.'
    },
    'nimari': {
        'sci_name': 'Bos indicus',
        'origin': 'Madhya Pradesh (Narmada)',
        'status': 'Secure',
        'type': 'Draft Breed',
        'specs': 'Red & White',
        'milk_stats': 'Yield: Low',
        'features': ['Copper red patches', 'Massive hump', 'Hard red hooves', 'Curved horns'],
        'bio': {'lifespan': '15 Years', 'climate': 'Dry', 'gestation': '280 Days', 'behavior': 'Aggressive'},
        'desc': 'Resembles the Gir in coloration and the Khillari in body structure, making it a tough worker.'
    },
    'ongole': {
        'sci_name': 'Bos indicus',
        'origin': 'Andhra Pradesh',
        'status': 'Export Quality',
        'type': 'Dual Purpose',
        'specs': 'White | Massive',
        'milk_stats': 'Yield: 1000kg',
        'features': ['Large muscular body', 'Short stumpy horns', 'Great heat tolerance', 'Global export breed'],
        'bio': {'lifespan': '20 Years', 'climate': 'Tropical/Humid', 'gestation': '285 Days', 'behavior': 'Dominant'},
        'desc': 'The ancestor of the Brahman breed, Ongoles are known worldwide for their size and disease resistance.'
    },
    'pandharpuri': {
        'sci_name': 'Bubalus bubalis',
        'origin': 'Maharashtra (Solapur)',
        'status': 'Secure',
        'type': 'Dairy Buffalo',
        'specs': 'Black | Long Flat Horns',
        'milk_stats': 'Yield: 1400kg | High Fat',
        'features': ['Long sword-like flat horns', 'Medium body size', 'Very hardy nature', 'High reproductive efficiency'],
        'bio': {'lifespan': '18-20 Years', 'climate': 'Dry/Hot', 'gestation': '310 Days', 'behavior': 'Docile & Active'},
        'desc': 'Native to the Pandharpur region, this breed is easily recognized by its exceptionally long, flat horns.'
    },
    'pulikulam': {
        'sci_name': 'Bos indicus',
        'origin': 'Tamil Nadu (Madurai)',
        'status': 'Cultural',
        'type': 'Draft / Sport',
        'specs': 'Grey | Compact',
        'milk_stats': 'Yield: Low',
        'features': ['Backward pointing horns', 'Compact muscular body', 'Used for Jallikattu', 'Aggressive nature'],
        'bio': {'lifespan': '15 Years', 'climate': 'Hot/Dry', 'gestation': '280 Days', 'behavior': 'Aggressive'},
        'desc': 'Raised specifically for the traditional bull-taming sport Jallikattu.'
    },
    'rathi': {
        'sci_name': 'Bos indicus',
        'origin': 'Rajasthan (Bikaner)',
        'status': 'Secure',
        'type': 'Dairy Breed',
        'specs': 'Brown/White spots',
        'milk_stats': 'Yield: 1500kg+',
        'features': ['Symmetrical body', 'Brown and white patches', 'Short horns', 'Good milker'],
        'bio': {'lifespan': '15 Years', 'climate': 'Desert/Arid', 'gestation': '280 Days', 'behavior': 'Gentle'},
        'desc': 'An excellent indigenous dairy breed for arid regions, often called the "Poor man\'s cow".'
    },
    'red_dane': {
        'sci_name': 'Bos taurus',
        'origin': 'Denmark',
        'status': 'Commercial',
        'type': 'Dairy Breed',
        'specs': 'Reddish | Large',
        'milk_stats': 'Yield: High',
        'features': ['Deep red coat', 'Large body frame', 'High milk production', 'Fast growth rate'],
        'bio': {'lifespan': '12 Years', 'climate': 'Cool', 'gestation': '280 Days', 'behavior': 'Docile'},
        'desc': 'A heavy European breed used for crossbreeding to improve milk yields.'
    },
    'red_sindhi': {
        'sci_name': 'Bos indicus',
        'origin': 'Pakistan (Sindh)',
        'status': 'High Value',
        'type': 'Dairy Breed',
        'specs': 'Deep Red',
        'milk_stats': 'Yield: 1800kg',
        'features': ['Deep red color', 'Compact body', 'High heat tolerance', 'Thick skin'],
        'bio': {'lifespan': '15 Years', 'climate': 'Hot/Arid', 'gestation': '280 Days', 'behavior': 'Docile'},
        'desc': 'Genetically similar to Sahiwal, renowned for high milk production in extreme heat.'
    },
    'sahiwal': {
        'sci_name': 'Bos indicus',
        'origin': 'Punjab',
        'status': 'Top Tier',
        'type': 'Dairy Breed',
        'specs': 'Reddish Dun',
        'milk_stats': 'Yield: 2700kg',
        'features': ['Loose skin (Lola)', 'Reddish dun color', 'Short horns', 'Massive hump'],
        'bio': {'lifespan': '18-20 Years', 'climate': 'Hot/Dry', 'gestation': '280 Days', 'behavior': 'Lethargic/Calm'},
        'desc': 'Considered the best indigenous dairy breed in India, known for its sweet milk.'
    },
    'surti': {
        'sci_name': 'Bubalus bubalis',
        'origin': 'Gujarat (Surat)',
        'status': 'Secure',
        'type': 'Dairy Buffalo',
        'specs': 'Small | Sickle Horns',
        'milk_stats': 'Yield: Moderate',
        'features': ['Sickle shaped horns', 'Two white collars', 'Rusty brown color', 'Compact body'],
        'bio': {'lifespan': '15 Years', 'climate': 'Moderate', 'gestation': '305 Days', 'behavior': 'Gentle'},
        'desc': 'An economical breed ideal for small farmers, known for high fat milk.'
    },
    'tharparkar': {
        'sci_name': 'Bos indicus',
        'origin': 'Rajasthan (Thar Desert)',
        'status': 'Secure',
        'type': 'Dual Purpose',
        'specs': 'White | Medium',
        'milk_stats': 'Yield: 2000kg',
        'features': ['White coat', 'Large drooping ears', 'Disease resistance', 'Arid climate tolerance'],
        'bio': {'lifespan': '20 Years', 'climate': 'Desert', 'gestation': '280 Days', 'behavior': 'Hardy'},
        'desc': 'A desert breed capable of producing milk even under severe drought conditions.'
    },
    'toda': {
        'sci_name': 'Bubalus bubalis',
        'origin': 'Tamil Nadu (Nilgiris)',
        'status': 'Endangered',
        'type': 'Cultural',
        'specs': 'Furry | Ash Grey',
        'milk_stats': 'Yield: Low',
        'features': ['Thick hairy coat', 'Wide crescent horns', 'Ash grey color', 'Distinct hump'],
        'bio': {'lifespan': '18 Years', 'climate': 'Cold Mountain', 'gestation': '310 Days', 'behavior': 'Semi-Wild'},
        'desc': 'The sacred buffalo of the Toda tribe in the Nilgiris.'
    },
    'umblachery': {
        'sci_name': 'Bos indicus',
        'origin': 'Tamil Nadu (Thanjavur)',
        'status': 'Secure',
        'type': 'Draft Breed',
        'specs': 'Grey (Calves Red)',
        'milk_stats': 'Yield: Low',
        'features': ['Calves born red', 'White star on forehead', 'White tail switch', 'Short legs'],
        'bio': {'lifespan': '15 Years', 'climate': 'Humid/Marshy', 'gestation': '280 Days', 'behavior': 'Semi-Wild'},
        'desc': 'Specifically adapted to the marshy paddy fields of the Cauvery delta.'
    },
    'vechur': {
        'sci_name': 'Bos indicus',
        'origin': 'Kerala (Vechur)',
        'status': 'Conservation',
        'type': 'Dual Purpose',
        'specs': 'Tiny | 90cm Height',
        'milk_stats': 'Yield: 560kg',
        'features': ['Smallest cattle breed', 'High disease resistance', 'Medicinal milk', 'Low feed intake'],
        'bio': {'lifespan': '15 Years', 'climate': 'Humid/Tropical', 'gestation': '280 Days', 'behavior': 'Docile'},
        'desc': 'Guinness World Record holder for the smallest cattle breed.'
    },
    'default': {
        'sci_name': '-', 'origin': '-', 'status': '-', 'type': '-', 'specs': '-', 'milk_stats': '-', 'features': ['No data'],
        'desc': 'Breed characteristics are not in the database.', 'bio': {'lifespan': '-', 'climate': '-', 'gestation': '-', 'behavior': '-'}
    }
}

# GLOBAL CAMERA
camera = None

# --- CAMERA HELPERS ---
def release_camera():
    global camera
    if camera is not None:
        if camera.isOpened():
            camera.release()
        camera = None

def generate_frames():
    global camera
    if camera is None or not camera.isOpened():
        camera = cv2.VideoCapture(0)
    while True:
        if camera is None or not camera.isOpened(): break
        success, frame = camera.read()
        if not success: break
        
        # DRAWING PARAMETERS FOR LIVE FEED
        results = model.predict(frame, show=False)
        for r in results:
            for box in r.boxes:
                conf = float(box.conf[0])
                # Filter out low-confidence false positives
                if conf >= 0.45:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    label = model.names[int(box.cls[0])]
                    # Format label to title case and include confidence
                    display_label = f"{label.replace('_', ' ').title()} {conf:.0%}"
                    # ORIGINAL THICKNESS & FONT
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    cv2.putText(frame, display_label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)

        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\nContent-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
# --- DATA STORAGE HELPER ---
HISTORY_FILE = 'scan_history.json'

def save_scan(breed, score):
    # 1. Load existing history
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            history = json.load(f)
    else:
        history = []

    # 2. Add new scan
    new_entry = {
        'breed': breed,
        'score': float(score.strip('%')), # Remove % sign to save as number
        'date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    history.insert(0, new_entry) # Add to top of list

    # 3. Save back to file
    with open(HISTORY_FILE, 'w') as f:
        json.dump(history, f, indent=4)        

# --- ROUTES ---

@app.route('/')
def landing():
    release_camera() # FORCE KILL
    return render_template('landing.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    release_camera() # FORCE KILL
    if request.method == 'POST': return redirect(url_for('menu'))
    return render_template('login.html')

@app.route('/menu')
def menu():
    release_camera() # FORCE KILL
    return render_template('menu.html')

@app.route('/predict', methods=['GET', 'POST'])
def predict():
    release_camera()
    if request.method == 'POST':
        if 'file' not in request.files: return "No file", 400
        file = request.files['file']
        if file.filename == '': return "No file", 400
        if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg')): return "Please upload a valid image file.", 400
        
        audio_lang = request.form.get('language', 'en')
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        
        # 1. RUN PREDICTION
        results = model(filepath)

        breed_name = "default"
        conf_score = "0.00"

        if results and len(results[0].boxes) > 0:

            # get confidence value
             raw_conf = float(results[0].boxes[0].conf[0])
  
            # 35% confidence threshold
             if raw_conf >= 0.35:

            # get predicted breed name
                 raw_name = model.names[int(results[0].boxes[0].cls[0])]

            # standardize breed name
                 breed_name = raw_name.lower().strip().replace(" ", "_")

            # format confidence
                 conf_score = f"{raw_conf:.2%}"

             # save scan only for valid predictions
                 save_scan(breed_name, conf_score)

             else:
                 breed_name = "default"
                 conf_score = f"{raw_conf:.2%} (Low Confidence)"

        # 2. DRAW VISUALS (Bold Style preserved)
        img = cv2.imread(filepath)
        if results and len(results[0].boxes) > 0:
            for r in results:
                for box in r.boxes:
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    # Original bold thickness
                    cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                    # Original bold text
                    display_label = breed_name.replace("_", " ").title()
                    cv2.putText(img, display_label, (x1, y1-10), 
                                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        cv2.imwrite(filepath, img)

        # 3. GET DETAILS & AUDIO SCRIPT
        details = cattle_database.get(breed_name, cattle_database.get('default'))
        features_list = ", ".join(details.get('features', []))
        bio = details.get('bio', {})
        
        # SCRIPT FIXED: Now includes PHYSICAL SPECS and BIOLOGICAL PROFILE
        audio_text = (
            f"The identified breed is {breed_name.replace('_', ' ')}. "
            f"Originating from {details.get('origin')}. "
            f"This is a {details.get('type')} type breed. "
            f"Physical specifications are {details.get('specs')}. "
            f"Milk statistics: {details.get('milk_stats')}. "
            f"Key features include: {features_list}. "
            f"Biological Profile details: "
            f"The typical lifespan is {bio.get('lifespan', 'Not mentioned')}. "
            f"It is suited for {bio.get('climate', 'Not mentioned')} climates. "
            f"Gestation period is {bio.get('gestation', 'Not mentioned')}. "
            f"Behavior is generally {bio.get('behavior', 'Not mentioned')}. "
            f"Summary: {details.get('desc')}"
        )

        # 4. TRANSLATE & GENERATE AUDIO
        if audio_lang != 'en':
            try:
                audio_text = GoogleTranslator(source='auto', target=audio_lang).translate(audio_text)
            except:
                pass

        audio_filename = f"audio_{int(time.time())}.mp3"
        try:
            tts = gTTS(text=audio_text, lang=audio_lang, slow=False)
            tts.save(os.path.join(app.config['AUDIO_FOLDER'], audio_filename))
        except:
            audio_filename = None
         
        display_breed = "Breed Not Recognized" if breed_name == "default" else breed_name
        return render_template('predict.html', uploaded_image=file.filename, 
                               breed=display_breed.replace('_', ' ').title(), score=conf_score, 
                               details=details, audio_file=audio_filename)

    return render_template('predict.html')

@app.route('/analytics')
def analytics():
    # Load Data
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            data = json.load(f)
    else:
        data = []

    # Calculate Stats for Charts
    breed_counts = {}
    total_score = 0

    for entry in data:
        b = entry['breed'].title()
        breed_counts[b] = breed_counts.get(b, 0) + 1
        total_score += entry['score']

    avg_conf = round(total_score / len(data), 2) if data else 0

    return render_template('analytics.html', 
                           history=data, 
                           labels=list(breed_counts.keys()), 
                           values=list(breed_counts.values()),
                           avg_conf=avg_conf,
                           total_scans=len(data))

@app.route('/clear_history')
def clear_history():
    if os.path.exists(HISTORY_FILE):
        os.remove(HISTORY_FILE) 
    return redirect(url_for('analytics'))

@app.route('/live')
def live(): return render_template('live.html')

@app.route('/video_feed')
def video_feed(): return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/stop_camera')
def stop_camera():
    release_camera()
    return redirect(url_for('menu'))

@app.route('/static/<path:filename>')
def serve_static(filename): return send_from_directory('static', filename)

if __name__ == '__main__':
    app.run(debug=True)