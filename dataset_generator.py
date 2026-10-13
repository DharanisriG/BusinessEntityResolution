"""
Synthetic Dataset Generator for Business Entity Resolution.
Generates realistic multi-source business records with varied formats, typos,
abbreviations, missing values, and ground truth entity clusters.
"""

import os
import random
import pandas as pd
import numpy as np

SEED = 42
random.seed(SEED)
np.random.seed(SEED)

# Canonical seed businesses pool (120 businesses for train, 60 for test)
CANONICAL_BUSINESS_TEMPLATES = [
    {"base": "Apex Technology Solutions", "sector": "Tech", "city": "San Francisco", "state": "CA", "country": "USA", "domain": "apextech.com", "phone_area": "415"},
    {"base": "Beacon Financial Advisory", "sector": "Finance", "city": "New York", "state": "NY", "country": "USA", "domain": "beaconfa.com", "phone_area": "212"},
    {"base": "Cascade Global Logistics", "sector": "Logistics", "city": "Seattle", "state": "WA", "country": "USA", "domain": "cascadelogistics.com", "phone_area": "206"},
    {"base": "Delta Health Pharmaceuticals", "sector": "Healthcare", "city": "Boston", "state": "MA", "country": "USA", "domain": "deltahealth.com", "phone_area": "617"},
    {"base": "Evergreen Renewable Energy", "sector": "Energy", "city": "Denver", "state": "CO", "country": "USA", "domain": "evergreenenergy.org", "phone_area": "303"},
    {"base": "Frontier Robotics & Automation", "sector": "Tech", "city": "Austin", "state": "TX", "country": "USA", "domain": "frontierrobotics.io", "phone_area": "512"},
    {"base": "Golden Gate Retail Enterprises", "sector": "Retail", "city": "San Francisco", "state": "CA", "country": "USA", "domain": "goldengateretail.com", "phone_area": "415"},
    {"base": "Horizon Aerospace Engineering", "sector": "Aerospace", "city": "Los Angeles", "state": "CA", "country": "USA", "domain": "horizonaero.com", "phone_area": "310"},
    {"base": "Infinity Cloud Networks", "sector": "Tech", "city": "Chicago", "state": "IL", "country": "USA", "domain": "infinitycloud.net", "phone_area": "312"},
    {"base": "Jupiter BioSciences Lab", "sector": "Healthcare", "city": "San Diego", "state": "CA", "country": "USA", "domain": "jupiterbiosci.com", "phone_area": "858"},
    {"base": "Keystone Construction Group", "sector": "Construction", "city": "Philadelphia", "state": "PA", "country": "USA", "domain": "keystonebuild.com", "phone_area": "215"},
    {"base": "Lumina Creative Media", "sector": "Media", "city": "Atlanta", "state": "GA", "country": "USA", "domain": "luminamedia.agency", "phone_area": "404"},
    {"base": "Matrix Cyber Defense", "sector": "Tech", "city": "Washington", "state": "DC", "country": "USA", "domain": "matrixcybersec.com", "phone_area": "202"},
    {"base": "Nexus Semiconductor Works", "sector": "Tech", "city": "San Jose", "state": "CA", "country": "USA", "domain": "nexussemi.com", "phone_area": "408"},
    {"base": "Orion Asset Management", "sector": "Finance", "city": "Charlotte", "state": "NC", "country": "USA", "domain": "orionasset.com", "phone_area": "704"},
    {"base": "Pinnacle Food Brands", "sector": "Food", "city": "Portland", "state": "OR", "country": "USA", "domain": "pinnaclefood.com", "phone_area": "503"},
    {"base": "Quantum Materials Research", "sector": "Science", "city": "Raleigh", "state": "NC", "country": "USA", "domain": "quantummat.org", "phone_area": "919"},
    {"base": "Radiant Solar Systems", "sector": "Energy", "city": "Phoenix", "state": "AZ", "country": "USA", "domain": "radiantsolar.com", "phone_area": "602"},
    {"base": "Silverline Maritime Transport", "sector": "Logistics", "city": "Miami", "state": "FL", "country": "USA", "domain": "silverlineshipping.com", "phone_area": "305"},
    {"base": "Trident Automotive Components", "sector": "Manufacturing", "city": "Detroit", "state": "MI", "country": "USA", "domain": "tridentauto.com", "phone_area": "313"},
    {"base": "UltraTech Software Innovations", "sector": "Tech", "city": "Bengaluru", "state": "Karnataka", "country": "India", "domain": "ultratechsoft.in", "phone_area": "080"},
    {"base": "Bharat Heavy Electrical Systems", "sector": "Manufacturing", "city": "New Delhi", "state": "Delhi", "country": "India", "domain": "bharatelectricals.co.in", "phone_area": "011"},
    {"base": "Tata Precision Engineering", "sector": "Manufacturing", "city": "Pune", "state": "Maharashtra", "country": "India", "domain": "tataprecision.com", "phone_area": "020"},
    {"base": "Infospectrum Digital Labs", "sector": "Tech", "city": "Hyderabad", "state": "Telangana", "country": "India", "domain": "infospectrum.co", "phone_area": "040"},
    {"base": "Mahindra Agri Logistics", "sector": "Agriculture", "city": "Mumbai", "state": "Maharashtra", "country": "India", "domain": "mahindra-agri.in", "phone_area": "022"},
    {"base": "Chennai Petrochemical Refining", "sector": "Energy", "city": "Chennai", "state": "Tamil Nadu", "country": "India", "domain": "chennaipetrochem.com", "phone_area": "044"},
    {"base": "Vanguard Security Solutions", "sector": "Services", "city": "London", "state": "England", "country": "UK", "domain": "vanguardsecurity.co.uk", "phone_area": "020"},
    {"base": "Crown FinTech Global", "sector": "Finance", "city": "London", "state": "England", "country": "UK", "domain": "crownfintech.com", "phone_area": "020"},
    {"base": "Bavaria Precision Motors", "sector": "Automotive", "city": "Munich", "state": "Bavaria", "country": "Germany", "domain": "bavariamotors.de", "phone_area": "089"},
    {"base": "Nordic Clean Energy Labs", "sector": "Energy", "city": "Stockholm", "state": "Stockholm", "country": "Sweden", "domain": "nordiccleanenergy.se", "phone_area": "08"},
]

