# 🧬 Y-Chromosome Data Analysis – 1000 Genomes Project

This project performs a detailed analysis of **Y-chromosome variants** from the **1000 Genomes Project**.  
The goal is to study allele frequency differences among global populations, identify population-specific variants, and visualize genetic similarity across continents.

The workflow is split into two main notebooks:  
- `y_analysis.ipynb` → preprocessing, cleaning, filtering, and computation of allele frequencies  
- `deeper_analysis.ipynb` → advanced population analysis and visualization

---

## 📁 Detailed File Descriptions

### 🧩 `y_analysis.ipynb` — *Preprocessing and Data Preparation Notebook*

This notebook handles **all data-cleaning and setup tasks** to prepare the Y-chromosome data for analysis.  

It converts raw genotypes into structured, reliable, population-aware data ready for exploration.

#### **Step-by-step explanation:**

1. **Data Loading & Inspection**
   - Loads the converted CSV file (`chrY_1000g.csv`), which originated from a VCF (Variant Call Format) file of Y-chromosome variants.
   - Automatically detects the delimiter (tab, comma, etc.) and ensures the header is properly read.
   - Displays column names and checks that required VCF columns like `#CHROM`, `POS`, `ID`, `REF`, `ALT`, `QUAL`, and `FILTER` exist.

2. **Data Cleaning & Filtering**
   - Keeps only *high-confidence* variant entries:
     - `FILTER = PASS` → only variants that passed sequencing quality filters.
     - `QUAL > 30` → removes low-quality sites.
     - Removes *multi-allelic variants* (where ALT has multiple possible alleles).
   - Replaces missing genotype values (`.` or `./.`) with `NaN` for numeric handling.

3. **Identifying Male Samples**
   - Since only males have data on chromosome Y, the notebook detects male samples automatically:
     - Calculates how many Y-chromosome genotypes each sample has.
     - Samples with >5% called sites are labeled as **males**.
     - Female samples are ignored (since they have missing Y genotypes).

4. **Genotype Matrix Creation (`Gm`)**
   - Builds a genotype matrix with rows = variants and columns = male samples.
   - Converts genotype calls (`0`, `1`, or missing) into numeric values:
     - `0` → reference allele  
     - `1` → alternate allele  
     - `NaN` → missing value  

5. **Per-Variant Quality Metrics**
   - Computes variant-level statistics:
     - **Call Rate:** proportion of male samples with a valid call at that variant.
     - **Allele Frequency (AF):** average value of `1`s (ALT) across samples.
     - **Singleton Flag:** identifies variants found in only one male (rare variants).
   - Produces a summary table containing:
     ```
     CHROM | POS | ID | REF | ALT | QUAL | call_rate | AF | alt_count | singleton
     ```

6. **Per-Sample Quality Metrics**
   - For each male sample:
     - **Missing Rate:** fraction of Y-chromosome sites that have no call.
     - **ALT Burden:** total number of ALT alleles carried by that sample.
   - Helps identify low-quality individuals or unusual allele distributions.

7. **Quality Control (QC) Filtering**
   - Retains only variants that meet strict QC thresholds:
     - Call rate ≥ 0.95  
     - QUAL ≥ 30  
   - Removes low-quality variants and unreliable samples.

8. **Integrating Population Metadata**
   - Loads the `integrated_call_samples_v3.20130502.ALL.panel` file from the 1000 Genomes Project.
   - Links each male sample to its:
     - **Population code (e.g., GBR, YRI, CHB)**  
     - **Super-population (e.g., EUR, AFR, EAS, SAS, AMR)**
   - Filters metadata to keep only detected male samples.

9. **Population-Wise Allele Frequency Calculation**
   - Groups male samples by population and calculates the **average ALT allele frequency per variant** in each group.
   - The result is saved as:
     ```
     chrY_AF_by_population.csv
     ```
     where each column (AFR, EUR, EAS, SAS, AMR) represents the average frequency of ALT alleles in that population.

10. **Output Files from this Notebook**
    | Output File | Description |
    |--------------|-------------|
    | `chrY_variant_summary_qc.csv` | Contains per-variant statistics (CHROM, POS, REF, ALT, QUAL, call_rate, AF, singleton). |
    | `chrY_sample_summary_qc.csv` | Contains per-sample statistics (missing_rate, alt_burden) for male samples. |
    | `chrY_AF_by_population.csv` | Population-level average ALT allele frequencies, used for deeper analysis. |

---

### 🔬 `deeper_analysis.ipynb` — *Population Analysis and Visualization Notebook*

This notebook performs **in-depth analysis and visualization** using the cleaned outputs from `y_analysis.ipynb`.

It explores how Y-chromosome variants differ among global populations and visualizes population relationships.

#### **Step-by-step explanation:**

1. **Data Loading**
   - Imports the cleaned allele-frequency dataset `chrY_AF_by_population.csv`.
   - Automatically identifies population columns (AFR, EUR, EAS, SAS, AMR).
   - Optionally merges back variant information (`POS`, `ID`, etc.) for labeling.

2. **Correlation Analysis**
   - Computes pairwise **Pearson correlation coefficients** between populations.
   - Measures how similar allele frequencies are across groups.
   - Example: a high EUR–SAS correlation implies shared variant patterns between Europe and South Asia.

3. **Heatmap Visualization**
   - Creates a **heatmap of population correlations**:
     - Bright colors = higher correlation (genetically closer populations)
     - Darker colors = lower correlation (genetically more distinct)
   - Helps visualize overall population relatedness on chromosome Y.

4. **Variant-Level Heatmap (optional)**
   - Selects a subset of variants (e.g., 50 random ones).
   - Plots their allele frequencies across populations.
   - Shows which variants are rare, common, or population-specific.

5. **Frequency Distribution Plots**
   - Generates histograms for allele frequencies (AF) and call rates.
   - Helps distinguish rare variants (AF < 0.05) from common variants.
   - Allows comparing frequency distributions between populations.

6. **Outlier Detection**
   - Identifies **population-differentiated variants**, where:
     ```
     max(AF) - min(AF) > 0.3
     ```
     meaning the variant has at least a 30% difference in frequency between populations.
   - Saves these as potential population-specific or ancestry-informative SNPs.

7. **(Optional) PCA Analysis**
   - Performs Principal Component Analysis (PCA) on allele frequencies.
   - Visualizes clustering of populations based on Y-chromosome diversity.

8. **Outputs & Visuals**
   | Output | Description |
   |---------|-------------|
   | Population correlation heatmap | Shows genetic similarity between populations. |
   | Variant–population heatmap | Displays per-variant allele-frequency variation across groups. |
   | Frequency histograms | Show distribution of allele frequencies and call rates. |
   | Differentiated variants file | List of variants that vary significantly between populations. |


## 🧠 What You’ll Learn from the Analysis

- Which populations share the most similar Y-chromosome variants.  
- How allele frequencies differ across continents (e.g., rare in Europe, common in East Asia).  
- Which variants are unique or highly specific to certain ancestral lineages.  
- Overall genetic diversity and structure on the Y chromosome across global populations.
