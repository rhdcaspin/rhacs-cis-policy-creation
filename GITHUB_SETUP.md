# GitHub Setup Guide

This guide will help you push your RHACS CIS Policy Creator to GitHub.

## Step 1: Create GitHub Repository

1. **Go to GitHub.com** and log into your account
2. **Click the "+" icon** in the top right corner
3. **Select "New repository"**
4. **Configure your repository:**
   - **Repository name:** `rhacs-cis-policy-creation` (or your preferred name)
   - **Description:** `Automated RHACS CIS benchmark policy creator with runtime threat detection`
   - **Visibility:** Choose Public or Private
   - **Do NOT initialize** with README, .gitignore, or license (we already have these)
5. **Click "Create repository"**

## Step 2: Push to GitHub

After creating the repository, GitHub will show you commands. Use these commands in your terminal:

```bash
# Add the GitHub repository as remote origin
git remote add origin https://github.com/rhdcaspin/rhacs-cis-policy-creation.git

# Push your code to GitHub
git branch -M main
git push -u origin main
```

**Replace `YOUR_USERNAME`** with your actual GitHub username.

## Step 3: Verify Upload

1. **Refresh your GitHub repository page**
2. **Verify all files are present:**
   - ✅ README.md
   - ✅ rhacs_cis_policy_creator.py
   - ✅ cis_policies.json
   - ✅ requirements.txt
   - ✅ config.json.template
   - ✅ .gitignore
   - ❌ config.json (should NOT be present - contains sensitive data)

## Step 4: Repository Description

Add these **topics/tags** to your repository for better discoverability:
- `rhacs`
- `red-hat`
- `security`
- `cis-benchmark`
- `kubernetes`
- `docker`
- `policy-automation`
- `threat-detection`
- `devsecops`

## Step 5: Security Check

**IMPORTANT:** Verify that `config.json` is NOT uploaded to GitHub. This file contains:
- RHACS instance URL
- API token (sensitive!)

If you accidentally uploaded it:
1. Remove it from the repository
2. Regenerate your RHACS API token
3. Update your local `config.json`

## Optional: Add GitHub Actions

Consider adding CI/CD workflows for:
- Policy validation
- Automated testing
- Documentation updates

## Project Structure on GitHub

```
rhacs-cis-policy-creation/
├── README.md                     # Project documentation
├── rhacs_cis_policy_creator.py   # Main script
├── cis_policies.json            # Policy definitions
├── requirements.txt             # Python dependencies
├── config.json.template         # Configuration template
├── .gitignore                   # Git exclusions
├── corrected_policies.json      # Debugging reference
└── policy_fixes.json           # Fix documentation
```

## Next Steps

1. **Star the repository** if you find it useful
2. **Add collaborators** if this is a team project
3. **Create issues** for tracking improvements
4. **Consider creating releases** for stable versions
5. **Add a license** if you want to make it open source

---

**🎉 Congratulations!** Your RHACS CIS Policy Creator is now on GitHub and ready to share with the community! 
