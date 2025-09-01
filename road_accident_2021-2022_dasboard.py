import dash
import dash_bootstrap_components as dbc
from dash import dcc, html
from dash.dependencies import Input, Output
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# สีที่ใช้ในธีม
COLORS = {
    'background': '#f9f9f9',
    'text': '#333333',
    'primary': '#1f77b4',
    'secondary': '#ff7f0e',
    'accent': '#2ca02c',
    'grid': '#e1e1e1',
}

# โหลดข้อมูล
file_path_2022 = 'accident2022.csv'
file_path_2021 = 'accident2021.csv'

# อ่านข้อมูลทั้งสองปี
data_2022 = pd.read_csv(file_path_2022)
data_2021 = pd.read_csv(file_path_2021)

# เพิ่มคอลัมน์ปีเพื่อระบุที่มาของข้อมูล
data_2022['ปีที่บันทึก'] = 2022
data_2021['ปีที่บันทึก'] = 2021

# รวมข้อมูล
all_data = pd.concat([data_2021, data_2022], ignore_index=True)

# ประมวลผลข้อมูลเบื้องต้น
all_data['วันที่เกิดเหตุ'] = pd.to_datetime(all_data['วันที่เกิดเหตุ'], format='%d/%m/%Y', errors='coerce')
all_data.dropna(subset=['วันที่เกิดเหตุ'], inplace=True)
all_data['ปี'] = all_data['วันที่เกิดเหตุ'].dt.year
all_data['เดือน'] = all_data['วันที่เกิดเหตุ'].dt.month_name()

# สร้างแอป Dash พร้อม Theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])
app.title = "Road Accident Dashboard 2021-2022"

# Layout ของ Dashboard
app.layout = dbc.Container([
    # Header
    dbc.Row([
        dbc.Col(html.H1("🚗 Road Accident Analytics Dashboard 2021-2022", 
                        className="text-center text-primary my-4"), 
                width=12)
    ]),

    # Control Panel
    dbc.Row([
        dbc.Col([
            html.Label("เลือกสถิติที่ต้องการ:", className="fw-bold"),
            dcc.Dropdown(
                id='statistic-dropdown',
                options=[
                    {'label': 'จำนวนอุบัติเหตุทั้งหมด', 'value': 'ACC_CODE'},
                    {'label': 'จำนวนผู้เสียชีวิต', 'value': 'ผู้เสียชีวิต'},
                    {'label': 'จำนวนผู้บาดเจ็บสาหัส', 'value': 'ผู้บาดเจ็บสาหัส'},
                    {'label': 'จำนวนผู้บาดเจ็บเล็กน้อย', 'value': 'ผู้บาดเจ็บเล็กน้อย'},
                    {'label': 'จำนวนผู้บาดเจ็บรวม', 'value': 'รวมจำนวนผู้บาดเจ็บ'}
                ],
                value='ACC_CODE',
                clearable=False,
                className="mb-3",
                style={'color': 'black'}
            )
        ], width=6, lg=6),
        
        dbc.Col([
            html.Label("เลือกจังหวัด:", className="fw-bold"),
            dcc.Dropdown(
                id='province-dropdown',
                options=[{'label': province, 'value': province} for province in sorted(all_data['จังหวัด'].dropna().unique())],
                value=None,
                multi=True,
                placeholder="เลือกจังหวัดที่ต้องการ (หากไม่เลือกจะแสดงทุกจังหวัด)",
                className="mb-3",
                style={'color': 'black'}
            )
        ], width=6, lg=6)
    ]),

    # Graphs Grid
    dbc.Row([
        dbc.Col(dcc.Graph(id='monthly-trend-graph'), width=12, lg=12),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='accident-type-pie'), width=6, lg=6),
        dbc.Col(dcc.Graph(id='province-accidents-pie'), width=6, lg=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='fatalities-by-province-bar'), width=6, lg=6),
        dbc.Col(dcc.Graph(id='injuries-by-province-bar'), width=6, lg=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='time-of-day-heatmap'), width=12, lg=12),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='vehicle-type-bar'), width=6, lg=6),
        dbc.Col(dcc.Graph(id='weather-condition-pie'), width=6, lg=6),
    ], className="mb-4"),

    dbc.Row([
        dbc.Col(dcc.Graph(id='severity-distribution-histogram'), width=6, lg=6),
        dbc.Col(dcc.Graph(id='daily-accidents-line'), width=6, lg=6),
    ], className="mb-4"),

], fluid=True)

