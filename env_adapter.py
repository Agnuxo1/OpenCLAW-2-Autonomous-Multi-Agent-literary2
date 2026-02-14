"""
OpenCLAW Literary Agent 2 (GLM5) - Environment Variable Adapter
================================================================
PROBLEM: Agent has 30 secrets in numbered format (GEMINI_API_KEY_1, GROQ_API_KEY_1...)
         but code looks for different variable names.
         Result: "No API keys found in environment" despite 30 configured secrets.

SOLUTION: This adapter script runs BEFORE the main agent and consolidates
          all numbered env vars into CSV format that the agent code expects.

USAGE: 
  In your workflow, add this step BEFORE the main agent:
    - name: Consolidate API Keys
      run: python env_adapter.py >> $GITHUB_ENV

  Or import it in your main.py:
    import env_adapter
    env_adapter.consolidate()
"""

import os
import sys
from typing import Dict, List


# Map of expected CSV variable -> numbered prefix patterns
KEY_MAPPINGS = {
    'GROQ_API_KEYS': ['GROQ_API_KEY_', 'GROQ_KEY_'],
    'NVIDIA_API_KEYS': ['NVIDIA_API_KEY_', 'NVIDIA_KEY_'],
    'GEMINI_API_KEYS': ['GEMINI_API_KEY_', 'GOOGLE_API_KEY_'],
    'OPENROUTER_API_KEYS': ['OPENROUTER_API_KEY_', 'OPENROUTER_KEY_'],
    'MISTRAL_API_KEYS': ['MISTRAL_API_KEY_', 'MISTRAL_KEY_'],
    'DEEPSEEK_API_KEYS': ['DEEPSEEK_API_KEY_', 'DEEPSEEK_KEY_'],
    'ZHIPUAI_API_KEYS': ['ZHIPUAI_API_KEY_', 'GLM_API_KEY_', 'ZHIPU_KEY_'],
    'HF_TOKEN': ['HF_TOKEN_', 'HUGGINGFACE_TOKEN_'],
}


def collect_numbered_keys(prefix: str, max_index: int = 20) -> List[str]:
    """Collect all numbered keys with a given prefix."""
    keys = []
    for i in range(1, max_index + 1):
        val = os.environ.get(f"{prefix}{i}", '').strip()
        if val and len(val) > 5:
            keys.append(val)
    return keys


def consolidate(verbose: bool = True) -> Dict[str, str]:
    """
    Consolidate all numbered env vars into CSV format.
    Also sets them in the current process environment.
    
    Returns dict of {CSV_VAR: "key1,key2,key3"} for all found keys.
    """
    consolidated = {}
    total_keys = 0
    
    for csv_var, prefixes in KEY_MAPPINGS.items():
        all_keys = set()
        
        # Check if CSV var already exists
        existing = os.environ.get(csv_var, '').strip()
        if existing:
            for k in existing.split(','):
                k = k.strip()
                if k and len(k) > 5:
                    all_keys.add(k)
        
        # Also check single-key format (e.g., GROQ_API_KEY without number)
        for prefix in prefixes:
            single_var = prefix.rstrip('_')
            single_val = os.environ.get(single_var, '').strip()
            if single_val and len(single_val) > 5:
                all_keys.add(single_val)
            
            # Collect numbered keys
            numbered = collect_numbered_keys(prefix)
            all_keys.update(numbered)
        
        if all_keys:
            csv_value = ','.join(sorted(all_keys))
            os.environ[csv_var] = csv_value
            consolidated[csv_var] = csv_value
            total_keys += len(all_keys)
            
            if verbose:
                print(f"[env_adapter] {csv_var}: {len(all_keys)} key(s) consolidated", 
                      file=sys.stderr)
    
    if verbose:
        print(f"[env_adapter] ✅ Total: {total_keys} keys across {len(consolidated)} providers",
              file=sys.stderr)
    
    return consolidated


def write_github_env(consolidated: Dict[str, str]):
    """Write consolidated vars to $GITHUB_ENV for subsequent steps."""
    github_env = os.environ.get('GITHUB_ENV')
    if github_env:
        with open(github_env, 'a') as f:
            for var, val in consolidated.items():
                f.write(f"{var}={val}\n")
        print(f"[env_adapter] Written {len(consolidated)} vars to GITHUB_ENV", 
              file=sys.stderr)
    else:
        # Not in GitHub Actions - just print for shell eval
        for var, val in consolidated.items():
            print(f"export {var}=\"{val}\"")


if __name__ == '__main__':
    result = consolidate()
    
    if not result:
        print("[env_adapter] ⚠️ No API keys found in any format!", file=sys.stderr)
        print("[env_adapter] Expected: GROQ_API_KEY_1, NVIDIA_API_KEY_1, etc.", file=sys.stderr)
        sys.exit(0)  # Don't fail the workflow
    
    write_github_env(result)
