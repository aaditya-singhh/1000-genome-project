# Code — 1000 Genomes Project

Population genetics analysis of the 1000 Genomes Project data, focused on the **X and Y chromosomes**. The project classifies human populations from sex-chromosome genotypes using both classical population genetics methods and machine learning.

---

## Project Structure at a Glance

```
Data Pipeline → Population Analysis → ML Experiments → Cross-Chromosome Analysis
```

| Stage | Y Chromosome | X Chromosome |
|---|---|---|
| Data pipeline | `y_analysis.ipynb` | `X_analysis.ipynb` |
| Pop. genetics | `deeper_analysis.ipynb` | `X_deeper_analysis.ipynb` |
| ML — Exp 1 (5 super-pops) | `experiment1_ml.ipynb` | `X_experiment1_ml.ipynb` |
| ML — Exp 2 (26 sub-pops) | `experiment2_ml.ipynb` | `X_experiment2_ml.ipynb` |
| Boosting ensembles | `experiment1_boosting_ensemble.ipynb`, `experiment1_boosting_ensemble_50PC.ipynb`, `experiment1_cnn.ipynb` | `X_experiment2_other_approach.ipynb` |
| Cross-chromosome | `XY_coevaluation.ipynb`, `XY_coevolution.ipynb`, `xy_coevolution_updated.ipynb` | — |

---

## Data Pipeline

### `data_sort.py`

Utility script that converts a raw VCF file to a CSV table.

- Reads `csIaFkLbFNYDgIaV.vcf`, extracts the `#CHROM` header line, assigns correct column names
- Outputs `vcf_table.csv` — the starting point for all Y-chromosome notebooks
- Uses pandas `read_csv` with `comment='#'`

**Run:** `python data_sort.py`

---

### `y_analysis.ipynb`

**Y chromosome data pipeline** — processes the raw VCF table into analysis-ready files.

| Step | Detail |
|---|---|
| Input | `Data/vcf_table.csv` (62,042 raw variants, 1,233 male samples) |
| Male detection | Call rate > 5% on hemizygous Y sites |
| QC filters | FILTER=PASS, QUAL > 30, biallelic only, variant call_rate ≥ 0.95, sample missingness < 10% |
| Output variants | **60,789** QC-passed variants |
| Population AF | Second-pass streaming: computes per-population allele frequencies for AFR/AMR/EAS/EUR/SAS |

**Output files:**
- `chrY_variant_summary_qc.csv` — per-variant stats (POS, REF, ALT, QUAL, call_rate, AF)
- `chrY_sample_summary_qc.csv` — per-sample missingness and alt burden
- `chrY_AF_by_population.csv` — allele frequency per variant per super-population

**Plots:** AF histogram, call-rate distribution, sample missingness, inter-population AF correlation heatmap, AF heatmap (50 random variants)

---

### `X_analysis.ipynb`

**X chromosome data pipeline** — mirrors `y_analysis.ipynb` but handles the larger X chromosome dataset (~27 GB CSV) and sex-aware diploid/hemizygous encoding.

| Step | Detail |
|---|---|
| Input | `Data/chrX_full.csv` (streamed in chunks of 2,000 variants) |
| Samples | 2,504 total (1,271 females = diploid 0/0.5/1, 1,233 males = hemizygous 0/1) |
| QC filters | Same thresholds as Y; processes all 3,437,097 passing variants in two streaming passes |
| Output variants | **3,437,097** QC-passed variants |

**Output files:**
- `chrX_variant_summary_qc.csv`
- `chrX_sample_summary_qc.csv`
- `chrX_AF_by_population.csv`
- `chrX_differentiated_variants.csv` — 132,173 variants with max-min AF delta > 0.3 across populations

**Key result:** Zero sample missingness across all 2,504 samples; 132K highly population-differentiated variants.

---

## Population Genetics Analysis

### `deeper_analysis.ipynb`

**Y chromosome deep dive** — population genetics characterisation of the Y chromosome across 5 super-populations.

