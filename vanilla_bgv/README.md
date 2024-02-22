# Vanilla BGV

This directory contains a BGV implementation this is not the "original" BGV
paper, but a variant based on

    Revisiting Homomorphic Encryption Schemes for Finite Fields
    Andrey Kim, Yuriy Polyakov, and Vincent Zucca
    October 31, 2022
    https://eprint.iacr.org/2021/204

In particular, this implementation is "vanilla" in that it does **not**
incorporate a number of optimizations:

- CRT/RNS decompositions (uses gmp for multiprecision ints instead)
- Hybrid key switching
