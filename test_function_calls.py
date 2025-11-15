import pytest
from unittest.mock import patch, MagicMock
from function_calls import get_clinical_info, show_literature, get_consequence_info, get_gene_name


@patch("function_calls.MyVariantInfo")
def test_get_clinical_info_with_significance(mock_myvariant):
    # Mock response with clinical significance
    mock_mv = MagicMock()
    mock_mv.getvariant.return_value = {
        "clinvar": {
            "rcv": [
                {"clinical_significance": "Benign"},
                {"clinical_significance": "Benign"},
                {"clinical_significance": "Benign"},
                {"clinical_significance": "Benign"},
            ]
        }
    }
    mock_myvariant.return_value = mock_mv

    result = get_clinical_info("chr9:g.107620835G>A")

    # Assertions
    assert result.count("Benign") == 4
    assert result.startswith(
        "Clinical significance results of the chr9:g.107620835G>A"
    )


@patch("function_calls.MyVariantInfo")
def test_get_clinical_info_no_rcv_field(mock_myvariant):
    # Mock response with no 'rcv' field
    mock_mv = MagicMock()
    mock_mv.getvariant.return_value = {"clinvar": {}}
    mock_myvariant.return_value = mock_mv

    result = get_clinical_info("chr9:g.107620835G>C")
    assert result.startswith(
        "No clinical significance found. Please check your variant ID"
    )


@patch("function_calls.MyVariantInfo")
def test_get_clinical_info_exception(mock_myvariant):
    # Simulate exception in myvariant
    mock_mv = MagicMock()
    mock_mv.getvariant.side_effect = Exception("API error")
    mock_myvariant.return_value = mock_mv
    result = get_clinical_info("chr9:g.107620835G>C")
    assert result.startswith(
        "Error in extracting clinical significance. Please check your variant ID:"
    )


@patch("function_calls.GoogleSearch")
def test_show_literature_returns_links(mock_search):
    """Test show_literature returns 5 links when API responds with organic results."""

    # Mock API response
    mock_instance = MagicMock()
    mock_instance.get_dict.return_value = {
        "organic_results": [
            {"link": "http://paper1.com"},
            {"link": "http://paper2.com"},
            {"link": "http://paper3.com"},
            {"link": "http://paper4.com"},
            {"link": "http://paper5.com"},
        ]
    }
    mock_search.return_value = mock_instance

    # Call function
    result = show_literature("BRCA1 variant")

    # Assert output contains all links
    expected = "\n".join(
        [
            "http://paper1.com",
            "http://paper2.com",
            "http://paper3.com",
            "http://paper4.com",
            "http://paper5.com",
        ]
    )
    assert result == expected


@patch("function_calls.GoogleSearch")
def test_show_literature_no_results(mock_search):
    """Test show_literature handles case when no links are returned."""

    mock_instance = MagicMock()
    mock_instance.get_dict.return_value = {"organic_results": []}
    mock_search.return_value = mock_instance

    result = show_literature("nonexistent gene")
    assert result == "No links found."

@patch("function_calls.GoogleSearch")
def test_show_literature_error(mock_search):
    """Test show_literature handles exceptions properly."""

    mock_search.side_effect = Exception("API failure")

    result = show_literature("TP53 variant")
    assert result.startswith("Error in show_literature:")


@patch("function_calls.MyVariantInfo")
def test_get_consequence_info_success(mock_myvariant):
    # Mock a response with consequence data
    mock_mv = MagicMock()
    mock_mv.getvariant.return_value = {
        "cadd": {"consequence": ["NON_SYNONYMOUS", "REGULATORY"]}
    }
    mock_myvariant.return_value = mock_mv

    result = get_consequence_info("chr1:g.11856378G>A")

    assert "Predicted chr1:g.11856378G>A genetic consequences are NON_SYNONYMOUS, REGULATORY" in result


@patch("function_calls.MyVariantInfo")
def test_get_consequence_info_no_data(mock_myvariant):
    # Mock a response without consequence field
    mock_mv = MagicMock()
    mock_mv.getvariant.return_value = {"cadd": {}}
    mock_myvariant.return_value = mock_mv

    result = get_consequence_info("chr1:g.11856378G>A")

    assert result == "No consequence data found. Please check your variant ID"


@patch("function_calls.MyVariantInfo")
def test_get_consequence_info_exception(mock_myvariant):
    # Simulate an exception in getvariant
    mock_mv = MagicMock()
    mock_mv.getvariant.side_effect = Exception("API error")
    mock_myvariant.return_value = mock_mv

    result = get_consequence_info("chr1:g.11856378G>A")

    assert result.startswith("Error in extracting consequence data. Please check your variant ID:")
    assert "API error" in result


@patch("function_calls.MyVariantInfo")
def test_get_gene_name_success(mock_myvariant):
    # Mock response with gene names
    mock_mv = MagicMock()
    mock_mv.getvariant.return_value = {
        "cadd": {
            "gene": [
                {"genename": "MTHFR"},
                {"genename": "BRCA1"},
                {"feature_id": "ENSR00000279227"}  # no genename here
            ]
        }
    }
    mock_myvariant.return_value = mock_mv

    result = get_gene_name("chr1:g.11856378G>A")

    assert result == "chr1:g.11856378G>A is located and associated with: MTHFR, BRCA1"


@patch("function_calls.MyVariantInfo")
def test_get_gene_name_no_data(mock_myvariant):
    # Mock response without any gene names
    mock_mv = MagicMock()
    mock_mv.getvariant.return_value = {"cadd": {"gene": [{"feature_id": "ENSR00000279227"}]}}
    mock_myvariant.return_value = mock_mv

    result = get_gene_name("chr1:g.11856378G>A")

    assert result == "No gene name found. Please check your variant ID"


@patch("function_calls.MyVariantInfo")
def test_get_gene_name_exception(mock_myvariant):
    # Simulate exception in getvariant
    mock_mv = MagicMock()
    mock_mv.getvariant.side_effect = Exception("API error")
    mock_myvariant.return_value = mock_mv

    result = get_gene_name("chr1:g.11856378G>A")

    assert result.startswith("Error in extracting gene name. Please check your variant ID:")
    assert "API error" in result