| Section | Method | Key findings |
|---|---|---|
| Diversity metrics | Heterozygosity, private variants, polymorphic sites per population | SAS highest heterozygosity; EAS most private variants |
| Population differentiation | Pairwise Weir-Cockerham FST + 2-PC PCA | AFR vs AMR most differentiated; PCA: 60.5% variance |
| Rare vs common variants | AF binning (< 1%, 1–5%, > 5%) | 279,790 rare variants; 9,673 common |
| Selection signals | Simplified Tajima's D | No population shows \|D\| > 1 |
| Geographic patterns | FST-based hierarchical clustering dendrogram | Population phylogeny |
| Functional annotation | Position-based gene lookup (SRY, AMELY, TSPY, DAZ) | 252 variants in known Y genes |

**Output files:** `haplogroup_metrics.png`, `fst_heatmap.png`, `pca_plot.png`, `variant_frequency_distribution.png`, `tajimas_d.png`, `population_dendrogram.png`, `functional_annotation.png`, `analysis_summary.txt`

---

### `X_deeper_analysis.ipynb`

**X chromosome deep dive** — same analyses as `deeper_analysis.ipynb` but uses **Apple Silicon MPS GPU** for accelerated FST and PCA computation over 3.4M variants.

| Section | Method | Key findings |
|---|---|---|
| Diversity metrics | Same as Y | AFR highest heterozygosity AND most private variants |
| Population differentiation | GPU FST (all 3.4M variants) + GPU SVD PCA | AFR vs EAS most differentiated (FST=0.121); PCA: **96.5%** variance in PC1+PC2 |
| Rare vs common variants | AF binning | 15.1M rare, 1.35M common |
| Selection | Tajima's D per population | No population shows \|D\| > 1 |
| Geographic patterns | FST dendrogram | |
| Functional annotation | X-linked genes (DMD, AR, HPRT1, MECP2, FMR1, G6PD, XIST) | 69,672 variants in X-linked disease genes |

**Output files:** `chrX_diversity_metrics.png`, `chrX_fst_heatmap.png`, `chrX_pca_plot.png`, `chrX_variant_frequency_distribution.png`, `chrX_tajimas_d.png`, `chrX_population_dendrogram.png`, `chrX_functional_annotation.png`, `chrX_analysis_summary.txt`

---

## Y Chromosome — ML Experiments

### `experiment1_ml.ipynb`

**Experiment 1 — Y chromosome, 5 super-population classification.**

| Item | Value |
|---|---|
| Samples | 1,233 males |
| Features | 60,789 variants → **50 PCA components** |
| Task | Predict AFR / AMR / EAS / EUR / SAS |
| Split | 80% train / 20% test, stratified |

**Supervised results:**

| Model | Test Accuracy | CV Mean ± Std |
|---|---|---|
| **Logistic Regression** | **86.23%** | 82.66% ± 2.70% |
| SVM (RBF) | 85.83% | 83.57% ± 1.97% |
| Random Forest | 85.83% | 83.47% ± 1.75% |
| KNN (k=5) | 83.00% | 82.15% ± 1.51% |
| Decision Tree | 80.97% | 79.82% ± 2.86% |

**Unsupervised (K-Means, k=5):** ARI = 0.4637 | NMI = 0.4922

AMR is the hardest population to classify (smallest sample, most overlap with EUR).

---

### `experiment2_ml.ipynb`

**Experiment 2 — Y chromosome, 26 sub-population classification.**

Same QC pipeline and 50 PCA components as Experiment 1 but the target switches from 5 super-populations to **26 specific sub-populations** (e.g. YRI, CEU, CHB, GWD…).

**Supervised results:**

| Model | Test Accuracy | CV Mean ± Std |
|---|---|---|
| **SVM (RBF)** | **38.46%** | 35.50% ± 1.03% |
| **Random Forest** | **38.46%** | 37.13% ± 3.74% |
| KNN (k=5) | 37.65% | 35.30% ± 1.24% |
| Logistic Regression | 35.63% | 35.70% ± 1.67% |
| Decision Tree | 33.20% | 31.55% ± 2.14% |

