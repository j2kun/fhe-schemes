# FHE schemes

This repository contains learning-oriented implementations of major FHE
schemes and their optimizations. The focus is on correctness and legibility.

## Requirements

System requirements

```bash
sudo apt install -y libgmp3-dev libmpfr-dev libmpc-dev

# or on mac with homebrew
brew install gmp mpfr libmpc
```

Python requirements

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running tests

After installing requirements,

```bash
python -m pytest
```
