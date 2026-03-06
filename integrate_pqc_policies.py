#!/usr/bin/env python3
"""
Integrate PQC Policies into CIS Policies
Merges Post-Quantum Cryptography policies with existing CIS benchmark policies
"""

import json
import logging
import os
from typing import Dict, Any

def load_json_file(filename: str) -> Dict[str, Any]:
    """Load JSON file with error handling"""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logging.error(f"File '{filename}' not found.")
        return {}
    except json.JSONDecodeError as e:
        logging.error(f"Error parsing JSON file '{filename}': {e}")
        return {}

def save_json_file(filename: str, data: Dict[str, Any]) -> bool:
    """Save JSON file with error handling"""
    try:
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        logging.info(f"✅ Successfully saved '{filename}'")
        return True
    except Exception as e:
        logging.error(f"❌ Error saving '{filename}': {e}")
        return False

def integrate_pqc_policies():
    """Integrate PQC policies into CIS policies"""
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    logging.info("🔐 Starting PQC policy integration...")
    
    # Load existing CIS policies
    cis_data = load_json_file('cis_policies.json')
    if not cis_data:
        logging.error("❌ Could not load CIS policies. Aborting integration.")
        return False
    
    # Load PQC policies
    pqc_data = load_json_file('working_pqc_policies.json')
    if not pqc_data:
        logging.error("❌ Could not load PQC policies. Aborting integration.")
        return False
    
    pqc_policies = pqc_data.get('pqc_policies', [])
    if not pqc_policies:
        logging.error("❌ No PQC policies found in pqc_policy.json")
        return False
    
    # Create backup
    backup_filename = 'cis_policies_backup.json'
    if save_json_file(backup_filename, cis_data):
        logging.info(f"📁 Created backup: {backup_filename}")
    else:
        logging.warning("⚠️  Could not create backup file")
    
    # Add PQC policies to CIS policies
    if 'pqc_policies' not in cis_data:
        cis_data['pqc_policies'] = []
    
    # Check for duplicates
    existing_names = {policy['name'] for policy in cis_data.get('pqc_policies', [])}
    new_policies = []
    duplicate_count = 0
    
    for policy in pqc_policies:
        if policy['name'] not in existing_names:
            new_policies.append(policy)
        else:
            duplicate_count += 1
            logging.warning(f"⚠️  Skipping duplicate policy: {policy['name']}")
    
    # Add new policies
    cis_data['pqc_policies'].extend(new_policies)
    
    # Save updated file
    if save_json_file('cis_policies.json', cis_data):
        logging.info(f"✅ Successfully integrated {len(new_policies)} PQC policies")
        logging.info(f"   📋 Total PQC policies: {len(cis_data['pqc_policies'])}")
        if duplicate_count > 0:
            logging.info(f"   ⏭️  Skipped duplicates: {duplicate_count}")
        return True
    else:
        logging.error("❌ Failed to save integrated policies")
        return False

def main():
    """Main function"""
    print("🔐 Post-Quantum Cryptography Policy Integration")
    print("=" * 50)
    
    # Check if files exist
    required_files = ['cis_policies.json', 'working_pqc_policies.json']
    missing_files = [f for f in required_files if not os.path.exists(f)]
    
    if missing_files:
        print(f"❌ Missing required files: {', '.join(missing_files)}")
        print("\nTo create PQC policies, run:")
        print("   python3 pqc_policy_creator.py")
        return
    
    # Prompt user
    response = input("\nThis will add PQC policies to your cis_policies.json file.\nContinue? (y/N): ").strip().lower()
    
    if response in ['y', 'yes']:
        if integrate_pqc_policies():
            print("\n🎉 PQC policies successfully integrated!")
            print("\nNext steps:")
            print("1. Review the updated cis_policies.json file")
            print("2. Run: python3 rhacs_cis_policy_creator.py")
            print("   (This will create both CIS and PQC policies in RHACS)")
        else:
            print("\n❌ Integration failed. Check the logs above.")
    else:
        print("\n⏹️  Integration cancelled.")
        print("\nTo create PQC policies separately, run:")
        print("   python3 pqc_policy_creator.py")

if __name__ == "__main__":
    main()