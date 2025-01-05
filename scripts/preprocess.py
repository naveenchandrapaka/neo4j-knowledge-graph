import json
import pandas as pd

def preprocess_openalex(input_file, output_dir):
    with open(input_file, "r") as f:
        data = json.load(f)

    # Initialize data containers
    papers, authors, institutions, topics, relationships = [], [], [], [], []

    for paper in data:
        # Add paper node
        papers.append({
            "id": paper["id"],
            "title": paper.get("title", ""),
            "doi": paper.get("doi", ""),
            "publication_year": paper.get("publication_year", ""),
        })

        # Add author nodes and relationships
        for authorship in paper.get("authorships", []):
            author = authorship.get("author", {})
            authors.append({
                "id": author.get("id", ""),
                "name": author.get("display_name", "")
            })
            relationships.append({
                "start_id": paper["id"],
                "end_id": author.get("id", ""),
                "type": "WRITTEN_BY"
            })

            # Add institution nodes and relationships
            for institution in authorship.get("institutions", []):
                institutions.append({
                    "id": institution.get("id", ""),
                    "name": institution.get("display_name", "")
                })
                relationships.append({
                    "start_id": author.get("id", ""),
                    "end_id": institution.get("id", ""),
                    "type": "AFFILIATED_WITH"
                })

        # Add topic nodes and relationships
        for topic in paper.get("concepts", []):
            topics.append({
                "id": topic.get("id", ""),
                "name": topic.get("display_name", "")
            })
            relationships.append({
                "start_id": paper["id"],
                "end_id": topic.get("id", ""),
                "type": "RELATED_TO"
            })

    # Convert to DataFrames and save as CSV
    pd.DataFrame(papers).drop_duplicates().to_csv(f"{output_dir}/papers.csv", index=False)
    pd.DataFrame(authors).drop_duplicates().to_csv(f"{output_dir}/authors.csv", index=False)
    pd.DataFrame(institutions).drop_duplicates().to_csv(f"{output_dir}/institutions.csv", index=False)
    pd.DataFrame(topics).drop_duplicates().to_csv(f"{output_dir}/topics.csv", index=False)
    pd.DataFrame(relationships).to_csv(f"{output_dir}/relationships.csv", index=False)

if __name__ == "__main__":
    preprocess_openalex("../data/raw_papers.json", "../data")
    print("Data preprocessed and saved to '../data' directory.")
