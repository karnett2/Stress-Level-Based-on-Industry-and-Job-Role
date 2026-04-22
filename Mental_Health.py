import pandas as pd
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

# ------------------------------------------------------------------------------
# 1. Load and Prep Data
# ------------------------------------------------------------------------------
df = pd.read_csv('Impact_of_Remote_Work_on_Mental_Health.csv')

stress_mapping = {'Low': 8, 'Medium': 5.5, 'High': 3}
df['Stress_Score'] = df['Stress_Level'].map(stress_mapping)

# ------------------------------------------------------------------------------
# 2. Initialize Dash App
# ------------------------------------------------------------------------------
app = dash.Dash(__name__, title="Mental Health Dashboard")

# Make cards extremely compact
CARD_STYLE = {
    'boxShadow': '0 2px 5px 0 rgba(0,0,0,0.1)',
    'padding': '8px',
    'margin': '5px',
    'backgroundColor': 'white',
    'borderRadius': '5px'
}

def get_btn_style(is_active):
    base = {'padding': '5px 15px', 'marginRight': '5px', 'borderRadius': '5px', 'cursor': 'pointer', 'border': 'none', 'fontWeight': 'bold', 'transition': '0.2s', 'fontSize': '14px'}
    if is_active:
        return {**base, 'backgroundColor': '#2c3e50', 'color': 'white'}
    return {**base, 'backgroundColor': '#ecf0f1', 'color': '#2c3e50'}

def apply_uniform_font(fig):
    fig.update_layout(
        font=dict(size=11),
        title_font=dict(size=13),
        margin=dict(t=30, l=15, r=15, b=20)
    )
    return fig

def create_side_layout(side_id, title_text, color):
    return html.Div(style={'flex': '1', 'display': 'flex', 'flexDirection': 'column', 'minWidth': '300px', 'overflowY': 'auto', 'padding': '5px'}, children=[
        html.Div(style={**CARD_STYLE, 'marginBottom': '5px'}, children=[
            html.H3(title_text, style={'textAlign': 'center', 'color': color, 'margin': '5px 0', 'fontSize': '18px'}),
            html.H4(id=f'selection-info-{side_id}', style={'textAlign': 'center', 'color': '#34495e', 'margin': '2px', 'fontSize': '14px'}),
        ]),
        
        # Filtering charts (Focal Point)
        html.Div(style={'display': 'flex', 'flexDirection': 'column', 'flex': '0 1 auto', 'marginBottom': '5px', 'gap': '5px'}, children=[
            html.Div(style={**CARD_STYLE, 'flex': '1', 'display': 'flex'}, children=[
                dcc.Graph(id=f'industry-bar-{side_id}', style={'height': '250px', 'flex': '1'})
            ]),
            html.Div(id=f'job-role-container-{side_id}', style={**CARD_STYLE, 'flex': '1', 'display': 'flex'}, children=[
                dcc.Graph(id=f'job-role-bar-{side_id}', style={'height': '250px', 'flex': '1'})
            ])
        ]),
        
        # Details panels grouped
        html.Div(style={'display': 'flex', 'flexDirection': 'row', 'flex': '1'}, children=[
            # Stress, MH, Sleep
            html.Div(style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'}, children=[
                html.Div(style=CARD_STYLE, children=[dcc.Graph(id=f'stress-gauge-{side_id}', style={'height': '150px'})]),
                html.Div(style=CARD_STYLE, children=[dcc.Graph(id=f'mental-health-spectrum-{side_id}', style={'height': '150px'})]),
                html.Div(style=CARD_STYLE, children=[dcc.Graph(id=f'sleep-quality-bar-{side_id}', style={'height': '150px'})]),
            ]),
            # Hours, WLB, Support
            html.Div(style={'flex': '1', 'display': 'flex', 'flexDirection': 'column'}, children=[
                html.Div(style=CARD_STYLE, children=[dcc.Graph(id=f'hours-indicator-{side_id}', style={'height': '150px'})]),
                html.Div(style=CARD_STYLE, children=[dcc.Graph(id=f'wlb-indicator-{side_id}', style={'height': '150px'})]),
                html.Div(style=CARD_STYLE, children=[dcc.Graph(id=f'company-support-bar-{side_id}', style={'height': '150px'})])
            ])
        ])
    ])

