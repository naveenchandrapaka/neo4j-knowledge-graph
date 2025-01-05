from flask import Blueprint, render_template, request
from app.models import search_papers, get_paper_details, driver, advanced_search_papers, generate_graph, generate_interactive_graph
from urllib.parse import unquote
import base64


routes_app = Blueprint('routes_app', __name__)

@routes_app.route('/')
def home():
    return render_template('home.html')

@routes_app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        query = request.form.get('query', '')
        # print("query", query)
        results = search_papers(query)
        # print("Results passed to template:", results)
        return render_template('results.html', results=results, query=query)
    return render_template('search.html')

@routes_app.route('/advanced_search', methods=['GET', 'POST'])
def advanced_search():
    if request.method == 'POST':
        filters = {
            "topic_name": request.form.get("topic_name") or None,
            "author_name": request.form.get("author_name") or None,
            "start_year": int(request.form.get("start_year")) if request.form.get("start_year") else None,
            "end_year": int(request.form.get("end_year")) if request.form.get("end_year") else None
        }
        print(f"Filters received: {filters}")  # Debugging
        results = advanced_search_papers(filters)
        return render_template('advanced_results.html', results=results, filters=filters)
    return render_template('advanced_search.html')




@routes_app.route('/details/<paper_id>')
def details(paper_id):
    print(f"Encoded paper_id received: {paper_id}")


    decoded_paper_id = unquote(paper_id)  # Decode the URL-encoded paper_id
    print(f"Decoded paper_id: {decoded_paper_id}")  # Debugging step
    

    paper = get_paper_details(decoded_paper_id)  # Pass the decoded id
    if paper:
        print("1")
        return render_template('details.html', paper=paper)
    else:
        print("2")
        return render_template('details.html', error="Paper not found.")


@routes_app.route('/visualize')
def visualize():
    graph_image = generate_graph()
    return render_template('visualize.html', graph_image=graph_image)

@routes_app.route('/interactive-visualize')
def interactive_visualize():
    html_path = generate_interactive_graph()
    return render_template('interactive_visualize.html', graph_file='interactive_graph.html')






