"""Shared Plotly charts with explicit units and no cross-origin forecast lines."""
import plotly.express as px
import plotly.graph_objects as go
from textwrap import wrap
from .theme import COLORS

def styled(fig,title):
    fig.update_layout(title={'text':'<br>'.join(wrap(title,36)),'font':{'size':14}},template='plotly_white',height=420,font={'family':'Arial','size':13,'color':'#142B45'},
        colorway=COLORS,margin={'l':40,'r':20,'t':65,'b':45},legend={'orientation':'h','y':-0.2},paper_bgcolor='rgba(0,0,0,0)')
    return fig

def trend(frame,x,y,title,color=None,unit=''):
    f=frame.sort_values(([color] if color else [])+[x])
    fig=px.line(f,x=x,y=y,color=color,markers=True,color_discrete_sequence=COLORS,labels={y:unit or y,x:'Month'})
    return styled(fig,title)

def bars(frame,x,y,title,unit='',color=None):
    fig=px.bar(frame,x=x,y=y,color=color,color_discrete_sequence=COLORS,labels={y:unit or y,x:x.replace('_',' ')})
    fig.update_yaxes(rangemode='tozero')
    return styled(fig,title)

def scatter(frame,x,y,title,label=None):
    fig=px.scatter(frame,x=x,y=y,hover_name=label,color_discrete_sequence=COLORS)
    return styled(fig,title)

def heatmap(pivot,title,unit):
    fig=go.Figure(go.Heatmap(z=pivot.to_numpy(dtype=float),x=pivot.columns.astype(str),y=pivot.index.astype(str),colorscale='Blues',
        colorbar={'title':unit},hovertemplate='%{y}<br>%{x}<br>%{z:.2f} '+unit+'<extra></extra>'))
    return styled(fig,title)

def forecast_points(history,predictions,title):
    fig=go.Figure(go.Scatter(x=history.month,y=history.prescription_items,mode='lines',name='Observed items',line={'color':COLORS[0]}))
    for i,(variant,f) in enumerate(predictions.groupby('variant',sort=True)):
        f=f.sort_values(['target_date','origin_date'])
        custom=[[str(r.origin_date.date()),int(r.horizon),r.model_status] for r in f.itertuples()]
        fig.add_trace(go.Scatter(x=f.target_date,y=f.prediction,mode='markers',name=variant,customdata=custom,
            marker={'size':9,'symbol':['circle','diamond','square','cross','triangle-up'][i%5],'color':COLORS[(i+1)%len(COLORS)]},
            hovertemplate='Target %{x|%b %Y}<br>Items %{y:,.0f}<br>Origin %{customdata[0]}<br>Horizon %{customdata[1]} months<br>Status %{customdata[2]}<extra>%{fullData.name}</extra>'))
    fig.update_yaxes(title='Prescription items',rangemode='tozero')
    return styled(fig,title)

def actual_predicted(predictions,title):
    f=predictions[predictions.model_status.eq('ok') & predictions.prediction.notna()]
    fig=px.scatter(f,x='actual',y='prediction',color='variant',
        hover_data=['origin_date','target_date','horizon'],color_discrete_sequence=COLORS,
        labels={'actual':'Actual prescription items','prediction':'Predicted prescription items'})
    if not f.empty:
        lo=min(f.actual.min(),f.prediction.min()); hi=max(f.actual.max(),f.prediction.max())
        fig.add_shape(type='line',x0=lo,y0=lo,x1=hi,y1=hi,line={'color':'#6A7687','dash':'dot'})
    return styled(fig,title)