# Generate more businesses programmatically to reach 150+ canonical entities
PREFIXES = ["Global", "National", "United", "Prime", "Summit", "First", "Royal", "Pacific", "Atlantic", "Metro", "Direct", "Allied", "Alpha", "Omega", "Terra", "Nova", "Starlight", "Core", "Zenith", "Vortex", "Falcon", "Eagle", "Acro", "Synapse", "Hyper", "Spectra", "Optima", "BluePeak", "GreenLeaf", "IronClad"]
MIDDLES = ["Data", "Digital", "Bio", "Eco", "Micro", "Nano", "Smart", "Aero", "Chem", "Agri", "Supply", "Health", "Fin", "Capital", "Media", "Robotics", "Analytics", "Network", "Pharma", "Logistics", "Energy", "Infra", "Security", "Wireless", "Industrial"]
SUFFIX_TYPES = ["Technologies", "Solutions", "Enterprises", "Corporation", "Holdings", "Systems", "Consulting", "Ventures", "Laboratories", "Industries", "Group", "Services", "Innovations", "Dynamics", "Partners"]

CITIES_DB = [
    ("San Francisco", "CA", "USA", "415"),
    ("New York", "NY", "USA", "212"),
    ("Austin", "TX", "USA", "512"),
    ("Seattle", "WA", "USA", "206"),
    ("Boston", "MA", "USA", "617"),
    ("Chicago", "IL", "USA", "312"),
    ("Los Angeles", "CA", "USA", "310"),
    ("Denver", "CO", "USA", "303"),
    ("Dallas", "TX", "USA", "214"),
    ("Atlanta", "GA", "USA", "404"),
    ("Bengaluru", "Karnataka", "India", "080"),
    ("Mumbai", "Maharashtra", "India", "022"),
    ("Hyderabad", "Telangana", "India", "040"),
    ("Chennai", "Tamil Nadu", "India", "044"),
    ("Pune", "Maharashtra", "India", "020"),
    ("London", "England", "UK", "020"),
    ("Manchester", "England", "UK", "0161"),
    ("Berlin", "Berlin", "Germany", "030"),
    ("Toronto", "ON", "Canada", "416"),
    ("Sydney", "NSW", "Australia", "02")
]

STREET_NAMES = [
    "Market Street", "Broadway", "Tech Parkway", "Innovation Boulevard", "Industrial Avenue", 
    "Main Street", "Mission Street", "Fifth Avenue", "MG Road", "Brigade Road", 
    "Silicon Expressway", "High Street", "Victoria Road", "Cyber City", "Financial Center Way"
]

