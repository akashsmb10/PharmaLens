import pandas as pd

def number(value,kind='count'):
    if pd.isna(value): return 'Unavailable'
    if kind=='gbp': return f'£{value:,.2f}'
    if kind=='percent': return f'{value:,.2f}%'
    if kind=='ratio': return f'{value:,.4f}'
    return f'{value:,.0f}'
