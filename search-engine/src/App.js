import React, { useState, useEffect, useCallback } from "react";
import axios from "axios";
import "./App.css"; // Import the CSS file

const API_URL = "http://127.0.0.1:5000";

const App = () => {
  const [buildBaseUrl, setBuildBaseUrl] = useState("");
  const [buildMaxPages, setBuildMaxPages] = useState(10);
  const [buildStatus, setBuildStatus] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchAlpha, setSearchAlpha] = useState(1);
  const [searchTopK, setSearchTopK] = useState(5);
  const [searchResults, setSearchResults] = useState([]);
  const [searchError, setSearchError] = useState(null);
  const [loading, setLoading] = useState(false);

  const buildSearchData = useCallback(async () => {
    if (!buildBaseUrl) {
      setBuildStatus("Please enter a base URL.");
      return;
    }

    const data = { base_url: buildBaseUrl, max_pages: buildMaxPages };
    setLoading(true);
    try {
      const response = await axios.post(`${API_URL}/build`, data, {
        headers: {
          "Content-Type": "application/json",
        },
      });

      setBuildStatus(response.data.status);
    } catch (error) {
      console.error("Error building data:", error);
      setBuildStatus(
        `Error building data: ${error.message || "Unknown error"}`
      );
    } finally {
      setLoading(false);
    }
  }, [buildBaseUrl, buildMaxPages]);

  const search = useCallback(
    async (includeSummary) => {
      if (!searchQuery) {
        setSearchError("Please enter a search query.");
        return;
      }
      setSearchError(null);
      setSearchResults([]);
      setLoading(true);

      const endpoint = includeSummary ? "search_with_summary" : "search";
      const url = `${API_URL}/${endpoint}`;

      try {
        const response = await axios.post(url, {
          query: searchQuery,
          alpha: searchAlpha,
          top_k: searchTopK,
        });

        if (response.data && Array.isArray(response.data)) {
          setSearchResults(response.data);
        } else {
          setSearchError("Invalid response format from the server.");
          setSearchResults([]);
        }
      } catch (error) {
        console.error(`Error searching (${endpoint}):`, error);
        setSearchError(
          `Error fetching search results: ${error.message || "Unknown error"}`
        );
        setSearchResults([]);
      } finally {
        setLoading(false);
      }
    },
    [searchQuery, searchAlpha, searchTopK]
  );

  const displayResults = () => {
    if (searchError) {
      return (
        <div className="alert alert-error" role="alert">
          <strong>Error: </strong>
          <span>{searchError}</span>
        </div>
      );
    }

    if (loading) {
      return <p>Loading...</p>;
    }

    if (!searchResults || searchResults.length === 0) {
      if (searchQuery) {
        return <p>No results found.</p>;
      }
      return null;
    }

    return (
      <>
        {searchResults.map((result) => (
          <div key={result.doc_id} className="search-result-item">
            <div className="result-title">
              {result.snippet.substring(0, 80)}
              {result.snippet.length > 80 && "..."}
            </div>
            <a
              href={result.url}
              className="result-url"
              target="_blank"
              rel="noopener noreferrer"
            >
              {result.url}
            </a>
            <p className="result-score">Score: {result.score.toFixed(3)}</p>
            <p className="result-snippet">Snippet: {result.snippet}</p>
            {result.summary && (
              <p className="result-summary">Summary: {result.summary}</p>
            )}
          </div>
        ))}
      </>
    );
  };

  useEffect(() => {
    const handleEnter = (event) => {
      if (event.key === "Enter") {
        search(false);
      }
    };
    window.addEventListener("keydown", handleEnter);
    return () => {
      window.removeEventListener("keydown", handleEnter);
    };
  }, [search]);

  return (
    <div className="app-container">
      <h1 className="app-title">Intelligent Search Engine</h1>

      <div className="build-section">
        <h2 className="section-title">Build Search Data</h2>
        <div className="input-group">
          <label htmlFor="build-base-url" className="input-label">
            Base URL:
          </label>
          <input
            type="text"
            id="build-base-url"
            placeholder="e.g., https://en.wikipedia.org/wiki/Web_crawler"
            value={buildBaseUrl}
            onChange={(e) => setBuildBaseUrl(e.target.value)}
            className="input-field"
          />
        </div>
        <div className="input-group">
          <label htmlFor="build-max-pages" className="input-label">
            Max Pages (optional):
          </label>
          <input
            type="number"
            id="build-max-pages"
            value={buildMaxPages}
            onChange={(e) => setBuildMaxPages(parseInt(e.target.value, 10))}
            className="input-field"
          />
        </div>
        <button onClick={buildSearchData} className="build-button">
          Build Index
        </button>
        {buildStatus && <p className="status-message">{buildStatus}</p>}
      </div>

      <div className="search-section">
        <h2 className="section-title">Search</h2>
        <div className="input-group">
          <label htmlFor="query" className="input-label">
            Query:
          </label>
          <input
            type="text"
            id="query"
            placeholder="Enter your search query"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="input-field"
          />
        </div>
        <div className="input-group">
          <label htmlFor="alpha" className="input-label">
            Alpha (Keyword Weight, 0-1):
          </label>
          <input
            type="number"
            id="alpha"
            value={searchAlpha}
            step={0.1}
            min={0}
            max={1}
            onChange={(e) => setSearchAlpha(parseFloat(e.target.value))}
            className="input-field"
          />
        </div>
        <div className="input-group">
          <label htmlFor="top_k" className="input-label">
            Top K Results:
          </label>
          <input
            type="number"
            id="top_k"
            value={searchTopK}
            min={1}
            onChange={(e) => setSearchTopK(parseInt(e.target.value, 10))}
            className="input-field"
          />
        </div>
        <div className="search-buttons">
          <button onClick={() => search(false)} className="search-button">
            Search
          </button>
          <button onClick={() => search(true)} className="search-button">
            Search with Summary
          </button>
        </div>
      </div>

      <div className="results-section">
        <h2 className="section-title">Search Results</h2>
        {displayResults()}
      </div>
    </div>
  );
};

export default App;
