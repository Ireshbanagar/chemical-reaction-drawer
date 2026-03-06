# AI Features Quick Start Guide

## Generate Molecules from Names in 3 Steps

### Step 1: Open AI Assistant
Press **Ctrl+G** or go to **AI Assistant > Generate from Name...**

### Step 2: Enter Molecule Name
Type any common molecule name:
- aspirin
- caffeine
- benzene
- glucose
- ethanol
- water
- methane

### Step 3: Add to Canvas
Click **Generate**, then **Add to Canvas**

---

## Features

### ✓ Works Offline
Built-in database of 17 common molecules works without internet or AWS.

### ✓ AI-Powered (Optional)
Connect to AWS Bedrock for unlimited molecule generation using Claude 3.5 Sonnet.

### ✓ Fast
Results in seconds. Cached molecules load instantly.

---

## Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Open AI Assistant | Ctrl+G |
| Generate | Enter (in dialog) |

---

## Menu Options

### AI Assistant Menu:
- **Generate from Name...** - Main feature
- **AI Status** - Check connection status
- **Clear AI Cache** - Clear cached molecules

---

## Status Indicators

### ✓ AI Available
Green indicator: Connected to AWS Bedrock
- Unlimited molecule generation
- AI-powered recognition
- Latest chemical data

### ⚠ Fallback Mode
Orange indicator: Using built-in database
- 17 common molecules available
- No AWS credentials needed
- Works offline

---

## Supported Molecules (Fallback Mode)

1. water
2. methane
3. ethane
4. propane
5. butane
6. methanol
7. ethanol
8. acetone
9. benzene
10. toluene
11. aspirin
12. caffeine
13. glucose
14. acetic acid
15. ammonia
16. carbon dioxide
17. formaldehyde

---

## Enable Full AI Features

### Requirements:
- Python package: boto3
- AWS account with Bedrock access
- AWS credentials configured

### Setup:
```bash
# 1. Install boto3
pip install boto3

# 2. Configure AWS credentials
aws configure
# Enter your AWS Access Key ID
# Enter your AWS Secret Access Key
# Default region: us-east-1
# Default output format: json

# 3. Restart Chemical Reaction Drawer
```

---

## Troubleshooting

### "AI Unavailable" message?
- **Solution 1:** Use fallback mode (works for common molecules)
- **Solution 2:** Install boto3 and configure AWS credentials

### Molecule not recognized?
- Try different spelling or name
- Check if it's in the fallback database list
- Enable full AI features for better recognition

### Generated structure looks wrong?
- SMILES parser uses simple layout algorithm
- Manually adjust atom positions after generation
- Report issues for future improvements

---

## Tips

1. **Use Cache:** Keep "Use cache" checked for faster repeated queries
2. **Common Names:** Use common names (aspirin) not IUPAC names
3. **Edit After:** Generated structures can be edited like any other molecule
4. **Save Often:** Use Ctrl+S to save your work

---

## Examples

### Example 1: Generate Aspirin
1. Press Ctrl+G
2. Type "aspirin"
3. Click Generate
4. See: C9H8O4, 13 atoms, 13 bonds
5. Click Add to Canvas

### Example 2: Generate Caffeine
1. Press Ctrl+G
2. Type "caffeine"
3. Click Generate
4. See: C8H10N4O2, 14 atoms, 15 bonds
5. Click Add to Canvas

### Example 3: Generate Benzene
1. Press Ctrl+G
2. Type "benzene"
3. Click Generate
4. See: C6H6, 6 atoms, 6 bonds
5. Click Add to Canvas

---

## What's Next?

After generating molecules, you can:
- Edit structure (add/remove atoms/bonds)
- Validate chemistry (Tools > Validate Molecules)
- View properties (Tools > Molecular Properties)
- View in 3D (View > 3D View or F3)
- Export (File > Export)
- Save project (Ctrl+S)

---

## Support

For issues or questions:
1. Check AI Status (AI Assistant > AI Status)
2. Review error messages in status bar
3. Check console output for detailed errors
4. Refer to AI_INTEGRATION_SUMMARY.md for technical details

---

**Enjoy AI-powered molecule generation!** 🧪✨
