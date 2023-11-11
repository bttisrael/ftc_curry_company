from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
import numpy as np
from PIL import Image
import folium
from streamlit_folium import folium_static
st.set_page_config(page_title = 'Visão Restaurantes', layout = 'wide')
image = Image.open('OIP.jpg')
st.sidebar.image(image,width =120)
df = pd.read_csv('train.crdownload')
print(df.head())

#Limpeza de dados:
def clean_code(df1):
    df1 = df.copy()
    
    linhas_selecionadas = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    
    linhas_selecionadas = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    linhas_selecionadas = (df1['Time_taken(min)'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    linhas_selecionadas = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    linhas_selecionadas = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1.shape
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format ='%d-%m-%Y')
    linhas_selecioandas = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_selecionadas, :].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(float)
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Festival'] = df1.loc[:,'Festival'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()
    def extract_time(text):
        try:
            return int(str(text).split('(min) ')[1])
        except (ValueError, IndexError):
            return None
    
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(extract_time)
    
    return df1

def distance(df1,fig):
        if fig == False:
            cols = ['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
            df1['distance'] = df1.loc[:,cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),(x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
            avg_distance = df1['distance'].mean()
            return avg_distance
        else:
            cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
            df1['distance'] = df1.loc[:,cols].apply(lambda x:
        haversine((x['Restaurant_latitude'],x['Restaurant_longitude']),(x['Delivery_location_latitude'],x['Delivery_location_longitude'])),axis =1)
            avg_distance = df1.loc[:,['City','distance']].groupby('City').mean().reset_index()
            fig = go.Figure(data=go.Pie(labels = avg_distance['City'],values=avg_distance['distance'], pull=[0,0.1,0]))
            return fig

def avg_std_time_delivery(df1,festival,op):
    """ 
        Esta função calcula o tempo medio e desvio padrão do                        tempo de entrega
        input:
            - df: dataframe com os dados para o cálculo
            - op: Tipo de operação a ser calculado
            - avg_time
            - std_time
        output
            - df: dataframe com 2 colunas e uma linha
    """
    df_aux=(df1.loc[:,['Time_taken(min)','Festival']]).groupby('Festival').agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux=df_aux.reset_index()
    df_aux=df_aux.loc[df_aux['Festival'] =='Yes',op]
    return df_aux

def avg_std_time_graph(df1,fig):
    df_aux = df1.loc[:, ['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control',x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data',array=df_aux['std_time'])))
    fig.update_layout(barmode='group')
    return fig

def avg_std_time_on_traffic(df1,fig):
    cols = ['City','Time_taken(min)','Road_traffic_density']
    df_aux = df1.loc[:,cols].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':['mean','std']})
    df_aux.columns = ['avg_time','std_time']
    df_aux = df_aux.reset_index()
    fig = px.sunburst(df_aux,path=['City','Road_traffic_density'], values = 'avg_time', color ='std_time', color_continuous_scale = 'RdBu', color_continuous_midpoint = np.average(df_aux['std_time']))
    return fig


df1 = clean_code(df)

## LAYOUT STREAMLIT
# BARRA LATERAL
##
st.header('Marketplace - Visão Restaurantes')
image_path='OIP.jpg'
image = Image.open(image_path)
st.sidebar.image(image, width = 120)
st.sidebar.markdown('# Cury Company')
st.sidebar.markdown('## Fastest Delivery in Town')


st.sidebar.markdown('## Selecione uma data limite')
data_slider = st.sidebar.slider('Até qual valor',value =pd.datetime(2022,4,13),min_value=pd.datetime(2022,2,11),max_value=pd.datetime(2022,4,6),format=('DD-MM-YYYY'))                    
                
st.header(data_slider)

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect('Quais as condições do trânsito',['Low','Medium','High','Jam'],default = ['Low','Medium','High','Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown("### Powered by Comunidade DS")


## Filtro de data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]


## Filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas,:]

st.dataframe(df1)
#--------------------
# layout no streamlit
#--------------------
tab1,tab2,tab3 = st.tabs(['Visão Gerencial','',''])
with tab1:
    with st.container():
        st.title("Overal Metrics")
        col1,col2,col3,col4,col5,col6 = st.columns(6)
        with col1:
            delivery_unique = len(df1.loc[:,'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos',delivery_unique)
        with col2:
            avg_distance = distance(df1,fig = False)
            col2.metric('Distância média', avg_distance)
                                                        
        with col3:
            df_aux = avg_std_time_delivery(df1,'Yes','avg_time')
            col3.metric('Tempo médio de entrega nos festivais', df_aux)

            
        with col4:
            df_aux = avg_std_time_delivery(df1,'Yes','std_time')
            col4.metric('Desvio padrão médio nos festivais', df_aux)
        with col5:
            df_aux = avg_std_time_delivery(df1,'No','avg_time')
            col5.metric('Tempo medio sem festivais', df_aux)
        with col6:
            df_aux = avg_std_time_delivery(df1,'No','std_time')
            col6.metric('Desvio padrão sem festivais', df_aux)
        
    with st.container():
        st.title("Tempo Medio de Entrega por cidade")
        #cols =['Delivery_location_latitude','Delivery_location_longitude','Restaurant_latitude','Restaurant_longitude']
        #df1['distance'] = df1.loc[:,cols].apply(lambda x: haversine((x['Restaurant_latitude'], x['Restaurant_longitude']),(x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        #avg_distance = df1[:,['City','distance']].groupby('City').mean().reset_index()
        #fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0])])
        #st.plotly_chart(fig)
    with st.container():
        st.title("Distribuição do tempo")
        col1,col2 = st.columns(2)
        with col1:
            fig = avg_std_time_graph(df1, fig = True)
            st.plotly_chart(fig)
        with col2:

            fig =avg_std_time_on_traffic(df1, fig = False)
            st.plotly_chart(fig)
    with st.container():
        st.title("Distribuição da Distância")
        df_aux = (df1.loc[:,['City','Time_taken(min)','Type_of_order']].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']}))
        df_aux.columns=['avg_time','std_time']
        df_aux = df_aux.reset_index()
        st.dataframe(df_aux)
        
