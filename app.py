from shiny import App, ui, render, reactive
from datetime import datetime, timezone
import pandas as pd
import plotnine as p9

TIMEZONE = timezone.utc

color_map = {
    0: "#812EBB",  # Primária
    1: "#D03384",  # Secundária
    2: "#2DBE82",  # Verde esmeralda
    3: "#2CAAD6",  # Azul turquesa
    4: "#F4B93C",  # Amarelo dourado
    5: "#E85C4A",  # Vermelho coral
}
cor_completude_map = {
    "0-20%":  color_map[5],
    "20-40%": color_map[4],
    "40-60%": color_map[3],
    "60-80%": color_map[2],
    "80-100%": color_map[1]   # equivalente ao else da função
}

teachers = pd.read_parquet("data/teachers.parquet")
faixas_completude = teachers['faixa_completude'].unique().tolist()
faixas_completude.sort()

interactions = pd.read_parquet("data/teachers_interactions.parquet")
interactions['data_inicio'] = pd.to_datetime(interactions['data_inicio'])


icon_teacher = '<img src="https://github.com/guifidalgo/aprendizap/blob/main/assets/teacher_white.png?raw=true" alt="Professor" width="50" height="50">'
icon_student = '<img src="https://github.com/guifidalgo/aprendizap/blob/main/assets/student_white.png?raw=true" alt="Aluno" width="50" height="50">'
icon_interaction = '<img src="https://github.com/guifidalgo/aprendizap/blob/main/assets/interaction_white.png?raw=true" alt="Interação" width="50" height="50">'


app_ui = ui.page_sidebar(
    ui.sidebar(
        "Filtros",
        ui.input_switch(
            'switch_valid',
            'Apenas Usuários Válidos',
            value=False
            ),
        ui.input_selectize(
            'select_completude',
            'Selecione as faixas de completude do cadastro',
            choices=faixas_completude,
            multiple=True,
            selected=faixas_completude,  # Seleciona todas as faixas por padrão
        ),
        ui.input_slider(
            "slider_date",
            label="Data de Cadastro:",
            min=teachers['data_entrada'].min(),
            max=teachers['data_entrada'].max(),
            value=(teachers['data_entrada'].min(), teachers['data_entrada'].max()),
            time_format="%m/%Y",
        ),
        ui.input_slider(
            "slider_interacoes",
            label="Data de Interações:",
            min=interactions['data_inicio'].min(),
            max=interactions['data_inicio'].max(),
            value=(interactions['data_inicio'].min(), interactions['data_inicio'].max()),
            time_format="%m/%Y",
        ),
        bg="#f8f8f8"
    ),
    ui.layout_columns(
        ui.value_box(
            "Professores",
            ui.output_text("qtd_professores"),
            showcase=ui.HTML(icon_teacher),
            theme=ui.value_box_theme('aprendizap', bg=color_map[0], fg="white")
        ),
        ui.value_box(
            "Média de Alunos por Professor",
            ui.output_text("media_alunos_por_professor"),
            showcase=ui.HTML(icon_student),
            theme=ui.value_box_theme('aprendizap3', bg=color_map[2], fg="white")
        ),
        ui.value_box(
            "Interações de Professores",
            ui.output_text("qtd_interacoes"),
            showcase=ui.HTML(icon_interaction),
            theme=ui.value_box_theme('aprendizap2', bg=color_map[1], fg="white")
        ),
        ui.card(
            ui.card_header("Cadastro de Professores"),
            ui.card_body(
                ui.output_plot("plot_cadastros")
            )
        ),
        ui.card(
            ui.card_header("Professores por Estado"),
            ui.card_body(
                ui.output_plot("plot_professores_estado")
            )
        ),
        ui.card(
            ui.card_header("UTM Origem"),
            ui.card_body(
                ui.output_plot("plot_utm_origem")
            )
        ),
        # ui.card(
        #     ui.card_header("Interações por Data de Entrada"),
        #     ui.card_body(
        #         ui.output_plot("plot_interacoes_data_entrada")
        #     )
        # ),
        ui.card(
            ui.card_header("Interações ao Longo do Tempo"),
            ui.card_body(
                ui.output_plot("plot_interacoes_data_inicio")
            )
        ),
        col_widths=[3, 3, 3, 12, 6, 6, 12]
    ),
    title="AprendiZAP - Grupo 01",
)



