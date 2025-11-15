import os
from serpapi import GoogleSearch
from dotenv import load_dotenv
from myvariant import MyVariantInfo

load_dotenv()
SERP_API_KEY = os.getenv("SERP_API_KEY")


# 1. Literature lookup via Google Scholar (SerpApi)
def show_literature(query: str) -> str:
    """
    Search Google Scholar for a variant/gene query and return first 5 paper links.
    """
    try:
        params = {
            "engine": "google_scholar",
            "q": query,
            "api_key": SERP_API_KEY,
            "num": 5,
            "hl": "en",
        }
        search = GoogleSearch(params)
        result = search.get_dict()
        links = [
            res.get("link") for res in result.get("organic_results", [])[:5]
        ]
        text = "\n".join(links) or "No links found."
        return text
    except Exception as e:
        return f"Error in show_literature: {e}"


# 2. Clinical significance via myvariant.info
def get_clinical_info(variant_id: str) -> str:
    """Extracts clinical significance terms from myvariant.info response.

    :param variant_id: variant identifier, e.g. 'chr9:g.107620835G>A'
    :type variant_id: str
    :return: clinical significance terms
    :rtype: str
    """
    try:
        mv = MyVariantInfo()
        variant_data = mv.getvariant(variant_id)
        significances = ""

        # Path where clinical significance is usually stored in myvariant.info
        clinvar_data = variant_data.get("clinvar", {})

        # 'rcv' field contains list of reports
        for record in clinvar_data.get("rcv", []):
            sig = record.get("clinical_significance")
            if sig:
                significances += sig + ", "

        return (
            f"Clinical significance results of the {variant_id}, reported and interpreted by studies: {significances[:-2]}"
            if significances
            else "No clinical significance found. Please check your variant ID"
        )
    except Exception as e:
        return f"Error in extracting clinical significance. Please check your variant ID: {e}"


# 3. Get variant genetic consequence via myvariant.info
def get_consequence_info(variant_id: str) -> str:
    """
    Extracts variant consequence terms from myvariant.info.

    :param variant_id: variant identifier, e.g. 'chr1:g.11856378G>A'
    :type variant_id: str
    :return: consequence terms
    :rtype: str
    """
    try:
        mv = MyVariantInfo()
        variant_data = mv.getvariant(variant_id)

        # Get consequence list from CADD data
        consequence = variant_data.get("cadd", {}).get("consequence", [])

        if consequence:
            return f"Predicted {variant_id} genetic consequences are {', '.join(consequence)}"
        else:
            return "No consequence data found. Please check your variant ID"

    except Exception as e:
        return f"Error in extracting consequence data. Please check your variant ID: {e}"


# 4. Get gene name via myvariant.info
def get_gene_name(variant_id: str) -> str:
    """
    Extracts gene names from myvariant.info response.

    :param variant_id: variant identifier, e.g. 'chr1:g.11856378G>A'
    :type variant_id: str
    :return: gene names
    :rtype: str
    """
    try:
        mv = MyVariantInfo()
        variant_data = mv.getvariant(variant_id)

        # Extract gene names from 'gene' list
        data = variant_data.get("cadd", {}).get("gene", [])
        gene_name = [item["genename"] for item in data if "genename" in item]
        if gene_name:
            return f"{variant_id} is located and associated with: {', '.join(gene_name)}"
        else:
            return "No gene name found. Please check your variant ID"

    except Exception as e:
        return (
            f"Error in extracting gene name. Please check your variant ID: {e}"
        )


tools = [
    {
        "type": "function",
        "function": {
            "name": "get_consequence_info",
            "description": "Get variant consequence information associated with a specific variant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "variant_id": {
                        "type": "string",
                        "description": "Variant identifier, e.g. 'chr1:g.11856378G>A'",
                    }
                },
                "required": ["variant_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_gene_name",
            "description": "Get gene name associated with a specific variant.",
            "parameters": {
                "type": "object",
                "properties": {
                    "variant_id": {
                        "type": "string",
                        "description": "Variant identifier, e.g. 'chr1:g.11856378G>A'",
                    }
                },
                "required": ["variant_id"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "show_literature",
            "description": "Search Google scholar for variant-related publications",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Searching for literature, scientific papers and research for variant-related publications",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_clinical_info",
            "description": "Gets clinical significance information from various sources about one specific variant in accordance to HGVS standards",
            "parameters": {
                "type": "object",
                "properties": {
                    "variant_id": {
                        "type": "string",
                        "description": "Variant HGVS identifier, e.g. 'chr9:g.107620835G>A'",
                    }
                },
                "required": ["variant_id"],
            },
        },
    },
]
