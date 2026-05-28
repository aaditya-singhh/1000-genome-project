# 1000 Genomes Project — X and Y Chromosome Analysis

Population genetics and machine learning analysis of the [1000 Genomes Project](https://www.internationalgenome.org/) dataset, focusing on **X and Y chromosome variation** across 5 continental super-populations and 26 sub-populations.

The project covers the full pipeline from raw VCF data to publication-quality population genetics figures and ML classifiers that can predict a sample's ancestry from sex-chromosome genotypes alone.

---

## Key Results

| Task | Chromosome | Best Model | Accuracy |
|---|---|---|---|
| 5 super-population classification | X | SVM (RBF) | **98.60%** |
| 5 super-population classification | Y | XGBoost ×10 ensemble | **88.11%** |
| 26 sub-population classification | X | SVM (RBF) | **54.49%** |
| 26 sub-population classification | Y | SVM (RBF) | **38.46%** |

| Metric | X chromosome | Y chromosome |
|---|---|---|
| QC-passed variants | 3,437,097 | 60,789 |
| Samples | 2,504 (1,271 F + 1,233 M) | 1,233 males |
| K-Means ARI (k=5) | 0.8898 | 0.4637 |
| Most differentiated populations | AFR vs EAS (FST = 0.121) | AFR vs AMR |
| Highest heterozygosity | AFR (0.0372) | SAS (0.0125) |
| Tajima's D range (Y corrected) | [−1.45, −1.22] | [−2.59, −2.24] |

---

## Repository Structure

```
.
├── Code/                              # All notebooks and intermediate data files
│   ├── data_sort.py                   # VCF → CSV converter
│   │
│   ├── -- Y Chromosome --
│   ├── y_analysis.ipynb               # QC pipeline, allele frequency computation
│   ├── deeper_analysis.ipynb          # Population genetics (FST, PCA, Tajima's D, SFS)
│   ├── experiment1_ml.ipynb           # ML: 5 super-populations (Y)
│   ├── experiment2_ml.ipynb           # ML: 26 sub-populations (Y)
│   ├── experiment1_boosting_ensemble.ipynb     # XGBoost/LightGBM/CatBoost + Optuna (Y)
│   ├── experiment1_boosting_ensemble_50PC.ipynb # Same with adaptive PCA (Y)
│   ├── experiment1_cnn.ipynb          # XGBoost ×10 ensemble, 150 Optuna trials (Y)
│   │
│   ├── -- X Chromosome --
│   ├── X_analysis.ipynb               # QC pipeline, sex-aware encoding, streamed 27 GB
│   ├── X_deeper_analysis.ipynb        # Population genetics on MPS GPU
│   ├── X_experiment1_ml.ipynb         # ML: 5 super-populations (X), Gram-matrix PCA
│   ├── X_experiment2_ml.ipynb         # ML: 26 sub-populations (X)
│   ├── X_experiment2_other_approach.ipynb  # UMAP, 100 PCs, hierarchical classification
│   │
│   ├── -- Cross-Chromosome --
│   ├── XY_coevaluation.ipynb          # Side-by-side X vs Y ML results
│   ├── XY_coevolution.ipynb           # X–Y correlation analysis (fixed)
│   ├── xy_coevolution_updated.ipynb   # Statistically corrected coevolution analysis
│   │
│   └── chrY_AF_by_population.csv      # (and other intermediate CSV files)
│
├── Data/                              # Raw input files
│   ├── chrX_full.csv                  # X chromosome genotype table (~27 GB)
│   ├── convert_vcf-csv.py             # VCF conversion helper
│   └── explore_data.py
│
├── Output /                           # All generated figures and saved models
│   ├── coevo_*.png                    # Cross-chromosome analysis figures
│   ├── exp1_*.png / exp2_*.png / exp3_*.png
│   ├── chrX_*.png
│   ├── exp1_xgb_ensemble.pkl          # Saved XGBoost ×10 ensemble (Y, 5 super-pops)
│   └── exp3_boosting_ensemble.pkl     # Saved boosting ensemble (Y)
│
├── Techniques_Parameters_and_Outputs.txt   # Full hyperparameter reference
├── X_Chromosome_Analysis_Report.txt
└── README_Y_Chromosome_Analysis.md         # Legacy Y-chromosome README
```

---

## Pipeline Overview

```
Raw VCF
   │
   ├─ data_sort.py ──────────────────────────► vcf_table.csv
   │
   ├─ y_analysis.ipynb ──────────────────────► chrY_AF_by_population.csv  (60,789 variants)
   │       └─ deeper_analysis.ipynb            Population genetics + figures
   │               └─ experiment1/2_ml.ipynb   Supervised + unsupervised ML
   │                       └─ boosting ensembles, XGBoost CNN-style
   │
   └─ X_analysis.ipynb  (27 GB, chunked) ──► chrX_AF_by_population.csv  (3.4M variants)
           └─ X_deeper_analysis.ipynb         MPS GPU population genetics
                   └─ X_experiment1/2_ml.ipynb  Gram-matrix PCA (70 min on GPU)
                           └─ X_experiment2_other_approach.ipynb
                                   │
                                   └─ XY_coevolution*.ipynb   Cross-chromosome analysis
```

---

## Notebooks

### Data Pipelines

#### `y_analysis.ipynb` — Y chromosome QC and allele frequencies
- Loads raw Y chromosome VCF table (62,042 variants, 1,233 male samples)
- Detects males via call rate > 5% on hemizygous sites
- Applies QC: FILTER=PASS, QUAL > 30, biallelic only, call rate ≥ 0.95
- Outputs **60,789** QC-passed variants with per-population allele frequencies

#### `X_analysis.ipynb` — X chromosome QC with sex-aware encoding
- Streams the ~27 GB CSV in chunks of 2,000 variants using DuckDB column detection
- Applies sex-aware encoding: females diploid (0 / 0.5 / 1), males hemizygous (0 / 1)
- Outputs **3,437,097** QC-passed variants; 132,173 high-differentiation variants (max-min AF > 0.3)

---

### Population Genetics

#### `deeper_analysis.ipynb` / `X_deeper_analysis.ipynb`

Both notebooks apply the same analytical framework to Y and X respectively:

| Analysis | Method | Y result | X result |
|---|---|---|---|
| Diversity | Heterozygosity, private variants | SAS highest het; EAS most private | AFR highest in both |
| Differentiation | Weir-Cockerham FST (pairwise) | AFR vs AMR most differentiated | AFR vs EAS (FST = 0.121) |
| Population structure | PCA on AF matrix | 60.5% variance (PC1+PC2) | 96.5% variance (PC1+PC2) |
| Selection | Tajima's D (corrected formula) | −2.59 to −2.24 (strong negative) | −1.45 to −1.22 (negative) |
| Variant classes | AF < 1%, 1–5%, > 5% | 279,790 rare; 9,673 common | 15.1M rare; 1.35M common |
| Functional annotation | Position-based gene lookup | 252 variants in SRY, AMELY, DAZ | 69,672 in DMD, AR, MECP2, FMR1 |

The X chromosome analysis runs FST and PCA on **Apple Silicon MPS GPU** via PyTorch to handle the 3.4M × 2,504 allele-frequency tensor.

---

### Machine Learning

#### Y Chromosome — Experiment 1 (`experiment1_ml.ipynb`)
**Task:** classify 1,233 Y chromosome samples into 5 super-populations (AFR / AMR / EAS / EUR / SAS)

- Features: 60,789 variants → 50 PCA components (86.8% variance)
- 80/20 stratified train/test split

| Model | Test Accuracy | 5-fold CV |
|---|---|---|
| **Logistic Regression** | **86.23%** | 82.66% ± 2.70% |
| SVM (RBF) | 85.83% | 83.57% ± 1.97% |
| Random Forest | 85.83% | 83.47% ± 1.75% |
| KNN (k=5) | 83.00% | 82.15% ± 1.51% |
| Decision Tree | 80.97% | 79.82% ± 2.86% |

K-Means (k=5): ARI = 0.4637, NMI = 0.4922. AMR is the most confused class (smallest sample, overlaps with EUR).

#### Y Chromosome — Experiment 2 (`experiment2_ml.ipynb`)
**Task:** classify into **26 sub-populations**. Best: SVM 38.46% (random baseline = 3.8%).

#### Y Chromosome — Boosting Ensembles

| Notebook | Setup | Best Accuracy |
|---|---|---|
| `experiment1_boosting_ensemble.ipynb` | XGB + LGBM + CatBoost, 100 Optuna trials each, 15-model ensemble | **89.19%** (CatBoost ×5) |
| `experiment1_cnn.ipynb` | XGBoost ×10 ensemble, 150 Optuna trials | **88.11%** |

---

#### X Chromosome — Experiment 1 (`X_experiment1_ml.ipynb`)
**Task:** classify 2,504 samples into 5 super-populations

- Features: 3.4M variants → 50 PCA components via incremental **Gram-matrix PCA on MPS GPU** (~70 min)
- 80/20 stratified train/test split

| Model | Test Accuracy | 5-fold CV |
|---|---|---|
| **SVM (RBF)** | **98.60%** | 98.50% ± 0.84% |
| Random Forest | 97.21% | 97.55% ± 0.97% |
| KNN (k=5) | 97.01% | 96.85% ± 0.98% |
| Decision Tree | 96.41% | 95.96% ± 0.71% |
| Logistic Regression | 95.21% | 97.30% ± 1.06% |

K-Means (k=5): ARI = 0.8898, NMI = 0.8995. EAS and SAS clusters are essentially pure.

The X chromosome outperforms Y by ~12 percentage points, driven by 57× more variants and 2× more samples.

#### X Chromosome — Experiment 2 (`X_experiment2_ml.ipynb`)
**Task:** classify into **26 sub-populations**. Best: SVM 54.49%.

#### X Chromosome — Improved Approaches (`X_experiment2_other_approach.ipynb`)

| Approach | Method | Result |
|---|---|---|
| A | 100 PCA components + XGBoost, MLP, LDA | LDA: 56.69% (+2.2 pp over baseline) |
| B | 50-dim UMAP features | XGBoost: 45.31% (−9.18 pp — UMAP hurts here) |
| C | Hierarchical: SVM super-pop then SVM sub-pop | Eliminates cross-continent errors |

---

### Cross-Chromosome Analysis

#### `XY_coevaluation.ipynb` — ML results comparison
Compiles all X vs Y accuracy figures side by side. Key finding: X consistently outperforms Y in every model and both experiments; the accuracy drop from 5→26 classes is nearly identical for both chromosomes (~48 pp on Y, ~44 pp on X).

#### `xy_coevolution_updated.ipynb` — Statistically corrected coevolution analysis

Four sections, each measuring a different aspect of X–Y co-variation across populations:

| Section | Method | Result |
|---|---|---|
| 1. Cross-metric correlation | 10×10 Pearson matrix (5 populations × 10 metrics); BH-FDR corrected | Heterozygosity and polymorphic-site counts show strong X–Y concordance |
| 2. Variant signature concordance | K-means centroids (k=5) matched via **Hungarian algorithm**; permutation null (1,000 shuffles of population columns) | Z = 2.07, permutation **p = 0.015** — shared population archetypes are significant |
| 3. Association rules | Lift/confidence mining with Fisher exact test + FDR correction | No rules survive FDR at n=5 (underpowered by design) |
| 4. SFS correlation | 10×10 Pearson correlation between 50-bin SFS fingerprints | Same-chrom diff-pop pairs (mean r = 0.957) > intra-pop cross-chrom (mean r = 0.948) — X SFS is highly stable across populations |

> **Note:** `XY_coevolution.ipynb` is the same analysis with two fixed bugs: (1) Tajima's D formula now uses the correct Tajima 1989 constants (`e1 = c1/a1`, `e2 = c2/(a1²+a2)`) with per-population sample sizes; (2) the correlation matrix divisor is `len(POP_COLS)` (not `len(POP_COLS)-1`). The updated notebook has been re-run and shows correct outputs; `XY_coevolution.ipynb` has the corrected code but needs to be re-run.

---

## Reproducing the Analysis

### Prerequisites

```bash
pip install pandas numpy matplotlib seaborn scipy scikit-learn \
            torch xgboost lightgbm catboost optuna umap-learn \
            duckdb joblib
```

Python ≥ 3.10 recommended. The X chromosome notebooks use Apple Silicon MPS GPU (`torch.backends.mps`) but will fall back to CPU automatically.

### Data

The raw VCF files are from the 1000 Genomes Project Phase 3:
- Y chromosome: `ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/`
- X chromosome: corresponding chrX file (27 GB; not included in this repository)
- Population panel: `integrated_call_samples_v3.20130502.ALL.panel` (included)

### Execution Order

```
1.  data_sort.py                          # VCF → CSV
2.  y_analysis.ipynb                      # Y pipeline
3.  X_analysis.ipynb                      # X pipeline  (~70 min, 27 GB input)
4.  deeper_analysis.ipynb                 # Y population genetics
5.  X_deeper_analysis.ipynb               # X population genetics (MPS GPU)
6.  experiment1_ml.ipynb                  # Y Exp 1 — 5 super-pops
7.  experiment2_ml.ipynb                  # Y Exp 2 — 26 sub-pops
8.  experiment1_boosting_ensemble.ipynb   # Y boosting ensembles
9.  experiment1_cnn.ipynb                 # Y XGBoost ×10 ensemble
10. X_experiment1_ml.ipynb                # X Exp 1 — 5 super-pops  (~70 min, MPS GPU)
11. X_experiment2_ml.ipynb                # X Exp 2 — 26 sub-pops   (~70 min, MPS GPU)
12. X_experiment2_other_approach.ipynb    # X improved approaches
13. XY_coevaluation.ipynb                 # Cross-chromosome ML comparison
14. xy_coevolution_updated.ipynb          # Cross-chromosome correlation
```

Steps 10–11 recompute the Gram matrix from scratch and take ~70 minutes each on an M-series Mac. If you already have the intermediate CSVs (`chrX_AF_by_population.csv` etc.), steps 3 and 10–11 can be skipped.

---

## Selected Figures

| Figure | Notebook | Description |
|---|---|---|
| `Output /coevo_09_corr_matrix.png` | xy_coevolution_updated | 10×10 cross-metric Pearson correlation matrix |
| `Output /coevo_10_sig_corr.png` | xy_coevolution_updated | Centroid concordance test + dominant-population fractions |
| `Output /coevo_12a_intra_inter_heatmap.png` | xy_coevolution_updated | 10×10 SFS correlation matrix with boxplot by pair type |
| `Output /chrX_pca_plot.png` | X_deeper_analysis | PCA of X chromosome AF — populations cleanly separated |
| `Output /chrX_fst_heatmap.png` | X_deeper_analysis | Pairwise FST heatmap (X chromosome) |
| `Output /exp1_pca_true_labels.png` | experiment1_ml | PCA of 50-component Y chromosome features with true pop labels |
| `Output /exp3_model_comparison.png` | experiment1_boosting_ensemble | CatBoost/XGBoost/LightGBM vs baseline |

---

## Dataset

**1000 Genomes Project Phase 3** — the largest publicly available catalogue of human genetic variation.

| Property | Value |
|---|---|
| Total samples | 2,504 individuals |
| Populations | 26 sub-populations spanning 5 continental groups |
| Super-populations | AFR (Africa), AMR (Americas), EAS (East Asia), EUR (Europe), SAS (South Asia) |
| Reference genome | GRCh37/hg19 |
| Data type | Whole-genome sequencing, phased genotypes |

---

## Biological Interpretation

- **Y chromosome Tajima's D ≈ −2.5** (all populations): strong negative D consistent with purifying selection or a recent population expansion filtering out deleterious variants on the non-recombining Y.
- **X chromosome Tajima's D ≈ −1.4**: also negative but less extreme — X recombines in females, maintaining greater diversity.
- **SFS structure**: X chromosome SFS shape is nearly identical across all five populations (mean inter-population r = 0.957), reflecting the large number of variants stabilising the estimate. Y chromosome populations show more SFS divergence, consistent with smaller effective population size and stronger drift.
- **Centroid concordance (p = 0.015)**: Y and X variants cluster into population archetypes that match each other significantly better than chance — evidence of shared demographic history shaping both chromosomes.
- **X vs Y classification gap**: the ~12 percentage-point advantage of X over Y in 5-class ML is driven by (1) 57× more variants, (2) 2× more samples, and (3) X chromosome recombination preserving more population-specific haplotype structure.

---

## License

Data from the 1000 Genomes Project is publicly available under the [Creative Commons Attribution 4.0](https://creativecommons.org/licenses/by/4.0/) license. Analysis code in this repository is MIT licensed.
