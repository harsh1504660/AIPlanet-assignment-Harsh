# Calculus - Core Formulas (JEE Level)

## Limits

### Standard Limits
- lim(x→0) sin(x)/x = 1
- lim(x→0) tan(x)/x = 1
- lim(x→0) (1-cos x)/x² = 1/2
- lim(x→∞) (1 + 1/x)ˣ = e
- lim(x→0) (eˣ - 1)/x = 1
- lim(x→0) (aˣ - 1)/x = ln(a)
- lim(x→0) ln(1+x)/x = 1
- lim(x→a) (xⁿ - aⁿ)/(x-a) = naⁿ⁻¹

### L'Hôpital's Rule
- If lim gives 0/0 or ∞/∞ form: lim f(x)/g(x) = lim f'(x)/g'(x)
- Apply only when indeterminate form exists

### Continuity
- f is continuous at x=a if: lim(x→a) f(x) = f(a)
- Left limit = Right limit = Function value

## Derivatives

### Basic Rules
- d/dx(xⁿ) = nxⁿ⁻¹
- d/dx(eˣ) = eˣ
- d/dx(aˣ) = aˣ ln(a)
- d/dx(ln x) = 1/x
- d/dx(sin x) = cos x
- d/dx(cos x) = -sin x
- d/dx(tan x) = sec²x
- d/dx(cot x) = -csc²x
- d/dx(sec x) = sec x·tan x
- d/dx(csc x) = -csc x·cot x

### Inverse Trig Derivatives
- d/dx(sin⁻¹x) = 1/√(1-x²)
- d/dx(cos⁻¹x) = -1/√(1-x²)
- d/dx(tan⁻¹x) = 1/(1+x²)

### Differentiation Rules
- Sum: (f+g)' = f' + g'
- Product: (fg)' = f'g + fg'
- Quotient: (f/g)' = (f'g - fg')/g²
- Chain: d/dx[f(g(x))] = f'(g(x))·g'(x)

### Implicit Differentiation
- Differentiate both sides w.r.t. x
- Treat y as function of x
- Apply chain rule to y terms

## Applications of Derivatives

### Increasing/Decreasing Functions
- f'(x) > 0 → f increasing
- f'(x) < 0 → f decreasing
- f'(x) = 0 → critical point

### Maxima & Minima
- First derivative test: sign change of f'
- Second derivative test:
  - f''(x) < 0 → local max
  - f''(x) > 0 → local min
  - f''(x) = 0 → inconclusive (check higher derivatives)

### Tangent & Normal Lines
- Slope of tangent at (a,b): m = f'(a)
- Tangent: y - b = m(x - a)
- Normal slope: -1/m
- Normal: y - b = (-1/m)(x - a)

### Rolle's Theorem
- If f continuous on [a,b], differentiable on (a,b), f(a)=f(b)
- Then ∃ c ∈ (a,b) such that f'(c) = 0

### Mean Value Theorem
- If f continuous on [a,b], differentiable on (a,b)
- Then ∃ c ∈ (a,b) such that f'(c) = [f(b)-f(a)]/(b-a)

## Optimization Problems Template
1. Define the quantity to optimize
2. Express it as a function of one variable
3. Find critical points (set derivative = 0)
4. Apply second derivative test
5. Check endpoints if domain is closed interval
6. State answer with units

## Common Mistakes in Calculus
- Forgetting chain rule in composite functions
- Not checking domain when computing limits
- Confusing local and global extrema
- Forgetting ± in √ when differentiating implicitly
- Using L'Hôpital's rule when limit is not indeterminate
