import json
import pandas as pd

def preprocess_openalex(input_file, output_dir):
    with open(input_file, "r") as f:
        data = json.load(f)

    # Initialize data containers
    papers, authors, institutions, topics, relationships = [], [], [], [], []

    for paper in data:
        # Extract simplified paper ID
        paper_id = paper["id"].split("/")[-1]

        # Add paper node
        papers.append({
            "id": paper_id,
            "title": paper.get("title", ""),
            "doi": paper.get("doi", ""),
            "publication_year": paper.get("publication_year", ""),
        })

        # Add author nodes and relationships
        for authorship in paper.get("authorships", []):
            author = authorship.get("author", {})
            author_id = author.get("id", "").split("/")[-1]  # Simplify author ID
            authors.append({
                "id": author_id,
                "name": author.get("display_name", "")
            })
            relationships.append({
                "start_id": paper_id,
                "end_id": author_id,
                "type": "WRITTEN_BY"
            })

            # Add institution nodes and relationships
            for institution in authorship.get("institutions", []):
                institution_id = institution.get("id", "").split("/")[-1]  # Simplify institution ID
                institutions.append({
                    "id": institution_id,
                    "name": institution.get("display_name", "")
                })
                relationships.append({
                    "start_id": author_id,
                    "end_id": institution_id,
                    "type": "AFFILIATED_WITH"
                })

        # Add topic nodes and relationships
        for topic in paper.get("concepts", []):
            topic_id = topic.get("id", "").split("/")[-1]  # Simplify topic ID
            topics.append({
                "id": topic_id,
                "name": topic.get("display_name", "")
            })
            relationships.append({
                "start_id": paper_id,
                "end_id": topic_id,
                "type": "RELATED_TO"
            })

    # Convert to DataFrames and save as CSV
    pd.DataFrame(papers).drop_duplicates().to_csv(f"{output_dir}/papers1.csv", index=False)
    pd.DataFrame(authors).drop_duplicates().to_csv(f"{output_dir}/authors1.csv", index=False)
    pd.DataFrame(institutions).drop_duplicates().to_csv(f"{output_dir}/institutions1.csv", index=False)
    pd.DataFrame(topics).drop_duplicates().to_csv(f"{output_dir}/topics1.csv", index=False)
    pd.DataFrame(relationships).to_csv(f"{output_dir}/relationships1.csv", index=False)

if __name__ == "__main__":
    preprocess_openalex("./data/raw_papers.json", "./data")
    print("Data preprocessed and saved to './data' directory.")
