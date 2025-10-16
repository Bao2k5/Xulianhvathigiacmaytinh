# 🔬 GIẢI THÍCH THUẬT TOÁN CHI TIẾT

## Algorithm Explanation for Academic Paper

---

## 📚 MỤC LỤC

1. [MTCNN - Face Detection](#1-mtcnn---face-detection)
2. [FaceNet - Face Recognition](#2-facenet---face-recognition)
3. [Anti-Spoofing Methods](#3-anti-spoofing-methods)
4. [Pipeline tổng thể](#4-pipeline-tổng-thể)
5. [Toán học đằng sau](#5-toán-học-đằng-sau)

---

## 1. MTCNN - Face Detection

### 1.1 Tổng quan

**MTCNN** (Multi-task Cascaded Convolutional Networks) là kiến trúc CNN cascade 3 stages để detect faces và facial landmarks.

### 1.2 Kiến trúc

```
Input Image (H × W × 3)
    ↓
┌─────────────────────────────────────────┐
│  STAGE 1: Proposal Network (P-Net)      │
│  - Input: Image Pyramid (multiple scales)│
│  - Output: Candidate windows             │
│  - Purpose: Nhanh chóng tìm vùng có thể chứa face│
└─────────────────┬───────────────────────┘
                  ↓
        Non-Maximum Suppression (NMS)
                  ↓
┌─────────────────────────────────────────┐
│  STAGE 2: Refine Network (R-Net)        │
│  - Input: Candidates từ P-Net           │
│  - Output: Refined windows               │
│  - Purpose: Loại bỏ false positives     │
└─────────────────┬───────────────────────┘
                  ↓
        Non-Maximum Suppression (NMS)
                  ↓
┌─────────────────────────────────────────┐
│  STAGE 3: Output Network (O-Net)        │
│  - Input: Refined candidates            │
│  - Output: Final bounding boxes +       │
│            5 facial landmarks            │
│  - Purpose: Xác định chính xác vị trí   │
└─────────────────┬───────────────────────┘
                  ↓
    Bounding Boxes + Landmarks
```

### 1.3 Chi tiết từng stage

#### Stage 1: P-Net (Proposal Network)

**Input**: Image pyramid với scales khác nhau
**Output**: Candidate face regions

**Network Architecture**:

```
Input (12 × 12 × 3)
    ↓
Conv1: 3×3, stride=1 → (10 × 10 × 10)
    ↓
PReLU + MaxPool 2×2 → (5 × 5 × 10)
    ↓
Conv2: 3×3 → (3 × 3 × 16)
    ↓
PReLU
    ↓
Conv3: 3×3 → (1 × 1 × 32)
    ↓
PReLU
    ↓
┌────────┬────────┬────────┐
│ Face   │ BBox   │        │
│ Cls    │ Reg    │        │
│ (2)    │ (4)    │        │
└────────┴────────┴────────┘
```

**Loss Function**:

```
L = L_cls + λ₁·L_box

Trong đó:
- L_cls: Binary cross-entropy cho classification
- L_box: Smooth L1 loss cho bounding box regression
- λ₁: Trọng số (thường = 0.5)
```

#### Stage 2: R-Net (Refine Network)

**Input**: 24 × 24 patches từ P-Net
**Output**: Refined face regions

**Network Architecture**:

```
Input (24 × 24 × 3)
    ↓
Conv1: 3×3 → (22 × 22 × 28)
PReLU + MaxPool 3×3 → (11 × 11 × 28)
    ↓
Conv2: 3×3 → (9 × 9 × 48)
PReLU + MaxPool 3×3 → (4 × 4 × 48)
    ↓
Conv3: 2×2 → (3 × 3 × 64)
PReLU
    ↓
FC: 128 units
    ↓
┌────────┬────────┐
│ Face   │ BBox   │
│ Cls    │ Reg    │
└────────┴────────┘
```

#### Stage 3: O-Net (Output Network)

**Input**: 48 × 48 patches từ R-Net
**Output**: Final bounding boxes + 5 landmarks

**Network Architecture**:

```
Input (48 × 48 × 3)
    ↓
Conv1: 3×3 → (46 × 46 × 32)
PReLU + MaxPool 3×3 → (23 × 23 × 32)
    ↓
Conv2: 3×3 → (21 × 21 × 64)
PReLU + MaxPool 3×3 → (10 × 10 × 64)
    ↓
Conv3: 3×3 → (8 × 8 × 64)
PReLU + MaxPool 2×2 → (4 × 4 × 64)
    ↓
Conv4: 2×2 → (3 × 3 × 128)
PReLU
    ↓
FC: 256 units
    ↓
┌────────┬────────┬──────────┐
│ Face   │ BBox   │ Landmark │
│ Cls    │ Reg    │ (10)     │
└────────┴────────┴──────────┘
```

**5 Landmarks**:

1. Left eye center
2. Right eye center
3. Nose tip
4. Left mouth corner
5. Right mouth corner

### 1.4 Training Details

**Multi-task Loss**:

```
L = α·L_cls + β·L_box + γ·L_landmark

Trong đó:
- L_cls: Face classification loss
- L_box: Bounding box regression loss
- L_landmark: Facial landmark localization loss
- α, β, γ: Trọng số (thường 1, 0.5, 0.5)
```

**Optimization**:

- Optimizer: Stochastic Gradient Descent (SGD)
- Learning rate: 0.001 (với decay)
- Batch size: 384
- Data augmentation: Flip, rotate, scale

---

## 2. FaceNet - Face Recognition

### 2.1 Tổng quan

**FaceNet** học một embedding space trong đó khoảng cách Euclidean tương ứng với similarity giữa các khuôn mặt.

**Mục tiêu**:

```
Same person → Small distance
Different people → Large distance
```

### 2.2 Architecture: InceptionResnetV1

```
Input Face Image (160 × 160 × 3)
    ↓
┌────────────────────────────────────┐
│   Stem (Initial Conv layers)       │
│   Conv 3×3, stride=2               │
│   Conv 3×3                         │
│   Conv 3×3, stride=2               │
└────────────────┬───────────────────┘
                 ↓
┌────────────────────────────────────┐
│   Inception-Resnet-A × 5           │
│   (Mixed layers with residual)     │
└────────────────┬───────────────────┘
                 ↓
    Reduction-A
                 ↓
┌────────────────────────────────────┐
│   Inception-Resnet-B × 10          │
└────────────────┬───────────────────┘
                 ↓
    Reduction-B
                 ↓
┌────────────────────────────────────┐
│   Inception-Resnet-C × 5           │
└────────────────┬───────────────────┘
                 ↓
    Global Average Pooling
                 ↓
    Dropout (keep_prob=0.8)
                 ↓
    Fully Connected (512 units)
                 ↓
    L2 Normalization
                 ↓
    512-D Embedding Vector
```

### 2.3 Inception-Resnet Block

**Inception-Resnet-A**:

```
Input
  ↓
┌───┬───┬───┐
│1×1│1×1│1×1│
│   │→5×5│→3×3│
│   │   │→3×3│
└───┴───┴───┘
  ↓   ↓   ↓
  Concat
    ↓
  1×1 Conv (Linear)
    ↓
  Scale (λ=0.17)
    ↓
    + ← Input (Residual)
    ↓
  ReLU
```

### 2.4 Triplet Loss

**Core Idea**: Học embedding sao cho:

- Anchor-Positive gần nhau
- Anchor-Negative xa nhau

**Triplet**:

- **Anchor** (A): Ảnh gốc
- **Positive** (P): Ảnh cùng người
- **Negative** (N): Ảnh người khác

**Loss Function**:

```
L = max(0, ||f(A) - f(P)||² - ||f(A) - f(N)||² + α)

Trong đó:
- f(x): Embedding function
- ||·||: L2 norm
- α: Margin (thường = 0.2)
```

**Mục tiêu**:

```
||f(A) - f(P)||² + α < ||f(A) - f(N)||²

Nghĩa là:
Distance(A, P) + margin < Distance(A, N)
```

### 2.5 Hard Negative Mining

**Vấn đề**: Hầu hết triplets đều "dễ" (loss = 0)

**Giải pháp**: Chỉ chọn hard triplets:

1. **Hard Positive**:

   ```
   argmax ||f(A) - f(P)||²
   P∈{same_identity}
   ```

2. **Hard Negative**:

   ```
   argmin ||f(A) - f(N)||²
   N∈{diff_identity}
   ```

3. **Semi-Hard Negative**:
   ```
   ||f(A) - f(P)||² < ||f(A) - f(N)||² < ||f(A) - f(P)||² + α
   ```

### 2.6 Face Verification

**Input**: 2 face images
**Output**: Same person (Yes/No)

**Algorithm**:

```python
def verify(face1, face2, threshold=0.6):
    # Extract embeddings
    emb1 = facenet(face1)  # 512-D vector
    emb2 = facenet(face2)  # 512-D vector

    # Calculate distance
    distance = np.linalg.norm(emb1 - emb2)

    # Decision
    if distance < threshold:
        return "Same person"
    else:
        return "Different people"
```

**Euclidean Distance**:

```
d = √(Σᵢ(emb1ᵢ - emb2ᵢ)²)
```

**Cosine Similarity** (alternative):

```
similarity = (emb1 · emb2) / (||emb1|| × ||emb2||)

if similarity > threshold:
    → Same person
```

### 2.7 Face Recognition (1:N)

**Input**: 1 face image, N registered faces
**Output**: Identity (or Unknown)

**Algorithm**:

```python
def recognize(face, database, threshold=0.6):
    # Extract embedding
    emb_query = facenet(face)

    # Compare with all in database
    min_distance = float('inf')
    best_match = None

    for identity, emb_db in database.items():
        distance = np.linalg.norm(emb_query - emb_db)

        if distance < min_distance:
            min_distance = distance
            best_match = identity

    # Decision
    if min_distance < threshold:
        return best_match
    else:
        return "Unknown"
```

---

## 3. Anti-Spoofing Methods

### 3.1 Tổng quan

**Mục tiêu**: Phân biệt khuôn mặt thật (live) vs giả (spoof)

**Loại tấn công**:

1. Photo attack (ảnh in)
2. Video replay attack
3. 3D mask attack

### 3.2 Method 1: Texture Analysis

#### 3.2.1 Local Binary Pattern (LBP)

**Nguyên lý**: Ảnh in có texture đồng đều hơn da người thật

**Algorithm**:

```python
def compute_lbp(image, point=(x, y)):
    center = image[y, x]
    code = 0

    # 8 neighbors
    neighbors = [
        image[y-1, x-1], image[y-1, x], image[y-1, x+1],
        image[y, x+1], image[y+1, x+1], image[y+1, x],
        image[y+1, x-1], image[y, x-1]
    ]

    for i, neighbor in enumerate(neighbors):
        if neighbor > center:
            code |= (1 << i)

    return code
```

**LBP Code** (8-bit):

```
       n₀  n₁  n₂
       n₇  c   n₃
       n₆  n₅  n₄

LBP = Σᵢ s(nᵢ - c) × 2ⁱ

Trong đó:
s(x) = 1 if x ≥ 0
       0 if x < 0
```

**Features**:

- Histogram of LBP codes
- Variance of LBP
- Entropy of LBP distribution

#### 3.2.2 Frequency Domain Analysis (FFT)

**Nguyên lý**: Ảnh in thiếu high-frequency components

**Algorithm**:

```python
def frequency_analysis(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Apply FFT
    fft = np.fft.fft2(gray)
    fft_shift = np.fft.fftshift(fft)

    # Magnitude spectrum
    magnitude = np.abs(fft_shift)

    # Analyze frequency distribution
    H, W = magnitude.shape
    center_h, center_w = H//2, W//2

    # High frequency ratio
    high_freq = (magnitude[0:center_h//2, :].sum() +
                 magnitude[center_h+center_h//2:, :].sum())
    total_freq = magnitude.sum()

    ratio = high_freq / total_freq

    # Real face: ratio > threshold
    return ratio
```

**Power Spectrum**:

```
P(u, v) = |F(u, v)|²

Trong đó:
- F(u, v): Fourier transform
- (u, v): Frequency coordinates
```

### 3.3 Method 2: Blink Detection

#### 3.3.1 Eye Aspect Ratio (EAR)

**Nguyên lý**: Ảnh in không nháy mắt

**Formula**:

```
       p₁      p₂
         ╱──╲
        │    │
         ╲__╱
       p₆      p₅
     p₃        p₄

EAR = (||p₂ - p₆|| + ||p₃ - p₅||) / (2 × ||p₁ - p₄||)

Trong đó:
- p₁, p₄: Horizontal eye corners
- p₂, p₃, p₅, p₆: Vertical eye points
```

**Properties**:

- Open eye: EAR ≈ 0.3
- Closed eye: EAR ≈ 0.1
- Blink: EAR drops then rises

**Blink Detection Algorithm**:

```python
def detect_blink(ear_sequence, threshold=0.2, consec_frames=3):
    blink_counter = 0
    blink_total = 0

    for ear in ear_sequence:
        if ear < threshold:
            blink_counter += 1
        else:
            if blink_counter >= consec_frames:
                blink_total += 1
            blink_counter = 0

    return blink_total
```

### 3.4 Method 3: Motion Analysis

#### 3.4.1 Optical Flow

**Nguyên lý**: Video replay có motion pattern khác người thật

**Lucas-Kanade Method**:

```
Assumptions:
1. Brightness constancy: I(x,y,t) = I(x+dx,y+dy,t+dt)
2. Small motion: Taylor expansion

I(x+dx,y+dy,t+dt) ≈ I(x,y,t) + ∂I/∂x·dx + ∂I/∂y·dy + ∂I/∂t·dt

Optical Flow Equation:
Iₓ·u + Iᵧ·v + Iₜ = 0

Trong đó:
- (u, v): Velocity vector
- Iₓ, Iᵧ: Spatial gradients
- Iₜ: Temporal gradient
```

**Farneback Method** (denser flow):

```python
flow = cv2.calcOpticalFlowFarneback(
    prev_gray, next_gray, None,
    pyr_scale=0.5,    # Pyramid scale
    levels=3,         # Number of pyramid layers
    winsize=15,       # Averaging window size
    iterations=3,     # Iterations at each level
    poly_n=5,         # Polynomial expansion
    poly_sigma=1.2,   # Gaussian std
    flags=0
)

# Magnitude and angle
magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
```

**Features**:

1. **Magnitude Variance**:

   ```
   σ²(mag) = E[(mag - μ)²]
   ```

2. **Direction Entropy**:

   ```
   H(angle) = -Σᵢ p(θᵢ)·log(p(θᵢ))
   ```

3. **Average Magnitude**:
   ```
   μ(mag) = (1/N)·Σᵢ mag(i)
   ```

### 3.5 Method 4: Depth Analysis

#### 3.5.1 Gradient-based Depth

**Nguyên lý**: Khuôn mặt 3D có gradient phức tạp hơn ảnh 2D

**Sobel Operator**:

```
Gₓ = [-1  0  1]       Gᵧ = [-1 -2 -1]
     [-2  0  2]            [ 0  0  0]
     [-1  0  1]            [ 1  2  1]

Gradient magnitude:
G = √(Gₓ² + Gᵧ²)

Gradient direction:
θ = atan2(Gᵧ, Gₓ)
```

**Features**:

```python
def depth_features(image):
    gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)

    # Sobel gradients
    sobelx = cv2.Sobel(gray, cv2.CV_64F, 1, 0, ksize=5)
    sobely = cv2.Sobel(gray, cv2.CV_64F, 0, 1, ksize=5)

    # Magnitude
    magnitude = np.sqrt(sobelx**2 + sobely**2)

    # Features
    features = {
        'mean_gradient': np.mean(magnitude),
        'std_gradient': np.std(magnitude),
        'max_gradient': np.max(magnitude)
    }

    return features
```

#### 3.5.2 Shadow/Highlight Analysis

**Nguyên lý**: Khuôn mặt 3D có shadow/highlight tự nhiên

**Otsu's Thresholding**:

```
Maximize inter-class variance:
σ²_between = w₀(μ₀ - μ_total)² + w₁(μ₁ - μ_total)²

Trong đó:
- w₀, w₁: Class weights
- μ₀, μ₁: Class means
- μ_total: Total mean
```

**Contrast Ratio**:

```
CR = (L_max - L_min) / (L_max + L_min)

Trong đó:
- L_max: Brightest region
- L_min: Darkest region
```

### 3.6 Liveness Score Fusion

**Multi-method Fusion**:

```
L = w₁·S_texture + w₂·S_blink + w₃·S_motion + w₄·S_depth

Trong đó:
- Sᵢ ∈ [0, 1]: Normalized score của method i
- wᵢ: Weight (Σwᵢ = 1)
- L ≥ threshold → LIVE
- L < threshold → SPOOF
```

**Weighted Average** (default):

```
w₁ = w₂ = w₃ = w₄ = 0.25
```

**Adaptive Weighting** (advanced):

```
wᵢ = conf(Sᵢ) / Σⱼ conf(Sⱼ)

Trong đó:
conf(S): Confidence of score S
```

---

## 4. Pipeline Tổng Thể

### 4.1 Attendance System Flowchart

```
START
  ↓
┌──────────────────┐
│ Capture Frame    │
│ from Camera      │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ MTCNN            │ ← Face Detection
│ Detect Faces     │
└────────┬─────────┘
         ↓
    Has Face?
    ↙     ↘
  Yes      No → Return to Capture
    ↓
┌──────────────────┐
│ Anti-Spoofing    │ ← Liveness Check
│ Analysis         │
└────────┬─────────┘
         ↓
    Is Real?
    ↙     ↘
  Yes      No → Reject + Log Spoofing
    ↓
┌──────────────────┐
│ FaceNet          │ ← Extract Embedding
│ Get Embedding    │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Compare with     │ ← Face Recognition
│ Database         │
└────────┬─────────┘
         ↓
   Match Found?
    ↙     ↘
  Yes      No → Display "Unknown"
    ↓
┌──────────────────┐
│ Check Time       │ ← Attendance Rule
│ Constraints      │
└────────┬─────────┘
         ↓
    Valid?
    ↙     ↘
  Yes      No → Skip (Too soon)
    ↓
┌──────────────────┐
│ Log Attendance   │ ← Database Write
│ to Database      │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Update UI        │ ← Display Result
│ Show Success     │
└────────┬─────────┘
         ↓
        END
```

### 4.2 Registration Flow

```
START
  ↓
┌──────────────────┐
│ Input Employee   │
│ Information      │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Capture N images │ (N = 5 default)
│ from Camera      │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ For each image:  │
│ - MTCNN detect   │
│ - Quality check  │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ FaceNet extract  │
│ N embeddings     │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Average          │
│ embeddings       │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Save to:         │
│ - SQLite DB      │
│ - Embeddings PKL │
└────────┬─────────┘
         ↓
        END
```

---

## 5. Toán Học Đằng Sau

### 5.1 Convolutional Neural Networks

**Convolution Operation**:

```
(I * K)(x, y) = ΣΣ I(x+i, y+j)·K(i, j)
                i j

Trong đó:
- I: Input image
- K: Kernel/filter
- *: Convolution operator
```

**Pooling**:

```
Max Pooling:
P(x, y) = max{I(x+i, y+j) | i,j ∈ window}

Average Pooling:
P(x, y) = (1/|W|)·ΣI(x+i, y+j)
```

### 5.2 Activation Functions

**ReLU**:

```
f(x) = max(0, x)
f'(x) = {1 if x > 0, 0 if x ≤ 0}
```

**PReLU** (Parametric ReLU):

```
f(x) = {x if x > 0, α·x if x ≤ 0}

Trong đó α được học trong training
```

### 5.3 Batch Normalization

```
μ_B = (1/m)·Σxᵢ          # Mean
σ²_B = (1/m)·Σ(xᵢ - μ_B)² # Variance

x̂ᵢ = (xᵢ - μ_B) / √(σ²_B + ε)  # Normalize

yᵢ = γ·x̂ᵢ + β            # Scale and shift

Trong đó:
- m: Batch size
- ε: Small constant (10⁻⁵)
- γ, β: Learnable parameters
```

### 5.4 Loss Functions

**Cross-Entropy Loss**:

```
L = -Σᵢ yᵢ·log(ŷᵢ)

Trong đó:
- yᵢ: True label (one-hot)
- ŷᵢ: Predicted probability
```

**Smooth L1 Loss**:

```
L₁_smooth(x) = {0.5·x²      if |x| < 1
               {|x| - 0.5   otherwise
```

**Triplet Loss**:

```
L = Σ[||f(A) - f(P)||² - ||f(A) - f(N)||² + α]₊

Trong đó [x]₊ = max(0, x)
```

### 5.5 Optimization

**Stochastic Gradient Descent**:

```
θₜ₊₁ = θₜ - η·∇L(θₜ)

Trong đó:
- θ: Parameters
- η: Learning rate
- ∇L: Gradient of loss
```

**Adam Optimizer**:

```
mₜ = β₁·mₜ₋₁ + (1-β₁)·gₜ      # First moment
vₜ = β₂·vₜ₋₁ + (1-β₂)·gₜ²     # Second moment

m̂ₜ = mₜ/(1-β₁ᵗ)               # Bias correction
v̂ₜ = vₜ/(1-β₂ᵗ)

θₜ = θₜ₋₁ - η·m̂ₜ/√(v̂ₜ + ε)

Trong đó:
- β₁ = 0.9, β₂ = 0.999
- ε = 10⁻⁸
```

### 5.6 Metrics

**Euclidean Distance**:

```
d(x, y) = √(Σᵢ(xᵢ - yᵢ)²) = ||x - y||₂
```

**Cosine Distance**:

```
d_cos(x, y) = 1 - (x·y)/(||x||·||y||)
```

**Accuracy**:

```
Acc = (TP + TN) / (TP + TN + FP + FN)
```

**F1 Score**:

```
Precision = TP / (TP + FP)
Recall = TP / (TP + FN)
F1 = 2·(Precision·Recall)/(Precision + Recall)
```

---

## 📚 TÀI LIỆU THAM KHẢO

### Papers:

1. **MTCNN**:

   - Zhang, K., et al. (2016). "Joint Face Detection and Alignment using Multi-task Cascaded Convolutional Networks." IEEE Signal Processing Letters.

2. **FaceNet**:

   - Schroff, F., et al. (2015). "FaceNet: A Unified Embedding for Face Recognition and Clustering." CVPR.

3. **InceptionNet**:

   - Szegedy, C., et al. (2017). "Inception-v4, Inception-ResNet and the Impact of Residual Connections on Learning." AAAI.

4. **Anti-Spoofing**:

   - Boulkenafet, Z., et al. (2016). "Face Spoofing Detection Using Colour Texture Analysis." IEEE TIFS.
   - Chingovska, I., et al. (2012). "On the Effectiveness of Local Binary Patterns in Face Anti-spoofing." BIOSIG.

5. **Triplet Loss**:
   - Hermans, A., et al. (2017). "In Defense of the Triplet Loss for Person Re-Identification." arXiv.

---

## 🎓 KẾT LUẬN

Document này cung cấp giải thích chi tiết về:

- ✅ Kiến trúc MTCNN (3 stages)
- ✅ FaceNet với Triplet Loss
- ✅ 4 phương pháp Anti-Spoofing
- ✅ Pipeline xử lý
- ✅ Công thức toán học

Có thể sử dụng trực tiếp cho:

- 📝 Báo cáo tiểu luận
- 📊 Slide thuyết trình
- 📖 Paper nếu publish

---

**Made for academic purposes** 🎓
**Date**: October 2025
