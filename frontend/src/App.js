import React, { useState } from "react";
import Typography from "@mui/material/Typography";
import Button from "@mui/material/Button";
import TextField from "@mui/material/TextField";
import Box from "@mui/material/Box";
import axios from "axios";
import Grid from "@mui/material/Grid";
import Stocks from "./Stocks";
import Accordion from "@mui/material/Accordion";
import AccordionSummary from "@mui/material/AccordionSummary";
import AccordionDetails from "@mui/material/AccordionDetails";
import ArrowDropDownIcon from "@mui/icons-material/ArrowDropDown";
import CircularProgress from "@mui/material/CircularProgress";
import { styled } from "@mui/material/styles";
import Paper from "@mui/material/Paper";

const Item = styled(Paper)(({ theme }) => ({
  backgroundColor: "#fff",
  ...theme.typography.body2,
  padding: theme.spacing(1),
  textAlign: "center",
  color: (theme.vars ?? theme).palette.text.secondary,
  ...theme.applyStyles("dark", {
    backgroundColor: "#1A2027",
  }),
}));

const colorMap = {
  lightred: "#fca5a5",
  darkred: "#b91c1c",
  lightgreen: "#86efac",
  darkgreen: "#166534",
  gray: "#d1d5db",
};

const App = () => {
  const [filePath, setFilePath] = useState("");
  const [stockNames, setStockNames] = useState([]);
  const [stockSymbols, setStockSymbols] = useState({});
  const [stockData, setStockData] = useState({});
  const [loadingStocks, setLoadingStocks] = useState(false);
  const [loadingSymbol, setLoadingSymbol] = useState({});
  const [errorMsg, setErrorMsg] = useState("");
  const [searchText, setSearchText] = useState("");

  const fetchStockInfo = async (stockName) => {
    try {
      const formData = new FormData();
      formData.append("company_name", stockName);
      const res = await axios.post("http://localhost:8000/search", formData);

      if (res.data.results && res.data.results.length > 0) {
        const symbol = res.data.results[0].symbol || res.data.results[0];
        setStockSymbols((prev) => ({ ...prev, [stockName]: symbol }));

        const formData2 = new FormData();
        formData2.append("symbol", symbol);
        const res2 = await axios.post("http://localhost:8000/history", formData2);

        if (!res2.data.error) {
          setStockData((prev) => ({
            ...prev,
            [stockName]: {
              data: res2.data.data || [],
              result: res2.data.result || {},
            },
          }));
        }
      } else {
        setErrorMsg(`No ticker found for ${stockName}`);
      }
    } catch (err) {
      console.error(err);
      setErrorMsg(`Error fetching info for ${stockName}`);
    }
  };

  const handleLoadStocks = async () => {
    if (!filePath) return;
    try {
      setErrorMsg("");
      setLoadingStocks(true);

      const res = await axios.post("http://localhost:8000/get-stocks/", {
        file_path: filePath,
      });

      if (res.data.error) {
        setErrorMsg(res.data.error);
        setStockNames([]);
        return;
      }

      const stocks = res.data.stock_names || [];
      setStockNames(stocks);

      const newLoading = {};
      stocks.forEach((name) => (newLoading[name] = true));
      setLoadingSymbol(newLoading);

      await Promise.all(
        stocks.map(async (stock) => {
          await fetchStockInfo(stock);
          setLoadingSymbol((prev) => ({ ...prev, [stock]: false }));
        })
      );
    } catch (err) {
      console.error(err);
      setErrorMsg("Error loading stocks");
    } finally {
      setLoadingStocks(false);
    }
  };

  // Filtered stocks based on search text
  const filteredStocks = stockNames.filter((name) =>
    name.toLowerCase().includes(searchText.toLowerCase())
  );

  return (
    <div className="min-h-screen bg-gradient-to-r from-indigo-100 via-blue-50 to-green-100 flex flex-col items-center p-8">
      <Typography variant="h4" className="font-bold text-gray-800 mb-6">
        📂 Stock Holdings Viewer
      </Typography>

      {/* File path input + load button */}
      <Box className="flex gap-4 mb-6 w-full max-w-md">
        <TextField
          label="Enter File Path"
          variant="outlined"
          value={filePath}
          onChange={(e) => setFilePath(e.target.value)}
          className="bg-white rounded-md"
          fullWidth
        />
        <Button
          variant="contained"
          color="primary"
          onClick={handleLoadStocks}
          disabled={loadingStocks}
          startIcon={loadingStocks && <CircularProgress size={18} color="inherit" />}
        >
          {loadingStocks ? "Loading..." : "Load Stocks"}
        </Button>
      </Box>

      {/* Search bar */}
      {stockNames.length > 0 && (
        <Box className="mb-6 w-full max-w-md">
          <TextField
            label="Search Stocks"
            variant="outlined"
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            fullWidth
          />
        </Box>
      )}

      {errorMsg && <p className="text-red-600">{errorMsg}</p>}

      {/* Stock accordions */}
      <Box className="flex flex-col gap-3 mb-6 w-full max-w-3xl">
        {filteredStocks.map((stock) => (
          <Accordion key={stock}>
            <AccordionSummary
              expandIcon={<ArrowDropDownIcon />}
              aria-controls={`${stock}-content`}
              id={`${stock}-header`}
            >
              <Box className="flex items-center gap-3 flex-wrap">
                <Typography component="span" className="font-semibold">
                  {stock}
                </Typography>

                {stockData[stock]?.data
                  ?.filter((item) =>
                    [
                      "RSI",
                      "ADX",
                      "Price/MA7/MA13",
                      "Price/MA100/MA200",
                      "MACD/Signal",
                    ].includes(item.key)
                  )
                  .map((item) => {
                    const bgColor = colorMap[item.value[1]] || "#d1d5db";
                    const label = item.value[2] || "";
                    return (
                      <Box
                        key={item.key}
                        sx={{
                          px: 1.5,
                          py: 0.5,
                          borderRadius: 2,
                          fontSize: "0.75rem",
                          fontWeight: 500,
                          backgroundColor: bgColor,
                          color: ["lightred", "darkred"].includes(item.value[1])
                            ? "white"
                            : "black",
                        }}
                      >
                        {item.key}:{" "}
                        {Array.isArray(item.value[0])
                          ? item.value[0].join("/")
                          : item.value[0]}{" "}
                        {label && `(${label})`}
                      </Box>
                    );
                  })}
              </Box>
            </AccordionSummary>

            <AccordionDetails>
              {loadingSymbol[stock] ? (
                <Typography className="text-gray-500">Loading...</Typography>
              ) : stockSymbols[stock] ? (
                <div className="w-full bg-white shadow-lg rounded-xl p-6">
                  <Typography variant="h5" className="mb-4 text-gray-700">
                    📈 {stockSymbols[stock]} Stock Info
                  </Typography>
                  <Stocks symbol={stockSymbols[stock]} preloadedData={stockData[stock]} />
                </div>
              ) : (
                <Typography className="text-gray-500">No ticker found</Typography>
              )}
            </AccordionDetails>
          </Accordion>
        ))}
      </Box>
    </div>
  );
};

export default App;