**Unsupervised (K-Means, k=26):** ARI = 0.1780 | NMI = 0.4910 | Clustering Accuracy = 31.79%

Random baseline = 1/26 ≈ 3.8%. The drop from ~86% (5 classes) to ~38% (26 classes) reflects the limited genetic resolution of the Y chromosome for fine-grained sub-population separation.

---

### `experiment1_boosting_ensemble.ipynb`

**Experiment 3 — Y chromosome, Boosting Ensemble (XGBoost + LightGBM + CatBoost), 300 PCA components.**

Goal: beat the 86.23% Logistic Regression baseline using gradient boosting.

| Item | Value |
|---|---|
| PCA components | 300 (64.9% variance) |
| Split | 70% train / 15% val / 15% test |
| Tuning | Optuna Bayesian search, 100 trials per model |
| Ensemble | 5 seeds × 3 model types = **15 models**, soft-voting (averaged softmax probabilities) |
| Class imbalance | Inverse-frequency sample weights |

**Results:**

| Model | Test Accuracy |
|---|---|
| XGBoost ×5 | 87.57% |
| LightGBM ×5 | 86.49% |
| CatBoost ×5 | 89.19% |
| **Full Ensemble ×15** | **86.49%** |
| Baseline (LR) | 86.23% |

**Output:** `Output/exp3_boosting_ensemble.pkl` — saved ensemble with best hyperparameters.

---

### `experiment1_boosting_ensemble_50PC.ipynb`

**Experiment 2 (variant) — Y chromosome, Boosting Ensemble with auto-selected PCA components.**

Identical to `experiment1_boosting_ensemble.ipynb` except PCA components are **automatically selected** to explain ≥ 80% of variance (rather than fixed at 300). Same Optuna + 15-model ensemble architecture.

**Output:** `Output/exp2_boosting_ensemble.pkl`

---

### `experiment1_cnn.ipynb`

**Y chromosome — XGBoost ×10 Ensemble with Optuna (150 trials), 300 PCA components.**

Despite the "CNN" name, this notebook implements a **tuned XGBoost ensemble** with:
- 150-trial Optuna Bayesian search (more thorough than the 100-trial versions)
- 10-model ensemble (different seeds), trained on full train+val set
- MPS GPU for data preprocessing
- Focal loss / data augmentation infrastructure (prepared but XGBoost chosen as the final classifier)

**Results:**

| Model | Test Accuracy |
|---|---|
| Decision Tree | 80.97% |
| KNN (k=5) | 83.00% |
| SVM / Random Forest | 85.83% |
| Logistic Regression | 86.23% |
| **XGBoost ×10 Ensemble** | **88.11%** |

**Output:** `Output/exp1_xgb_ensemble.pkl`

---

## X Chromosome — ML Experiments

### `X_experiment1_ml.ipynb`

**Experiment 1 — X chromosome, 5 super-population classification.**

The X chromosome presents a unique challenge: females are diploid (0/0.5/1 dosage) while males are hemizygous (0/1). A full Gram-matrix PCA is computed **incrementally on GPU** to handle the 3.4M × 2,504 matrix without loading it into RAM.

| Item | Value |
|---|---|
| Samples | 2,504 (1,271 female + 1,233 male) |
| Variants | 3,449,249 (all QC-passed) |
| PCA method | Incremental Gram-matrix G = X Xᵀ on MPS GPU, ~70 min |
| PCA components | 50 (66.7% variance) |
| Split | 80% train / 20% test, stratified |

**Supervised results:**

| Model | Test Accuracy | CV Mean ± Std |
|---|---|---|
| **SVM (RBF)** | **98.60%** | 98.50% ± 0.84% |
| Random Forest | 97.21% | 97.55% ± 0.97% |
| KNN (k=5) | 97.01% | 96.85% ± 0.98% |
| Decision Tree | 96.41% | 95.96% ± 0.71% |
| Logistic Regression | 95.21% | 97.30% ± 1.06% |

