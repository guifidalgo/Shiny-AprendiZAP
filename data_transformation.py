import pandas as pd
import datetime as dt

df = pd.read_parquet('data-raw/fct_teachers_entries.parquet')
dim_teachers = pd.read_parquet("data-raw/dim_teachers.parquet")


df['duracao_minutos'] = pd.to_datetime(df['data_fim']) - pd.to_datetime(df['data_inicio'])
df['duracao_minutos'] = df['duracao_minutos'].dt.total_seconds() / 60
df['data_inicio'] = pd.to_datetime(df['data_inicio']).dt.tz_localize(None)
df['data_fim'] = pd.to_datetime(df['data_fim']).dt.tz_localize(None)

ref_date = df['data_inicio'].max() + dt.timedelta(days=1)
rfm = df.groupby('unique_id').agg({
    'data_inicio': lambda x: (ref_date - x.max()).days,
    'unique_id': 'count',
    'duracao_minutos': 'sum'
}).rename(columns={
    'data_inicio': 'Recency',
    'unique_id': 'Frequency',
    'duracao_minutos': 'Duration'
})

# Score por quintis
rfm['R_score'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1])
rfm['F_score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
rfm['M_score'] = pd.qcut(rfm['Duration'], 5, labels=[1,2,3,4,5])

# Criar código RFM
rfm['RFM_Segment'] = rfm['R_score'].astype(str) + rfm['F_score'].astype(str) + rfm['M_score'].astype(str)
rfm['RFM_Score'] = rfm[['R_score','F_score','M_score']].astype(int).sum(axis=1)


teachers = dim_teachers.merge(rfm, on='unique_id', how='inner')
teachers['data_entrada'] = teachers['data_entrada'].dt.tz_localize(None)
teachers['semana_entrada'] = (teachers['data_entrada'] - pd.to_timedelta(teachers['data_entrada'].dt.dayofweek, unit='d')).dt.date

entries = df.merge(teachers, on='unique_id', how='inner')

teachers.to_parquet('data-transformed/teachers_entries.parquet')
entries.to_parquet('data-transformed/entries.parquet')