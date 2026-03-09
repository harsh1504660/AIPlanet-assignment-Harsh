# Common Mistakes & Pitfalls in JEE Math

## Algebra Pitfalls

### Division by Variable Errors
- WRONG: Divide both sides by x when solving equations (x could be 0)
- RIGHT: Factor out x and consider x=0 as a case
- Example: x² = x → WRONG: x = 1 → RIGHT: x(x-1)=0, so x=0 or x=1

### Square Root Errors
- √(x²) = |x|, NOT just x
- √(a)·√(b) = √(ab) only when a,b ≥ 0
- (√a)² = a, but √(a²) = |a|

### Logarithm Domain Errors
- log(x) is defined only for x > 0
- When solving log equations, always check solutions in original equation
- log(a-b) is NOT the same as log(a) - log(b)

### Inequality Mistakes
- Squaring: a > b does NOT imply a² > b² (sign matters!)
- Reciprocal: if a > b > 0, then 1/a < 1/b (flips)
- Always check if multiplied/divided by negative (flip inequality)

## Probability Pitfalls

### Conditional Probability Confusion
- P(A|B) ≠ P(B|A) - these are very different!
- Prosecutor's fallacy: P(evidence|innocent) ≠ P(innocent|evidence)

### Independence vs Mutually Exclusive
- Mutually exclusive: P(A∩B) = 0 (cannot both happen)
- Independent: P(A∩B) = P(A)·P(B)
- Mutually exclusive events (with P>0) are NOT independent!

### Overcounting in Combinatorics
- Be careful about distinguishable vs indistinguishable objects
- Circular arrangements: fix one object, arrange rest as (n-1)!
- Identical objects in permutations: divide by number of repetitions

## Calculus Pitfalls

### Chain Rule Forgetting
- d/dx[sin(x²)] = cos(x²)·2x, NOT just cos(x²)
- d/dx[ln(f(x))] = f'(x)/f(x)

### Limit Errors
- Cannot substitute x=0 if denominator becomes 0
- L'Hôpital's applies ONLY to 0/0 or ∞/∞, not 0/∞
- sin(1/x) has no limit as x→0 (oscillates)

### Integration (Definite)
- After finding antiderivative F(x): evaluate F(b) - F(a)
- Domain issues: integrand must be defined on [a,b]
- Check if function is continuous on interval

### Critical Points vs Extrema
- Not all critical points are extrema (saddle points)
- Global max/min may be at endpoints, not critical points
- Always check boundary conditions for optimization

## Linear Algebra Pitfalls

### Matrix Commutativity Error
- AB ≠ BA in general
- (A+B)² = A² + AB + BA + B² ≠ A² + 2AB + B²

### Inverse Matrix Errors
- A⁻¹ exists only if det(A) ≠ 0
- (AB)⁻¹ = B⁻¹A⁻¹ (reverse order!)
- A⁻¹A = AA⁻¹ = I (both must hold)

### Determinant Sign Errors
- Row swap changes sign: det(B) = -det(A) if B has two rows swapped
- Cofactor expansion: alternating +/- signs (checkerboard pattern)
- Cofactor C₁₁ = +M₁₁, C₁₂ = -M₁₂, etc.

## Unit/Domain Constraint Checks
- Probability answers: must be in [0,1]
- Number of objects: must be non-negative integers
- Geometric lengths: must be positive
- Angles in degrees vs radians: be consistent
- Logarithm arguments: must be positive
- Square roots: argument must be non-negative for real answers
