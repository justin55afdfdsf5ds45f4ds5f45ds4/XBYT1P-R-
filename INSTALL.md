# Installation Guide

## Quick Install

```bash
# Clone the repository
git clone https://github.com/justin55afdfdsf5ds45f4ds5f45ds4/XBYT1P-R-.git
cd XBYT1P-R-

# Run the installer
python install.py
```

This will:
1. Install XBYT1P globally as `xbyt1p` command
2. Create config directory at `~/.xbyt1p/`
3. Copy `.env.example` to `~/.xbyt1p/.env`

## Configure API Keys

Edit `~/.xbyt1p/.env` and add your API keys:

```bash
# Windows
notepad %USERPROFILE%\.xbyt1p\.env

# Linux/Mac
nano ~/.xbyt1p/.env
```

Required keys:
- `REPLICATE_API_TOKEN` - Get at https://replicate.com/account/api-tokens
- `E2B_API_KEY` - Get at https://e2b.dev/docs

**CRITICAL:**
- `ULTRACONTEXT_API_KEY` - Get at https://ultracontext.ai (REQUIRED for memory and RLM scaling)

## Usage

Once installed, you can use `xbyt1p` from any directory:

```bash
# Fix error from log file
xbyt1p error.log

# Fix error from clipboard
xbyt1p "Traceback (most recent call last)..."

# Specify codebase path
xbyt1p error.log /path/to/project
```

## Example

```bash
$ xbyt1p test_project/error.log test_project

[*] Analyzing error...
[!] Error: IndexError in test_project/utils.py:6
[*] Mapping file relations...
[+] Related files: 3
[*] Checking memory for similar fixes...
[*] Generating fix with cheap model...
[*] Testing fix in sandbox...
[+] Fix works! Storing in memory...

============================================================
SUCCESS - FIX GENERATED
============================================================

File: test_project/utils.py
Line: 6

Diff:
- return data[999]
+ if len(data) > 999:
+     return data[999]
+ return None

Cost: $0.0002
Model: deepseek-ai/deepseek-v3
```

## Troubleshooting

### Command not found

If `xbyt1p` command is not found after installation:

1. Make sure Python's Scripts directory is in your PATH
2. Try running directly: `python -m codehealer <args>`
3. Reinstall: `python -m pip install -e . --force-reinstall`

### API Key Errors

If you get "API key not found" errors:

1. Check that `~/.xbyt1p/.env` exists
2. Verify the keys are set correctly (no quotes, no spaces)
3. Try setting environment variables directly:
   ```bash
   # Windows
   set REPLICATE_API_TOKEN=your_token
   set E2B_API_KEY=your_key
   
   # Linux/Mac
   export REPLICATE_API_TOKEN=your_token
   export E2B_API_KEY=your_key
   ```

### Insufficient Credit

If you see "Insufficient credit" error from Replicate:

1. Go to https://replicate.com/account/billing
2. Add credit to your account
3. Wait a few minutes and try again

## Uninstall

```bash
pip uninstall xbyt1p
rm -rf ~/.xbyt1p  # Linux/Mac
rmdir /s %USERPROFILE%\.xbyt1p  # Windows
```