layout_defaults = {
    'plot_bgcolor': COLORS['background'],
    'paper_bgcolor': COLORS['background'],
    'font': {'color': COLORS['text']},
    'title': {
        'font': {'size': 16, 'color': COLORS['primary']},
        'x': 0.5,
        'xanchor': 'center'
    },
    'xaxis': {
        'gridcolor': COLORS['grid'],
        'zerolinecolor': COLORS['grid'],
        'title': {'font': {'color': COLORS['text']}},
        'tickfont': {'color': COLORS['text']}
    },
    'yaxis': {
        'gridcolor': COLORS['grid'],
        'zerolinecolor': COLORS['grid'],
        'title': {'font': {'color': COLORS['text']}},
        'tickfont': {'color': COLORS['text']}
    }
}

@app.callback(
    [
        Output('monthly-trend-graph', 'figure'),
        Output('accident-type-pie', 'figure'),
        Output('fatalities-by-province-bar', 'figure'),
        Output('injuries-by-province-bar', 'figure'),
        Output('time-of-day-heatmap', 'figure'),
        Output('vehicle-type-bar', 'figure'),
        Output('weather-condition-pie', 'figure'),
        Output('severity-distribution-histogram', 'figure'),
        Output('daily-accidents-line', 'figure'),
        Output('province-accidents-pie', 'figure')
    ],
    [
        Input('statistic-dropdown', 'value'),
        Input('province-dropdown', 'value')
    ]
)
def update_graphs(statistic, provinces):
    filtered_data = all_data.copy()
    if provinces:
        filtered_data = filtered_data[filtered_data['จังหวัด'].isin(provinces)]
    
    title_suffix = ""
    if provinces:
        if len(provinces) <= 3:
            title_suffix = f" - จังหวัด {''.join(provinces)}"
        else:
            title_suffix = f" - {len(provinces)} จังหวัด"
    
    stat_labels = {
        'ACC_CODE': 'จำนวนอุบัติเหตุ',
        'ผู้เสียชีวิต': 'จำนวนผู้เสียชีวิต',
        'ผู้บาดเจ็บสาหัส': 'จำนวนผู้บาดเจ็บสาหัส',
        'ผู้บาดเจ็บเล็กน้อย': 'จำนวนผู้บาดเจ็บเล็กน้อย',
        'รวมจำนวนผู้บาดเจ็บ': 'จำนวนผู้บาดเจ็บรวม'
    }
    
    # คัดลอกมาวางทั้งหมด ทำเหมือนเดิมทุกประการ
    
    monthly_data = filtered_data.groupby(['ปี', 'เดือน'])[statistic].sum().reset_index()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June', 
                  'July', 'August', 'September', 'October', 'November', 'December']
    monthly_data['เดือน'] = pd.Categorical(monthly_data['เดือน'], categories=month_order, ordered=True)
    monthly_data = monthly_data.sort_values('เดือน')
    
    # ปรับขนาดข้อมูล: แสดงหน่วยเป็นพันครั้ง
    monthly_data[statistic] = monthly_data[statistic] / 1000  

    # แสดงเส้นแยกตามปี
    trend_fig = px.line(
        monthly_data,
        x='เดือน',
        y=statistic,
        color='ปี',
        title=f"แนวโน้ม{stat_labels[statistic]}รายเดือน{title_suffix}",
        labels={'เดือน': 'เดือน', statistic: stat_labels[statistic], 'ปี': 'ปี'},
        color_discrete_map={2021: COLORS['primary'], 2022: COLORS['secondary']}
    )

    # ปรับให้เส้นมีความโปร่งใส และเปลี่ยนบางเส้นเป็นเส้นประ
    for i, trace in enumerate(trend_fig.data):
        trace.opacity = 0.7  # ลดความทึบของเส้น
        if i % 2 == 1:
            trace.line.dash = 'dash'  # ให้เส้นปี 2022 เป็นเส้นประ

    # ปรับขนาดแกน Y ให้อยู่ในช่วงที่เหมาะสม
    trend_fig.update_yaxes(range=[0, monthly_data[statistic].max() * 1.1])

    
    accident_types = filtered_data['ลักษณะการเกิดเหตุ'].value_counts().nlargest(10).reset_index()
    accident_types.columns = ['ลักษณะการเกิดเหตุ', 'จำนวน']
    
    pie_fig = px.pie(
        accident_types, 
        names='ลักษณะการเกิดเหตุ', 
        values='จำนวน', 
        title=f"ลักษณะการเกิดเหตุ{title_suffix}",
        color_discrete_sequence=px.colors.qualitative.Set3
    )
    pie_fig.update_traces(textposition='inside', textinfo='percent+label')
    
    
    fatalities_data = filtered_data.groupby('จังหวัด')['ผู้เสียชีวิต'].sum().reset_index()
    fatalities_data = fatalities_data.sort_values('ผู้เสียชีวิต', ascending=False).head(10)
    
    fatalities_fig = px.bar(
        fatalities_data, 
        x='จังหวัด', 
        y='ผู้เสียชีวิต', 
        title=f"อันดับจังหวัดที่มีผู้เสียชีวิตสูงสุด 10 อันดับ{title_suffix}",
        labels={'จังหวัด': 'จังหวัด', 'ผู้เสียชีวิต': 'จำนวนผู้เสียชีวิต'},
        color='ผู้เสียชีวิต',
        color_continuous_scale='Reds'
    )
    
    
    injuries_data = filtered_data.groupby('จังหวัด')['รวมจำนวนผู้บาดเจ็บ'].sum().reset_index()
    injuries_data = injuries_data.sort_values('รวมจำนวนผู้บาดเจ็บ', ascending=False).head(10)
    
    injuries_fig = px.bar(
        injuries_data, 
        x='จังหวัด', 
        y='รวมจำนวนผู้บาดเจ็บ', 
        title=f"อันดับจังหวัดที่มีผู้บาดเจ็บสูงสุด 10 อันดับ{title_suffix}",
        labels={'จังหวัด': 'จังหวัด', 'รวมจำนวนผู้บาดเจ็บ': 'จำนวนผู้บาดเจ็บ'},
        color='รวมจำนวนผู้บาดเจ็บ',
        color_continuous_scale='Blues'
    )
    
    
    try:
        filtered_data['ชั่วโมง'] = pd.to_datetime(filtered_data['เวลา'], format='%H:%M', errors='coerce').dt.hour
        time_data = filtered_data.groupby(['ชั่วโมง', 'เดือน']).size().reset_index(name='จำนวน')
        time_data['เดือน'] = pd.Categorical(time_data['เดือน'], categories=month_order, ordered=True)
        time_data = time_data.sort_values('เดือน')
        
        heatmap_fig = px.density_heatmap(
            time_data, 
            x='เดือน', 
            y='ชั่วโมง', 
            z='จำนวน',
            title=f"ช่วงเวลาที่เกิดอุบัติเหตุตามเดือน{title_suffix}",
            labels={'เดือน': 'เดือน', 'ชั่วโมง': 'ช่วงเวลา (ชั่วโมง)', 'จำนวน': 'จำนวนอุบัติเหตุ'},
            color_continuous_scale='Viridis'
        )
        heatmap_fig.update_layout(**layout_defaults)
        
    except Exception as e:
        # สร้างแผนภาพเปล่าในกรณีที่มีข้อผิดพลาด
        heatmap_fig = go.Figure()
        heatmap_fig.add_annotation(
            text=f"ไม่สามารถแสดงข้อมูลได้: {str(e)}",
            showarrow=False,
            font=dict(size=14)
        )
    
    
    vehicle_cols = ['รถจักรยานยนต์', 'รถยนต์นั่งส่วนบุคคล', 'รถปิคอัพบรรทุก4ล้อ', 'รถบรรทุก6ล้อ', 'รถอื่นๆ']
    vehicle_data = filtered_data[vehicle_cols].sum().reset_index()
    vehicle_data.columns = ['ประเภทยานพาหนะ', 'จำนวน']
    vehicle_mapping = {
        'รถจักรยานยนต์': 'รถจักรยานยนต์',
        'รถยนต์นั่งส่วนบุคคล': 'รถยนต์นั่งส่วนบุคคล',
        'รถปิคอัพบรรทุก4ล้อ': 'รถปิคอัพ 4 ล้อ',
        'รถบรรทุก6ล้อ': 'รถบรรทุก 6 ล้อ',
        'รถอื่นๆ': 'ยานพาหนะอื่นๆ'
    }
    vehicle_data['ประเภทยานพาหนะ'] = vehicle_data['ประเภทยานพาหนะ'].map(vehicle_mapping)
    vehicle_data = vehicle_data.sort_values('จำนวน', ascending=False)
    
    vehicle_fig = px.bar(
        vehicle_data, 
        x='ประเภทยานพาหนะ', 
        y='จำนวน', 
        title=f"ประเภทยานพาหนะที่เกี่ยวข้องกับอุบัติเหตุ{title_suffix}",
        color='จำนวน',
        color_continuous_scale='Greens'
    )
    
    weather_data = filtered_data['สภาพอากาศ'].value_counts().reset_index()
    weather_data.columns = ['สภาพอากาศ', 'จำนวน']
    
    weather_fig = px.pie(
        weather_data, 
        names='สภาพอากาศ', 
        values='จำนวน', 
        title=f"สภาพอากาศขณะเกิดอุบัติเหตุ{title_suffix}",
        color_discrete_sequence=px.colors.qualitative.Pastel
    )
    weather_fig.update_traces(textposition='inside', textinfo='percent+label')
    
    severity_data = pd.DataFrame({
        'ระดับความรุนแรง': ['เสียชีวิต', 'บาดเจ็บสาหัส', 'บาดเจ็บเล็กน้อย'],
        'จำนวน': [
            filtered_data['ผู้เสียชีวิต'].sum(),
            filtered_data['ผู้บาดเจ็บสาหัส'].sum(),
            filtered_data['ผู้บาดเจ็บเล็กน้อย'].sum()
        ]
    })
    
    severity_fig = px.bar(
        severity_data, 
        x='ระดับความรุนแรง', 
        y='จำนวน', 
        title=f"ระดับความรุนแรงของอุบัติเหตุ{title_suffix}",
        color='ระดับความรุนแรง',
        color_discrete_map={
            'เสียชีวิต': '#ff7f7f',
            'บาดเจ็บสาหัส': '#ffbf7f',
            'บาดเจ็บเล็กน้อย': '#ffff7f'
        }
    )
    
    daily_data = filtered_data.groupby('วันที่เกิดเหตุ').size().reset_index(name='จำนวนอุบัติเหตุ')
    daily_data = daily_data.sort_values('วันที่เกิดเหตุ')
    
    daily_line_fig = px.line(
        daily_data, 
        x='วันที่เกิดเหตุ', 
        y='จำนวนอุบัติเหตุ', 
        title=f"จำนวนอุบัติเหตุรายวัน{title_suffix}",
        labels={'วันที่เกิดเหตุ': 'วันที่', 'จำนวนอุบัติเหตุ': 'จำนวนอุบัติเหตุ'}
    )
    daily_line_fig.update_traces(line=dict(width=2, color=COLORS['accent']))
    
    province_data = filtered_data['จังหวัด'].value_counts().nlargest(10).reset_index()
    province_data.columns = ['จังหวัด', 'จำนวน']
    
    province_pie_fig = px.pie(
        province_data, 
        names='จังหวัด', 
        values='จำนวน', 
        title=f"10 จังหวัดที่มีอุบัติเหตุสูงสุด{title_suffix}",
        color_discrete_sequence=px.colors.qualitative.Pastel1
    )
    province_pie_fig.update_traces(textposition='inside', textinfo='percent+label')

    return (
        trend_fig, pie_fig, fatalities_fig, injuries_fig, heatmap_fig, 
        vehicle_fig, weather_fig, severity_fig, daily_line_fig, province_pie_fig
    )

if __name__ == '__main__':
    app.run(debug=True)