app.layout = html.Div(
    style={'fontFamily': 'Arial, sans-serif', 'backgroundColor': '#f4f6f9', 'padding': '10px', 'height': '98vh', 'display': 'flex', 'flexDirection': 'column'},
    children=[
        # Hidden store for location state tracking
        dcc.Store(id='loc-store', data='All'),

        html.H2("Mental Health & Remote Work Gender Dashboard", style={'textAlign': 'center', 'color': '#2c3e50', 'margin': '5px', 'fontSize': '22px'}),

        # ── Row 1: Controls (Location Filter Buttons & Reset) ──
        html.Div(style={**CARD_STYLE, 'display': 'flex', 'justifyContent': 'space-between', 'alignItems': 'center', 'padding': '8px 15px', 'flex': '0 1 auto'}, children=[
            html.Div(style={'display': 'flex', 'alignItems': 'center'}, children=[
                html.Span("Global Work Location Filter: ", style={'fontWeight': 'bold', 'marginRight': '10px', 'fontSize': '14px'}),
                html.Button("All Locations", id="btn-all", n_clicks=0, style=get_btn_style(True)),
                html.Button("Remote", id="btn-remote", n_clicks=0, style=get_btn_style(False)),
                html.Button("Hybrid", id="btn-hybrid", n_clicks=0, style=get_btn_style(False)),
                html.Button("Onsite", id="btn-onsite", n_clicks=0, style=get_btn_style(False))
            ]),
            html.Button("Reset All Filters", id="reset-btn", style={
                'padding': '5px 15px', 'backgroundColor': '#e74c3c', 
                'color': 'white', 'border': 'none', 'borderRadius': '5px', 'cursor': 'pointer',
                'fontWeight': 'bold', 'fontSize': '14px'
            })
        ]),

        # ── Row 2: Split Dashboard Layout ──
        html.Div(style={'display': 'flex', 'flexDirection': 'row', 'flex': '1', 'minHeight': '0'}, children=[
            create_side_layout('m', '👨 Male Workforce Data', '#2980b9'),
            create_side_layout('f', '👩 Female Workforce Data', '#e84393'),
        ])
    ]
)

# ------------------------------------------------------------------------------
# 3. Callbacks for Interactivity
# ------------------------------------------------------------------------------

# Callback 1: Location Filter Button Tracking
@app.callback(
    [Output('btn-all', 'style'), Output('btn-remote', 'style'), Output('btn-hybrid', 'style'), Output('btn-onsite', 'style'), Output('loc-store', 'data')],
    [Input('btn-all', 'n_clicks'), Input('btn-remote', 'n_clicks'), Input('btn-hybrid', 'n_clicks'), Input('btn-onsite', 'n_clicks'), Input('reset-btn', 'n_clicks')],
    State('loc-store', 'data')
)
def update_loc_buttons(n_a, n_r, n_h, n_o, n_reset, current_loc):
    ctx = dash.callback_context
    loc = current_loc or 'All'
    
    if ctx.triggered:
        btn_id = ctx.triggered[0]['prop_id'].split('.')[0]
        if btn_id == 'btn-remote': loc = 'Remote'
        elif btn_id == 'btn-hybrid': loc = 'Hybrid'
        elif btn_id == 'btn-onsite': loc = 'Onsite'
        elif btn_id == 'btn-all' or btn_id == 'reset-btn': loc = 'All'
        
    return get_btn_style(loc == 'All'), get_btn_style(loc == 'Remote'), get_btn_style(loc == 'Hybrid'), get_btn_style(loc == 'Onsite'), loc

# Callback 2: Resetting Chart Clicks for Both Sides
@app.callback(
    [Output('industry-bar-m', 'clickData'), Output('job-role-bar-m', 'clickData'),
     Output('industry-bar-f', 'clickData'), Output('job-role-bar-f', 'clickData')],
    [Input('reset-btn', 'n_clicks')],
    prevent_initial_call=True
)
def reset_clicks(n):
    return None, None, None, None