def server(input, output, session):
    @reactive.calc
    def teachers_filtrado():
        start_date = pd.to_datetime(input.slider_date()[0]).tz_localize(TIMEZONE)
        end_date = pd.to_datetime(input.slider_date()[1]).tz_localize(TIMEZONE)
        if input.switch_valid():
            df = teachers[teachers['usuario_valido'] == True]
        else:
            df = teachers
        return df[
            (df['data_entrada'] >= start_date) &
            (df['data_entrada'] <= end_date) &
            (df['faixa_completude'].isin(input.select_completude()))
            ]
    
    @reactive.calc
    def interactions_filtrado():
        start_date = pd.to_datetime(input.slider_interacoes()[0]).tz_localize(TIMEZONE)
        end_date = pd.to_datetime(input.slider_interacoes()[1]).tz_localize(TIMEZONE)
        if input.switch_valid():
            df = interactions[interactions['usuario_valido'] == True]
        else:
            df = interactions
        return df[
            (df['data_inicio'] >= start_date) &
            (df['data_inicio'] <= end_date) &
            (df['faixa_completude'].isin(input.select_completude()))
        ]


    @render.text
    def qtd_professores():
        return f"{teachers_filtrado().shape[0]:,d}"
    
    @render.text
    def qtd_interacoes():
        df = interactions_filtrado()
        return f"{df['unique_id'].count():,.0f}"
    
    @render.text
    def media_alunos_por_professor():
        df = teachers_filtrado()
        return f"{df['total_alunos'].mean():,.2f}"

    @render.plot
    def plot_cadastros():
        df = teachers_filtrado()
        semanais = df.groupby(['data_semana_entrada']).size().reset_index(name='cadastros_count')
        semanais['data_semana_entrada'] = pd.to_datetime(semanais['data_semana_entrada'])
        plot = (
            p9.ggplot(semanais, p9.aes(x='data_semana_entrada', y='cadastros_count')) +
            p9.geom_area(fill=color_map[0], alpha=0.5) +
            p9.geom_line(color=color_map[0]) +
            p9.labs(
                x='Data de Entrada (Semana)',
                y='Número de Cadastros'
            ) +
            p9.theme_minimal()
        )
        return plot
    
    @render.plot
    def plot_professores_estado():
        df = teachers_filtrado()
        # df['estado'] = df['estado'].fillna('Não Informado')
        estado_counts = df['estado'].value_counts().reset_index()
        estado_counts['estado'] = pd.Categorical(
            estado_counts['estado'],
            categories=estado_counts['estado'][::-1],
            ordered=True
        )
        estado_counts.columns = ['estado', 'professores_count']
        # Ordena os estados por quantidade de professores de forma decrescente
        estado_counts = estado_counts.sort_values('professores_count', ascending=False)
        plot = (
            p9.ggplot(estado_counts, p9.aes(x='estado', y='professores_count')) +
            p9.geom_bar(stat='identity', fill=color_map[0]) +
            p9.labs(
                x='',
                y='Número de Professores'
            ) +
            p9.theme_minimal() +
            p9.coord_flip()
        )
        return plot
    
    @render.plot
    def plot_utm_origem():
        df = teachers_filtrado()
        utm_counts = df['utm_origin'].value_counts().reset_index()
        utm_counts['utm_origin'] = pd.Categorical(
            utm_counts['utm_origin'],
            categories=utm_counts['utm_origin'][::-1],
            ordered=True
        )
        utm_counts.columns = ['utm_origin', 'professores_count']
        # Ordena os UTM por quantidade de professores de forma decrescente
        utm_counts = utm_counts.sort_values('professores_count', ascending=False)
        plot = (
            p9.ggplot(utm_counts, p9.aes(x='utm_origin', y='professores_count')) +
            p9.geom_bar(stat='identity', fill=color_map[0]) +
            p9.labs(
                x='',
                y='Número de Professores'
            ) +
            p9.theme_minimal() +
            p9.coord_flip()
        )
        return plot
    
    @render.plot
    def plot_interacoes_data_entrada():
        df = teachers_filtrado()
        interacoes_data = df.groupby(['data_semana_entrada', 'faixa_completude']).agg({'interactions_count': 'sum'}).reset_index()
        interacoes_data['data_semana_entrada'] = pd.to_datetime(interacoes_data['data_semana_entrada'])
        plot = (
            p9.ggplot(interacoes_data, p9.aes(x='data_semana_entrada', y='interactions_count', fill='faixa_completude')) +
            p9.geom_area(position='stack', alpha=0.5) +
            p9.scale_fill_manual(values=cor_completude_map) +
            p9.labs(
                x='Data de Entrada',
                y='Número de Interações',
                fill='Faixa de Completude'
            ) +
            p9.theme_minimal()
        )
        return plot
    
    @render.plot
    def plot_interacoes_data_inicio():
        df = interactions_filtrado()
        semanais = df.groupby(['data_semana_inicio', 'faixa_completude']).agg({'unique_id': 'count'}).reset_index()
        semanais['data_semana_inicio'] = pd.to_datetime(semanais['data_semana_inicio'])
        plot = (
            p9.ggplot(semanais, p9.aes(x='data_semana_inicio', y='unique_id', color='faixa_completude')) +
            p9.geom_line() +
            p9.scale_color_manual(values=cor_completude_map) +
            p9.labs(
                x='Data de Interação',
                y='Número de Interações',
                color='Faixa de Completude'
            ) +
            p9.theme_minimal()
        )
        return plot


app = App(app_ui, server)