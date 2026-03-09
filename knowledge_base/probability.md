# Probability - Core Formulas & Concepts

## Basic Probability
- P(A) = favorable outcomes / total outcomes
- 0 ≤ P(A) ≤ 1
- P(A) + P(A') = 1  [complement rule]
- P(A∪B) = P(A) + P(B) - P(A∩B)  [addition rule]
- P(A∩B) = P(A)·P(B|A) = P(B)·P(A|B)  [multiplication rule]

## Independent Events
- P(A∩B) = P(A)·P(B) if A and B are independent
- Events A and B independent iff P(A|B) = P(A)

## Conditional Probability
- P(A|B) = P(A∩B) / P(B), provided P(B) > 0
- Bayes' Theorem: P(A|B) = P(B|A)·P(A) / P(B)
- Total Probability: P(B) = Σ P(B|Aᵢ)·P(Aᵢ)

## Combinatorics
- Permutation: P(n,r) = n!/(n-r)!  (order matters)
- Combination: C(n,r) = n!/(r!(n-r)!)  (order doesn't matter)
- With repetition (permutation): nʳ
- Circular permutation: (n-1)!
- Multinomial coefficient: n!/(n₁!n₂!...nₖ!)

## Discrete Distributions
### Binomial Distribution
- X ~ B(n, p)
- P(X=k) = C(n,k) pᵏ (1-p)ⁿ⁻ᵏ
- Mean: μ = np
- Variance: σ² = np(1-p)

### Poisson Distribution
- X ~ Poisson(λ)
- P(X=k) = e⁻λ λᵏ / k!
- Mean = Variance = λ

### Geometric Distribution
- P(X=k) = (1-p)ᵏ⁻¹ p
- Mean: 1/p

## Continuous Distributions
### Normal Distribution
- X ~ N(μ, σ²)
- PDF: f(x) = (1/σ√(2π)) e^(-(x-μ)²/2σ²)
- Standard normal: Z = (X-μ)/σ
- P(μ-σ < X < μ+σ) ≈ 0.6827
- P(μ-2σ < X < μ+2σ) ≈ 0.9545
- P(μ-3σ < X < μ+3σ) ≈ 0.9973

## Expected Value & Variance
- E(X) = Σ xᵢ·P(xᵢ) for discrete
- E(aX+b) = aE(X) + b
- Var(X) = E(X²) - [E(X)]²
- Var(aX+b) = a²·Var(X)
- E(X+Y) = E(X) + E(Y)
- If X,Y independent: Var(X+Y) = Var(X) + Var(Y)

## JEE-Style Problem Templates
### Balls from Urn Problems
- Identify: n total, r favorable
- Without replacement: use combinations
- With replacement: use binomial distribution

### Card Problems
- Total: 52 cards, 4 suits, 13 per suit
- Face cards: J, Q, K (12 total)
- Aces: 4 total

### Dice Problems
- Single die: sample space = {1,2,3,4,5,6}
- Two dice: sample space has 36 outcomes

## Common Mistakes in Probability
- Confusing P(A|B) with P(B|A)
- Forgetting to subtract intersection in addition rule
- Treating non-independent events as independent
- Confusing permutation with combination