def build_canonical_entities(count=150):
    entities = []
    used_names = set()
    
    for t in CANONICAL_BUSINESS_TEMPLATES:
        name = t["base"]
        used_names.add(name)
        street_no = random.randint(10, 999)
        street = random.choice(STREET_NAMES)
        suite = f"Suite {random.randint(100, 900)}" if random.random() > 0.4 else ""
        addr = f"{street_no} {street}{', ' + suite if suite else ''}"
        phone_core = f"{random.randint(200, 999)}-{random.randint(1000, 9999)}"
        phone = f"+1 ({t['phone_area']}) {phone_core}" if t["country"] == "USA" else f"+{91 if t['country']=='India' else 44} {t['phone_area']} {random.randint(1000000, 9999999)}"
        email = f"contact@{t['domain']}"
        website = f"https://www.{t['domain']}"
        entities.append({
            "canonical_name": name,
            "address": addr,
            "city": t["city"],
            "state": t["state"],
            "country": t["country"],
            "phone": phone,
            "email": email,
            "website": website,
            "domain": t["domain"]
        })

    while len(entities) < count:
        p = random.choice(PREFIXES)
        m = random.choice(MIDDLES)
        s = random.choice(SUFFIX_TYPES)
        name = f"{p} {m} {s}"
        if name in used_names:
            continue
        used_names.add(name)
        
        city_info = random.choice(CITIES_DB)
        domain = f"{p.lower()}{m.lower()}.com"
        street_no = random.randint(10, 999)
        street = random.choice(STREET_NAMES)
        suite = f"Suite {random.randint(100, 900)}" if random.random() > 0.5 else ""
        addr = f"{street_no} {street}{', ' + suite if suite else ''}"
        phone = f"+1 ({city_info[3]}) {random.randint(200, 999)}-{random.randint(1000, 9999)}" if city_info[2] == "USA" else f"+91 {city_info[3]} {random.randint(1000000, 9999999)}"
        email = f"info@{domain}"
        website = f"https://www.{domain}"
        
        entities.append({
            "canonical_name": name,
            "address": addr,
            "city": city_info[0],
            "state": city_info[1],
            "country": city_info[2],
            "phone": phone,
            "email": email,
            "website": website,
            "domain": domain
        })
    return entities

def perturb_name(name, source_idx):
    if source_idx == 1:
        # Source 1: Standard legal variations
        transformations = [
            lambda x: x + " Pvt. Ltd.",
            lambda x: x + " Private Limited",
            lambda x: x + " Inc.",
            lambda x: x + " Corporation",
            lambda x: x + " LLC",
            lambda x: x.replace("Technologies", "Tech").replace("Solutions", "Sol."),
            lambda x: x.upper(),
            lambda x: x
        ]
        return random.choice(transformations)(name)
    elif source_idx == 2:
        # Source 2: Abbreviations, missing periods, lowercases
        transformations = [
            lambda x: x.lower() + " pvt ltd",
            lambda x: x.replace("Technologies", "Technologies Ltd"),
            lambda x: x.replace("Solutions", "Solutions Co."),
            lambda x: " ".join([c + "." for c in x.split()[0]]) + " " + " ".join(x.split()[1:]), # A.B.C. style
            lambda x: x.replace("Group", "Grp").replace("International", "Intl"),
            lambda x: typo_injector(x),
            lambda x: x + " & Co."
        ]
        return random.choice(transformations)(name)
    else:
        # Source 3: Extra spaces, minor typos, no legal suffix
        transformations = [
            lambda x: x.replace(" ", "  "), # double spaces
            lambda x: x.title(),
            lambda x: typo_injector(x),
            lambda x: x.replace("Corporation", "Corp.").replace("Enterprises", "Ent."),
            lambda x: x + " (Global)",
            lambda x: x
        ]
        return random.choice(transformations)(name)

def typo_injector(text):
    if len(text) < 5 or random.random() > 0.5:
        return text
    idx = random.randint(1, len(text) - 2)
    t_type = random.choice(["swap", "drop", "repeat"])
    if t_type == "swap":
        return text[:idx] + text[idx+1] + text[idx] + text[idx+2:]
    elif t_type == "drop":
        return text[:idx] + text[idx+1:]
    else:
        return text[:idx] + text[idx] + text[idx:]

