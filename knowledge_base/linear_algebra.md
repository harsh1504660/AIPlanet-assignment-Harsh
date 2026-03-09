# Linear Algebra - Core Concepts (JEE Level)

## Matrices

### Types
- Square matrix: n×n
- Identity matrix (I): diagonal elements 1, rest 0
- Zero matrix (O): all elements 0
- Diagonal matrix: non-diagonal elements = 0
- Symmetric: A = Aᵀ
- Skew-symmetric: A = -Aᵀ (diagonal elements = 0)
- Orthogonal: AAᵀ = AᵀA = I

### Matrix Operations
- Addition: (A+B)ᵢⱼ = aᵢⱼ + bᵢⱼ (same dimensions)
- Scalar multiplication: (cA)ᵢⱼ = c·aᵢⱼ
- Matrix multiplication: (AB)ᵢₖ = Σⱼ aᵢⱼ·bⱼₖ
  - Not commutative: AB ≠ BA in general
  - Associative: (AB)C = A(BC)
  - Distributive: A(B+C) = AB + AC

### Transpose Properties
- (Aᵀ)ᵀ = A
- (A+B)ᵀ = Aᵀ + Bᵀ
- (AB)ᵀ = BᵀAᵀ
- (cA)ᵀ = cAᵀ

## Determinants

### 2×2 Matrix
- det(A) = |a b; c d| = ad - bc

### 3×3 Matrix (Cofactor Expansion)
- det(A) = a₁₁(a₂₂a₃₃-a₂₃a₃₂) - a₁₂(a₂₁a₃₃-a₂₃a₃₁) + a₁₃(a₂₁a₃₂-a₂₂a₃₁)

### Properties
- det(AB) = det(A)·det(B)
- det(Aᵀ) = det(A)
- det(cA) = cⁿ·det(A) for n×n matrix
- det(A⁻¹) = 1/det(A)
- Row/column swap: changes sign of det
- If two rows/columns are equal: det = 0
- Row/column of zeros: det = 0

## Inverse Matrix
- A⁻¹ exists iff det(A) ≠ 0 (A is invertible/non-singular)
- A·A⁻¹ = A⁻¹·A = I
- For 2×2: A⁻¹ = (1/det(A)) × [d -b; -c a]
- (AB)⁻¹ = B⁻¹A⁻¹
- (Aᵀ)⁻¹ = (A⁻¹)ᵀ

## Systems of Linear Equations
- Matrix form: AX = B
- Unique solution: det(A) ≠ 0 → X = A⁻¹B
- No solution or infinite solutions: det(A) = 0

### Cramer's Rule (for unique solution)
- xᵢ = det(Aᵢ)/det(A) where Aᵢ is A with i-th column replaced by B

## Rank of a Matrix
- Rank = number of non-zero rows in row echelon form
- For n×n matrix: rank = n iff invertible
- rank(A) = rank(Aᵀ)
- rank(AB) ≤ min(rank(A), rank(B))

## Vectors
- Magnitude: |v| = √(v₁² + v₂² + v₃²)
- Dot product: a·b = |a||b|cos(θ) = a₁b₁ + a₂b₂ + a₃b₃
- Cross product: a×b = (a₂b₃-a₃b₂, a₃b₁-a₁b₃, a₁b₂-a₂b₁)
- |a×b| = |a||b|sin(θ)
- Unit vector: â = a/|a|
- Perpendicular vectors: a·b = 0
- Parallel vectors: a×b = 0

## Eigenvalues & Eigenvectors (Basic)
- Av = λv (v ≠ 0)
- Characteristic equation: det(A - λI) = 0
- Sum of eigenvalues = trace(A) = Σaᵢᵢ
- Product of eigenvalues = det(A)

## Common Mistakes in Linear Algebra
- AB ≠ BA (matrix multiplication not commutative)
- (A+B)² ≠ A² + 2AB + B² (since AB ≠ BA)
- Not checking det ≠ 0 before computing inverse
- Wrong sign in cofactor expansion
- Confusing row and column vectors
