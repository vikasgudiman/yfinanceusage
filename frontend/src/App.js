import React, { useState } from "react";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import axios from "axios";
import Stocks from "./Stocks";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";

const App = () => {
  const [filePath, setFilePath] = useState("");
  const [stockNames, setStockNames] = useState([]);
  const [stockSymbols, setStockSymbols] = useState({}); // Map: stockName -> symbol
  const [loadingStocks, setLoadingStocks] = useState(false);
  const [loadingSymbol, setLoadingSymbol] = useState({}); // Map: stockName -> loading boolean
  const [errorMsg, setErrorMsg] = useState("");

  // Fetch stock names from file
  const handleFetchStocks = async () => {
    try {
      setErrorMsg("");
      setLoadingStocks(true);
      const res = await axios.post("http://localhost:8000/get-stocks/", {
        file_path: filePath,
      });

      if (res.data.error) {
        setErrorMsg(res.data.error);
        setStockNames([]);
      } else {
        setStockNames(res.data.stock_names || []);
      }
    } catch (err) {
      setErrorMsg("Error fetching stocks from file path");
      console.error(err);
    } finally {
      setLoadingStocks(false);
    }
  };

  // Fetch symbol for a specific stock
  const handleStockClick = async (stockName) => {
    try {
      // If already fetched, do nothing
      if (stockSymbols[stockName]) return;

      setErrorMsg("");
      setLoadingSymbol((prev) => ({ ...prev, [stockName]: true }));

      const formData = new FormData();
      formData.append("company_name", stockName);

      const res = await axios.post("http://localhost:8000/search", formData);

      if (res.data.results && res.data.results.length > 0) {
        const symbol = res.data.results[0].symbol || res.data.results[0];
        setStockSymbols((prev) => ({ ...prev, [stockName]: symbol }));
      } else {
        setErrorMsg(`No ticker found for ${stockName}`);
      }
    } catch (err) {
      console.error(err);
      setErrorMsg("Error searching ticker");
    } finally {
      setLoadingSymbol((prev) => ({ ...prev, [stockName]: false }));
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-indigo-100 via-blue-50 to-green-100 flex flex-col items-center p-8">
      <Typography variant="h4" className="font-bold text-gray-800 mb-6">
        📂 Stock Holdings Viewer
      </Typography>

      {/* File path input */}
      <Box className="flex gap-4 mb-6">
        <TextField
          label="Enter File Path"
          variant="outlined"
          value={filePath}
          onChange={(e) => setFilePath(e.target.value)}
          className="bg-white rounded-md"
          style={{ minWidth: "400px" }}
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleFetchStocks}
        >
          Load Stocks
        </Button>
      </Box>

      {loadingStocks && <p className="text-blue-600">Loading stocks...</p>}
      {errorMsg && <p className="text-red-600">{errorMsg}</p>}

      {/* Stock accordions */}
      <Box className="flex flex-col gap-3 mb-6 w-full max-w-3xl">
        {stockNames.map((stock) => (
          <Accordion key={stock}>
            <AccordionSummary
              expandIcon={<ArrowDropDownIcon />}
              aria-controls={`${stock}-content`}
              id={`${stock}-header`}
              onClick={() => handleStockClick(stock)}
            >
              <Typography component="span">{stock}</Typography>
            </AccordionSummary>

            <AccordionDetails>
              {loadingSymbol[stock] ? (
                <Typography className="text-gray-500">Loading...</Typography>
              ) : stockSymbols[stock] ? (
                <div className="w-full bg-white shadow-lg rounded-xl p-6">
                  <Typography variant="h5" className="mb-4 text-gray-700">
                    📈 {stockSymbols[stock]} Stock Info
                  </Typography>
                  <Stocks symbol={stockSymbols[stock]} />
                </div>
              ) : (
                <Typography className="text-gray-500">
                  Click to load ticker
                </Typography>
              )}
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    </div>
  );
};

export default App;