def perturb_address(addr, source_idx):
    if not addr or random.random() < 0.08:
        return "" # Missing value
    
    variations = addr
    # Standardize/Abbreviate
    if "Street" in variations:
        variations = variations.replace("Street", "St." if source_idx % 2 == 0 else "St")
    if "Road" in variations:
        variations = variations.replace("Road", "Rd." if source_idx % 2 == 0 else "Rd")
    if "Avenue" in variations:
        variations = variations.replace("Avenue", "Ave" if source_idx % 2 == 0 else "Ave.")
    if "Boulevard" in variations:
        variations = variations.replace("Boulevard", "Blvd.")
    if "Suite" in variations:
        variations = variations.replace("Suite", "#" if source_idx == 3 else "Ste.")
    
    if source_idx == 2:
        variations = variations.lower()
    if source_idx == 3 and random.random() > 0.5:
        variations = variations.replace(",", "")
    return variations

def perturb_phone(phone, source_idx):
    if not phone or random.random() < 0.1:
        return "" # Missing value
    
    # Strip everything down to raw digits
    digits = "".join([c for c in phone if c.isdigit()])
    if len(digits) < 10:
        return phone
    
    if source_idx == 1:
        # Format: (123) 456-7890 or +91-1234567890
        if len(digits) == 10:
            return f"({digits[0:3]}) {digits[3:6]}-{digits[6:10]}"
        elif len(digits) == 11 and digits.startswith("1"):
            return f"+1 ({digits[1:4]}) {digits[4:7]}-{digits[7:11]}"
        else:
            return f"+{digits[:2]} {digits[2:6]} {digits[6:]}"
    elif source_idx == 2:
        # Format: 123-456-7890 or 123.456.7890
        if len(digits) == 10:
            return f"{digits[0:3]}.{digits[3:6]}.{digits[6:10]}"
        elif len(digits) == 11:
            return f"{digits[1:4]}-{digits[4:7]}-{digits[7:11]}"
        else:
            return f"{digits}"
    else:
        # Raw digits or spaces: 123 456 7890 or +11234567890
        if random.random() > 0.5:
            return f"+{digits}"
        return f"{digits}"

def perturb_email(email, source_idx):
    if not email or random.random() < 0.12:
        return "" # Missing value
    
    user, domain = email.split("@")
    if source_idx == 1:
        return f"contact@{domain}".lower()
    elif source_idx == 2:
        return f"INFO@{domain.upper()}"
    else:
        prefix = random.choice(["support", "hello", "sales", "office"])
        return f"{prefix}@{domain}"

def perturb_website(website, domain, source_idx):
    if not website or random.random() < 0.1:
        return ""
    if source_idx == 1:
        return f"https://www.{domain}"
    elif source_idx == 2:
        return f"http://{domain}/"
    else:
        return f"www.{domain}"

