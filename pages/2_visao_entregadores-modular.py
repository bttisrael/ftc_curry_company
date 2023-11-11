from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st.set_page_config(page_title = 'Visão Entregadores', layout = 'wide')
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
def top_delivers(df1,top_asc):
    df2 = df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']].groupby(['City','Time_taken(min)']).mean().sort_values(['City','Time_taken(min)'],ascending = top_asc).reset_index()
    df_aux01 = df2.loc[df2['City'] =='Metropolitian',:].head(10)
    df_aux02 = df2.loc[df2['City'] =='Urban',:].head(10)
    df_aux03 = df2.loc[df2['City'] =='Semi-Urban',:].head(10)

    df3 = pd.concat([df_aux01,df_aux02,df_aux03]).reset_index()
    return df3
df1 = clean_code(df)

## LAYOUT STREAMLIT
# BARRA LATERAL
##
st.header('Marketplace - Visão Entregadores')
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
tab1,tab2,tab3 = st.tabs(['Visão Gerencial','Visão Tática','Visão Geográfica'])

with tab1:
    with st.container():
        st.title("Overall metrics")
        col1,col2,col3,col4 = st.columns(4, gap='large')
        with col1:
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior Idade', maior_idade)
        with col2:
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)
        with col3:
            melhor_condicao = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor condição',melhor_condicao)
        with col4:
            pior_condicao = df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Melhor condição',pior_condicao)
            
            
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        col1,col2 = st.columns(2)
        with col1:
            st.markdown('#### Avaliações médias por entregador')
            media_avaliacao_entregador = df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']].groupby('Delivery_person_ID').mean().reset_index()
            st.dataframe(media_avaliacao_entregador)
            
        with col2:
            st.markdown('#### Avaliação média e desvio por trânsito')
            df_avg_traffic=(df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']].groupby('Road_traffic_density').agg({'Delivery_person_Ratings':['mean','std']} ))
            df_avg_traffic.columns = ['delivery_mean','delivery_std']
            df_avg_traffic = df_avg_traffic.reset_index()
            st.dataframe(df_avg_traffic)
            
            st.markdown('#### Avaliação média por clima')

            df_avg_weather=(df1.loc[:,['Delivery_person_Ratings','Weatherconditions']].groupby('Weatherconditions').agg({'Delivery_person_Ratings':['mean','std']} ))
            df_avg_weather.columns = ['delivery_mean','delivery_std']
            df_avg_weather = df_avg_weather.reset_index()
            st.dataframe(df_avg_weather)
    with st.container():
        st.markdown("""---""")
        st.title("Velocidade de entrega")
        col1,col2 =st.columns(2)
        with col1:
            st.markdown("#### Top Entregadores mais rapidos")
            df3 = top_delivers(df1, top_asc = True)
            st.dataframe(df3)
        with col2:
            st.markdown("#### Top Entregadores mais lentos")
            df3 = top_delivers(df1, top_asc = False)
            st.dataframe(df3)

