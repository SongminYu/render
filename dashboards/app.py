from dash import Dash, html, dcc
import dash
from dash_bootstrap_components.themes import BOOTSTRAP

app = Dash(__name__, pages_folder='pages', use_pages=True, external_stylesheets=[BOOTSTRAP])

app.layout = html.Div([
    html.Br(),
    html.P('Building Stock Dashboard', className="text-dark text-center fw-bold fs-1"),
    html.Div(children=[
        dcc.Link(page['name'],
                 href=page["relative_path"],
                 className="btn btn-primary m-2 fs-5")  # How link to other pages should be displayed
        for page in dash.page_registry.values()]
    ),
    dash.page_container
], className="col-8 mx-auto")

if __name__ == '__main__':
    app.run(debug=True)