# Generative main Callback for Each Side independently
def register_side_callback(side_id, gender):
    @app.callback(
        [Output(f'industry-bar-{side_id}', 'figure'),
         Output(f'job-role-container-{side_id}', 'style'),
         Output(f'job-role-bar-{side_id}', 'figure'),
         Output(f'selection-info-{side_id}', 'children'),
         Output(f'stress-gauge-{side_id}', 'figure'),
         Output(f'hours-indicator-{side_id}', 'figure'),
         Output(f'sleep-quality-bar-{side_id}', 'figure'),
         Output(f'company-support-bar-{side_id}', 'figure'),
         Output(f'mental-health-spectrum-{side_id}', 'figure'),
         Output(f'wlb-indicator-{side_id}', 'figure')],
        [Input(f'industry-bar-{side_id}', 'clickData'),
         Input(f'job-role-bar-{side_id}', 'clickData'),
         Input('loc-store', 'data')]
    )
    def update_side(ind_click, role_click, loc_filter):
        # 1. Base filter by Gender and Global Location
        base_df = df[df['Gender'] == gender]
        loc_filter = loc_filter or 'All'
        if loc_filter != 'All':
            base_df = base_df[base_df['Work_Location'] == loc_filter]

        # 2. Local Side parsing
        selected_industry = ind_click['points'][0].get('x') if ind_click and 'points' in ind_click else None
        selected_role = role_click['points'][0].get('x') if role_click and 'points' in role_click else None

        if selected_industry and selected_role:
            valid_roles = base_df[base_df['Industry'] == selected_industry]['Job_Role'].unique()
            if selected_role not in valid_roles:
                selected_role = None

        filtered_df = base_df.copy()
        if selected_industry: filtered_df = filtered_df[filtered_df['Industry'] == selected_industry]
        if selected_role: filtered_df = filtered_df[filtered_df['Job_Role'] == selected_role]

        # 3. Status text
        loc_text = f" ({loc_filter})" if loc_filter != 'All' else ""
        selection_text = f"Context: All {gender}s{loc_text}"
        if selected_industry and selected_role:
            selection_text = f"Context: {selected_role}s in {selected_industry} ({gender})"
        elif selected_industry:
            selection_text = f"Context: {selected_industry} Industry ({gender})"

        if filtered_df.empty:
            filtered_df = base_df.copy()
            selection_text += " [No Data - Baseline]"

        # 4. Industry Chart
        ind_stress = base_df.groupby('Industry')['Stress_Score'].mean().reset_index()
        fig_ind = px.bar(ind_stress, x='Industry', y='Stress_Score', title='Avg Stress by Industry', labels={'Stress_Score': 'Stress Level'})
        if selected_industry:
            colors = ['rgba(52,152,219,1)' if ind == selected_industry else 'rgba(190,190,190,0.5)' for ind in ind_stress['Industry']]
            fig_ind.update_traces(marker_color=colors)
        else:
            fig_ind.update_traces(marker_color='rgba(52,152,219,0.8)')
        fig_ind = apply_uniform_font(fig_ind)
        fig_ind.update_xaxes(title="", tickangle=45)
        fig_ind.update_layout(margin=dict(b=90))

        # 5. Role Chart
        job_role_style = {**CARD_STYLE, 'flex': '1', 'display': 'flex'}
        fig_role = go.Figure()
        if selected_industry:
            role_df = base_df[base_df['Industry'] == selected_industry]
            role_stress = role_df.groupby('Job_Role')['Stress_Score'].mean().reset_index()
            fig_role = px.bar(role_stress, x='Job_Role', y='Stress_Score', title=f'{selected_industry} Roles', labels={'Job_Role': 'Job Rules', 'Stress_Score': 'Stress Level'})
            if selected_role:
                colors = ['rgba(46,204,113,1)' if role == selected_role else 'rgba(190,190,190,0.5)' for role in role_stress['Job_Role']]
                fig_role.update_traces(marker_color=colors)
            else:
                fig_role.update_traces(marker_color='rgba(46,204,113,0.8)')
        else:
            # Render empty block with instructions when no industry is selected
            fig_role = go.Figure().add_annotation(text="Select an Industry first to see Roles", showarrow=False, font={"size":13, "color":"#7f8c8d"})
            fig_role.update_xaxes(visible=False).update_yaxes(visible=False)
            fig_role.update_layout(title='Avg Stress by Role')
            
        fig_role = apply_uniform_font(fig_role)
        fig_role.update_xaxes(title="", tickangle=45)
        fig_role.update_layout(margin=dict(b=90))

        # 6. Stress Gauge
        avg_stress = filtered_df['Stress_Score'].mean()
        stress_color, stress_text = ("red", "Bad") if avg_stress >= 7 else ("gold", "Mod") if avg_stress >= 4.5 else ("green", "Good")
        fig_stress = go.Figure(go.Indicator(
            mode="gauge+number", value=avg_stress, number={'valueformat': '.1f', 'font': {'size': 28}},
            gauge={'axis': {'range': [0, 10]}, 'bar': {'color': stress_color, 'thickness': 0.7}, 'steps': [{'range': [0, 4.5], 'color': '#d4edda'}, {'range': [4.5, 7], 'color': '#fffacd'}, {'range': [7, 10], 'color': '#ffcccb'}]}
        ))
        fig_stress = apply_uniform_font(fig_stress)
        fig_stress.update_layout(title_text=f"Average Stress Gauge", margin=dict(t=40, l=35, r=35, b=15))

        # 7. Hours
        avg_hours = filtered_df['Hours_Worked_Per_Week'].mean()
        fig_hours = go.Figure(go.Indicator(
            mode="number", value=avg_hours, number={'valueformat': '.1f', 'suffix': ' h', 'font': {'size': 28}}, title={'text': "Avg Hours", 'font': {'size': 14}}
        ))
        fig_hours = apply_uniform_font(fig_hours)
        fig_hours.update_layout(margin=dict(t=25, l=15, r=15, b=0))

        # 8. Sleep Quality
        sleep_counts = filtered_df['Sleep_Quality'].value_counts().reset_index()
        sleep_counts.columns = ['Sleep_Quality', 'Count']
        sleep_color_map = {'Good': '#2ecc71', 'Average': '#f1c40f', 'Poor': '#e74c3c'}
        fig_sleep = px.bar(sleep_counts, x='Sleep_Quality', y='Count', title='Sleep Quality', color='Sleep_Quality', color_discrete_map=sleep_color_map)
        fig_sleep = apply_uniform_font(fig_sleep)
        fig_sleep.update_layout(showlegend=False)
        fig_sleep.update_xaxes(title="")

        # 9. Company Support
        support_counts = filtered_df['Company_Support_for_Remote_Work'].value_counts().reset_index()
        support_counts.columns = ['Support_Level', 'Count']
        support_counts['Support_Level'] = support_counts['Support_Level'].astype(str)
        support_counts = support_counts.sort_values(by='Support_Level')
        support_color_map = {'1': '#e74c3c', '2': '#e67e22', '3': '#f1c40f', '4': '#27ae60', '5': '#2ecc71', '1.0': '#e74c3c', '2.0': '#e67e22', '3.0': '#f1c40f', '4.0': '#27ae60', '5.0': '#2ecc71'}
        fig_support = px.bar(support_counts, y='Support_Level', x='Count', orientation='h', title='Company Support', color='Support_Level', color_discrete_map=support_color_map)
        fig_support = apply_uniform_font(fig_support)
        fig_support.update_layout(showlegend=False, yaxis_title="Support")

        # 10. Mental Health Spec
        mh_counts = filtered_df['Mental_Health_Condition'].value_counts(normalize=True).reset_index()
        mh_counts.columns = ['Condition', 'Percentage']
        mh_counts['Percentage'] = mh_counts['Percentage'] * 100
        mh_counts['Spectrum'] = 'Ratio'
        mh_counts['Label'] = mh_counts['Percentage'].apply(lambda x: f"{x:.1f}%" if x > 2 else "")
        mh_color_map = {'Depression': '#8e44ad', 'Anxiety': '#8b4513', 'Burnout': '#bdc3c7', 'None': '#3498db'}
        fig_mh = px.bar(mh_counts, x='Percentage', y='Spectrum', color='Condition', orientation='h', barmode='stack', text='Label', color_discrete_map=mh_color_map)
        fig_mh = apply_uniform_font(fig_mh)
        fig_mh.update_xaxes(title="")
        fig_mh.update_yaxes(showticklabels=False, title="")
        fig_mh.update_layout(margin=dict(t=15, l=10, r=10, b=55), showlegend=True, legend=dict(orientation="h", yanchor="top", y=-0.35, xanchor="center", x=0.5, title=""))

        # 11. Work Life Balance
        avg_wlb = filtered_df['Work_Life_Balance_Rating'].mean() if not filtered_df.empty else 0
        fig_wlb = go.Figure(go.Indicator(
            mode="number", value=avg_wlb, number={'valueformat': '.1f', 'suffix': ' / 5', 'font': {'size': 28}}, title={'text': "Work Life Balance", 'font': {'size': 14}}
        ))
        fig_wlb = apply_uniform_font(fig_wlb)
        fig_wlb.update_layout(margin=dict(t=25, l=15, r=15, b=0))

        return (fig_ind, job_role_style, fig_role, selection_text, fig_stress, fig_hours, fig_sleep, fig_support, fig_mh, fig_wlb)

# Register independent side callbacks
register_side_callback('m', 'Male')
register_side_callback('f', 'Female')

if __name__ == '__main__':
    print("Starting dashboard... Open http://127.0.0.1:8051/ in your browser.")
    app.run(debug=True, port=8051)