def generate_dataset():
    os.makedirs("dataset/train", exist_ok=True)
    os.makedirs("dataset/test", exist_ok=True)
    
    all_entities = build_canonical_entities(count=160)
    train_entities = all_entities[:110] # 110 canonical entities for training
    test_entities = all_entities[110:]  # 50 canonical entities for testing
    
    def process_split(entities, split_name):
        s1_records, s2_records, s3_records = [], [], []
        entity_clusters = [] # (entity_id, source_record_id, source)
        
        for idx, ent in enumerate(entities, 1):
            ent_id = f"ENT{idx:04d}"
            
            # Decide presence in sources: 
            # Some appear in all 3, some in 2, some in 1, plus some singletons (noise/distractors)
            in_s1 = True if idx <= len(entities) * 0.9 else (random.random() > 0.4)
            in_s2 = True if idx <= len(entities) * 0.85 else (random.random() > 0.3)
            in_s3 = True if idx <= len(entities) * 0.8 else (random.random() > 0.3)
            
            # Ensure at least 2 sources for majority so matches exist
            if not in_s1 and not in_s2 and not in_s3:
                in_s1 = in_s2 = True
                
            if in_s1:
                r1_id = f"S1_{idx:04d}"
                s1_records.append({
                    "source_record_id": r1_id,
                    "business_name": perturb_name(ent["canonical_name"], 1),
                    "address": perturb_address(ent["address"], 1),
                    "city": ent["city"],
                    "state": ent["state"],
                    "country": ent["country"],
                    "phone": perturb_phone(ent["phone"], 1),
                    "email": perturb_email(ent["email"], 1),
                    "website": perturb_website(ent["website"], ent["domain"], 1)
                })
                entity_clusters.append({"entity_id": ent_id, "source_record_id": r1_id, "source": "Source1"})
                
            if in_s2:
                r2_id = f"S2_{idx:04d}"
                s2_records.append({
                    "source_record_id": r2_id,
                    "business_name": perturb_name(ent["canonical_name"], 2),
                    "address": perturb_address(ent["address"], 2),
                    "city": ent["city"].lower() if random.random() > 0.3 else ent["city"],
                    "state": ent["state"],
                    "country": ent["country"],
                    "phone": perturb_phone(ent["phone"], 2),
                    "email": perturb_email(ent["email"], 2),
                    "website": perturb_website(ent["website"], ent["domain"], 2)
                })
                entity_clusters.append({"entity_id": ent_id, "source_record_id": r2_id, "source": "Source2"})
                
            if in_s3:
                r3_id = f"S3_{idx:04d}"
                s3_records.append({
                    "source_record_id": r3_id,
                    "business_name": perturb_name(ent["canonical_name"], 3),
                    "address": perturb_address(ent["address"], 3),
                    "city": ent["city"],
                    "state": ent["state"],
                    "country": ent["country"],
                    "phone": perturb_phone(ent["phone"], 3),
                    "email": perturb_email(ent["email"], 3),
                    "website": perturb_website(ent["website"], ent["domain"], 3)
                })
                entity_clusters.append({"entity_id": ent_id, "source_record_id": r3_id, "source": "Source3"})
                
        df1 = pd.DataFrame(s1_records)
        df2 = pd.DataFrame(s2_records)
        df3 = pd.DataFrame(s3_records)
        
        # Save TSVs
        df1.to_csv(f"dataset/{split_name}/{split_name}_source1.tsv", sep="\t", index=False)
        df2.to_csv(f"dataset/{split_name}/{split_name}_source2.tsv", sep="\t", index=False)
        df3.to_csv(f"dataset/{split_name}/{split_name}_source3.tsv", sep="\t", index=False)
        
        # Create Ground Truth Pairwise Matches
        cluster_map = {row["source_record_id"]: row["entity_id"] for row in entity_clusters}
        all_record_ids = list(cluster_map.keys())
        
        # Generate pairwise combinations (all positive pairs + hard/random negative samples)
        ground_truth_pairs = []
        
        # 1. All positive pairs
        for i in range(len(all_record_ids)):
            for j in range(i + 1, len(all_record_ids)):
                r1, r2 = all_record_ids[i], all_record_ids[j]
                # Cross-source pairs primarily
                if r1[:2] != r2[:2]:
                    if cluster_map[r1] == cluster_map[r2]:
                        ground_truth_pairs.append({
                            "record_id_1": r1,
                            "record_id_2": r2,
                            "entity_id_1": cluster_map[r1],
                            "entity_id_2": cluster_map[r2],
                            "is_match": 1
                        })
        
        # 2. Hard & random negative pairs (sample negative pairs to balance data)
        num_positives = len(ground_truth_pairs)
        num_negatives = int(num_positives * 2.5) # realistic ratio for training
        
        sampled_negatives = 0
        attempts = 0
        while sampled_negatives < num_negatives and attempts < 20000:
            attempts += 1
            r1 = random.choice(all_record_ids)
            r2 = random.choice(all_record_ids)
            if r1 != r2 and r1[:2] != r2[:2] and cluster_map[r1] != cluster_map[r2]:
                ground_truth_pairs.append({
                    "record_id_1": r1,
                    "record_id_2": r2,
                    "entity_id_1": cluster_map[r1],
                    "entity_id_2": cluster_map[r2],
                    "is_match": 0
                })
                sampled_negatives += 1
                
        gt_df = pd.DataFrame(ground_truth_pairs)
        gt_df.to_csv(f"dataset/{split_name}/{split_name}_ground_truth.tsv", sep="\t", index=False)
        
        clusters_df = pd.DataFrame(entity_clusters)
        clusters_df.to_csv(f"dataset/{split_name}/{split_name}_entity_clusters.tsv", sep="\t", index=False)
        
        print(f"[{split_name.upper()}] Generated: Source1={len(df1)}, Source2={len(df2)}, Source3={len(df3)}, Total Records={len(df1)+len(df2)+len(df3)}, GroundTruthPairs={len(gt_df)} (Positives={num_positives}, Negatives={sampled_negatives})")

    process_split(train_entities, "train")
    process_split(test_entities, "test")
    print("Synthetic dataset generation completed successfully!")

if __name__ == "__main__":
    generate_dataset()