**Unsupervised (K-Means, k=5):** ARI = 0.8898 | NMI = 0.8995

X chromosome vastly outperforms Y in every model (~12 percentage point gap at Exp 1), driven by 57× more variants and 2× more samples.

---

### `X_experiment2_ml.ipynb`

**Experiment 2 — X chromosome, 26 sub-population classification.**

Same Gram-matrix PCA pipeline as `X_experiment1_ml.ipynb` but classifies **26 specific sub-populations**. Takes ~70 min to compute the Gram matrix.

**Supervised results:**

| Model | Test Accuracy | CV Mean ± Std |
|---|---|---|
| **SVM (RBF)** | **54.49%** | 49.67% ± 2.17% |
| Logistic Regression | 48.50% | 45.08% ± 1.62% |
| Random Forest | 46.51% | 45.03% ± 1.60% |
| KNN (k=5) | 36.73% | 37.19% ± 3.44% |
| Decision Tree | 33.53% | 31.20% ± 1.03% |

**Unsupervised (K-Means, k=26):** ARI = 0.2077 | NMI = 0.5163 | Clustering Accuracy = 32.11%

Compared to Y Experiment 2 (~38%), the X chromosome performs better at sub-population classification (~54%), consistent with its richer variant set.

---

### `X_experiment2_other_approach.ipynb`

**Improved X chromosome sub-population classification** — three alternative approaches to beat the 54.49% SVM baseline.

| Approach | Description | Best Accuracy |
|---|---|---|
| **A: 100 PCA components** | Expand from 50 → 100 PCs; add XGBoost, MLP, LDA | **LDA: 56.69%** (+2.20 pp) |
| **B: UMAP features** | Non-linear 50-dim UMAP on top of 100 PCA components | XGBoost: 45.31% (−9.18 pp) |
| **C: Hierarchical classification** | Stage 1: SVM predicts super-pop (98.60%); Stage 2: SVM predicts sub-pop within super-pop | Improves on baseline |

**Key finding:** LDA (Linear Discriminant Analysis) with 100 PCs is the best single model. Hierarchical classification avoids cross-continent confusion (e.g., an African sub-population cannot be confused with an East Asian one). UMAP features hurt classification, likely because the non-linear embedding loses information useful for separating nearby sub-populations.

**K-Means clustering:** 100 PCs ARI = 0.2077 (unchanged from 50 PCs); UMAP ARI also similar.

---

## Cross-Chromosome Analysis

### `XY_coevaluation.ipynb`

**Side-by-side comparison of all X and Y chromosome ML results.**

Compiles results from all four experiments (Exp1 and Exp2 for both chromosomes) and produces comparative visualisations.

| Visualisation | Description |
|---|---|
| Exp 1 side-by-side bar chart | X vs Y accuracy for each model (5 super-populations) |
| Exp 2 side-by-side bar chart | X vs Y accuracy for each model (26 sub-populations) |
| K-Means ARI & NMI comparison | Grouped bars for both experiments |
| Summary heatmap | All 20 model×experiment×chromosome combinations in one view |
| Accuracy drop chart | How much accuracy falls going from 5→26 classes (similar for X and Y) |

**Key findings from summary printout:**
- X consistently outperforms Y across all models and both experiments
- Biggest gap: X SVM Exp1 (98.60%) vs Y LR Exp1 (86.23%) — 12.4 pp
- X K-Means ARI (0.89) vs Y K-Means ARI (0.46) — X clusters map cleanly to populations
- SVM (RBF) is the best model on X; Logistic Regression wins on Y

---

### `XY_coevolution.ipynb`

**X–Y chromosome correlation analysis** — investigates whether genetic diversity co-varies between chromosomes across populations.

