import pandas as pd

vcf = 'csIaFkLbFNYDgIaV.vcf'

df = pd.read_csv(vcf, comment='#', sep='\t', header=None)
header = []
with open(vcf) as f:
    for line in f:
        if line.startswith('#CHROM'):
            header = line.strip().split('\t')
            break
df.columns = header

print(df.head())
df.to_csv('vcf_table.csv', index=False)