| Section | Method | Key finding |
|---|---|---|
| 1. Cross-metric correlation matrix | 5×10 Pearson correlation matrix (5 populations × 10 metrics) | Heterozygosity and polymorphic-sites metrics show strong X–Y concordance; FST weakly correlated |
| 2. Variant population-signature correlation | Sample 5,000 variants from each chromosome; cluster into k=6 archetypes; measure inter-chromosome mixing | Variants cluster into shared archetypes shaped by the same populations |
| 3. Association rules | Binary (above/below median) metrics; mine lift/confidence/support for cross-chromosome rules | Several strong X→Y and Y→X rules; e.g. high Y heterozygosity predicts high X heterozygosity |
| 4. SFS correlation (intra- vs inter-pop) | 10×10 Pearson correlation between 50-bin Site Frequency Spectra | Diff-pop same-chrom pairs have the highest mean r (0.957); intra-pop X–Y pairs are slightly lower (0.948) |

---

### `xy_coevolution_updated.ipynb`

**Updated and statistically corrected version of `XY_coevolution.ipynb`.** The original analysis had a methodological issue in Section 2 (best-match correlation in 5D is always ~1.0 by chance — an extreme-value artifact), and the significance tests in Sections 1 and 3 did not apply multiple-testing correction. This notebook fixes both.

| Section | Correction |
|---|---|
| 1. Cross-metric correlation | p-values now replaced with **Benjamini-Hochberg FDR q-values** |
| 2. Variant signature concordance | Replaces best-match r (uninformative) with two rigorous tests: **(a)** centroid concordance via Hungarian matching + permutation null (n=1,000 shuffles); **(b)** dominant-population fraction test (Pearson r + Cramér's V + chi-square) |
| 3. Association rules | Rules filtered by FDR q ≤ 0.10 in addition to lift/confidence thresholds; Fisher's exact test added per rule |
| 4. SFS correlation | Identical to original; interpretation updated to note the differences between pair types are small and cautious |

**Key methodological note:** Tajima's D computation is also updated to use population-specific sample sizes (Y: 319–661 per population; X: 170–661 per population) instead of a fixed n=250, which shifts all Y Tajima's D values from ~−0.2 to ~−2.5 (the more accurate figure).

---

## Dependencies

```
pandas, numpy, matplotlib, seaborn, scipy
scikit-learn
torch (MPS/CUDA/CPU)
duckdb          # X_analysis.ipynb
xgboost, lightgbm, catboost
optuna
umap-learn      # X_experiment2_other_approach.ipynb
joblib
```

---

## Data Files (in `Code/` — generated by the pipeline)

| File | Description |
|---|---|
| `chrY_variant_summary_qc.csv` | 60,789 QC-passed Y chromosome variants |
| `chrY_sample_summary_qc.csv` | Per-sample missingness and alt burden (1,233 males) |
| `chrY_AF_by_population.csv` | Allele frequency per Y variant per super-population |
| `chrX_variant_summary_qc.csv` | 3,437,097 QC-passed X chromosome variants |
| `chrX_AF_by_population.csv` | Allele frequency per X variant per super-population |

## Recommended Execution Order

```
1. data_sort.py                          # VCF → CSV
2. y_analysis.ipynb                      # Y chromosome pipeline
3. X_analysis.ipynb                      # X chromosome pipeline
4. deeper_analysis.ipynb                 # Y population genetics
5. X_deeper_analysis.ipynb               # X population genetics
6. experiment1_ml.ipynb                  # Y Exp1 (5 super-pops)
7. experiment2_ml.ipynb                  # Y Exp2 (26 sub-pops)
8. experiment1_boosting_ensemble.ipynb   # Y boosting ensemble
9. X_experiment1_ml.ipynb               # X Exp1 (5 super-pops)
10. X_experiment2_ml.ipynb              # X Exp2 (26 sub-pops)
11. X_experiment2_other_approach.ipynb  # X improved approaches
12. XY_coevaluation.ipynb              # Cross-chromosome ML comparison
13. xy_coevolution_updated.ipynb        # Cross-chromosome correlation
```
