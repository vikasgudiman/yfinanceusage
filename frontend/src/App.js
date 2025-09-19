import React, { useState } from "react";
import axios from "axios";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import Box from "@mui/material/Box";
import { ThemeProvider } from "@mui/material/styles";
import Grid from "@mui/material/Grid";
import Card from "@mui/material/Card";
import CardContent from "@mui/material/CardContent";
import Divider from "@mui/material/Divider";

const App = () => {
  const [companyName, setCompanyName] = useState("");
  const [symbols, setSymbols] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState("");
  const [tableData, setTableData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  // Add function to decide box color
  const getBoxColor = (key, value, rowData = {}) => {
    if (typeof value !== "number")
      return "linear-gradient(135deg, #f9fafb, #e5e7eb)";

    const colors = {
      strongBuy: "linear-gradient(135deg, #bbf7d0, #86efac)", // green
      buy: "linear-gradient(135deg, #dcfce7, #bbf7d0)", // light green
      sell: "linear-gradient(135deg, #fee2e2, #fecaca)", // red
      strongSell: "linear-gradient(135deg, #fca5a5, #ef4444)", // strong red
      neutral: "linear-gradient(135deg, #f3f4f6, #e5e7eb)", // gray
    };

    if (key === "MACD") {
      const macd = rowData.MACD;
      const signal = rowData.Signal;

      console.log("macd", macd);
      console.log("signal", signal);

      if (macd === signal) return colors.neutral;
      if (macd > signal && macd > 0 && signal > 0) return colors.strongBuy;
      if (macd < signal && macd < 0 && signal < 0) return colors.strongSell;
      if (macd < signal) return colors.sell;
      if (macd > signal) return colors.buy;

      return colors.neutral;
    }

    // default for other metrics (RSI, ADX, etc.)
    const ranges = {
      RSI: [30, 40, 60, 70],
      ADX: [20, 25, 40, 50],
      MA7: [-2, 0, 0.5, 2],
      MA13: [-2, 0, 0.5, 2],
    };

    const gradColors = [
      "linear-gradient(135deg, #fee2e2, #fecaca)",
      "linear-gradient(135deg, #ffedd5, #fed7aa)",
      "linear-gradient(135deg, #f3f4f6, #e5e7eb)",
      "linear-gradient(135deg, #dcfce7, #bbf7d0)",
      "linear-gradient(135deg, #a7f3d0, #6ee7b7)",
    ];

    const range = ranges[key];
    if (!range) return gradColors[2];

    if (value < range[0]) return gradColors[0];
    if (value < range[1]) return gradColors[1];
    if (value < range[2]) return gradColors[2];
    if (value < range[3]) return gradColors[3];
    return gradColors[4];
  };

  const handleSearch = async () => {
    if (!companyName) return;
    try {
      setLoading(true);
      setError("");
      const formData = new FormData();
      formData.append("company_name", companyName);
      const res = await axios.post("http://localhost:8000/search", formData);
      setSymbols(res.data.results || []);
    } catch (err) {
      console.error(err);
      setError("Error fetching symbols");
    } finally {
      setLoading(false);
    }
  };

  const handleFetchHistory = async (symbol) => {
    try {
      setLoading(true);
      setError("");
      setSelectedSymbol(symbol);

      const formData = new FormData();
      formData.append("symbol", symbol);
      const res = await axios.post("http://localhost:8000/history", formData);

      if (res.data.error) {
        setError(res.data.error);
        setTableData(null);
      } else {
        // Keep sections separate
        setTableData({
          data: res.data.data || {},
          result: res.data.result || {},
        });
      }
    } catch (err) {
      console.error(err);
      setError("Error fetching history");
    } finally {
      setLoading(false);
    }
  };

  const getValueColor = (key, value) => {
    if (key.toLowerCase().includes("indicator")) {
      return value === "Buy"
        ? "text-green-600 font-bold"
        : "text-red-600 font-bold";
    }
    return "text-gray-700";
  };

  return (
    <div className="min-h-screen bg-gradient-to-r from-indigo-100 via-blue-50 to-green-100 flex flex-col items-center p-8">
      {/* Title */}
      <Typography
        variant="h4"
        className="font-bold text-gray-800 mb-6 drop-shadow-md"
      >
        📈 Stock Info Finder
      </Typography>

      {/* Search Section */}
      <div className="flex gap-3 mb-8 w-full max-w-lg bg-white/70 p-4 rounded-xl shadow-md backdrop-blur-md">
        <TextField
          fullWidth
          required
          id="Share name"
          label="Share Name"
          onChange={(e) => setCompanyName(e.target.value)}
        />
        {/* Search Button */}
        <Button
          variant="contained"
          onClick={handleSearch}
          sx={{
            borderRadius: "12px",
            paddingX: "25px",
            paddingY: "10px",
            fontWeight: "bold",
            background:
              "linear-gradient(135deg,rgb(80, 185, 115) 0%,rgb(148, 50, 247) 100%)",
            color: "#fff",
            textTransform: "none",
            boxShadow: "0 6px 15px rgba(0,0,0,0.2)",
            transition: "all 0.3s ease",
            "&:hover": {
              background: "linear-gradient(135deg, #764ba2 0%, #667eea 100%)",
              transform: "translateY(-2px)",
              boxShadow: "0 10px 25px rgba(0,0,0,0.3)",
            },
          }}
        >
          {loading ? "Searching..." : "Search"}
        </Button>
      </div>

      {/* Error Message */}
      {error && <p className="text-red-600 mb-4 font-semibold">{error}</p>}

      {/* Symbols List */}

      {symbols.length > 0 && (
        <div className="mb-8 w-full max-w-lg bg-white/70 p-4 rounded-xl shadow-md">
          <h3 className="text-lg font-semibold mb-3 text-gray-800">
            Select a Symbol:
          </h3>
          <div className="flex flex-wrap gap-2">
            {symbols.map((s) => (
              <Chip
                key={s.symbol}
                label={` ${s.longname} (${s.symbol})`}
                clickable
                onClick={() => handleFetchHistory(s.symbol)}
                sx={{
                  borderRadius: "12px",
                  fontWeight: "bold",
                  background:
                    selectedSymbol === s.symbol
                      ? "linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%)"
                      : "linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%)",
                  color: selectedSymbol === s.symbol ? "#fff" : "#1e3a8a",
                  boxShadow: "0 4px 10px rgba(0,0,0,0.1)",
                  transition: "all 0.3s ease",
                  "&:hover": {
                    transform: "translateY(-2px)",
                    boxShadow: "0 8px 20px rgba(0,0,0,0.2)",
                  },
                }}
              />
            ))}
          </div>
        </div>
      )}

      {/* Stock Data Grid */}
      {tableData && (
        <div className="w-full max-w-6xl mt-6 space-y-8">
          {/* Technical Indicators */}
          <Card
            sx={{ borderRadius: 3, boxShadow: "0 8px 20px rgba(0,0,0,0.12)" }}
          >
            <CardContent>
              <Typography variant="h6" className="font-bold text-gray-800 mb-4">
                📊 Technical Indicators
              </Typography>
              <Grid container spacing={2}>
                {tableData.data.map((item) => (
                  <Grid item xs={6} md={3} key={item.key}>
                    <Box
                      sx={{
                        p: 3,
                        borderRadius: 3,
                        background: `linear-gradient(135deg, ${
                          item.value[1] === "lightgreen"
                            ? "#dcfce7,rgb(158, 248, 190)"
                            : item.value[1] === "darkgreen"
                            ? "#bbf7d0,rgb(3, 139, 53)"
                            : item.value[1] === "lightred"
                            ? "#fee2e2,rgb(236, 123, 123)"
                            : item.value[1] === "darkred"
                            ? "#fca5a5,rgb(126, 10, 10)"
                            : "#f3f4f6, #e5e7eb"
                        })`,
                        transition: "all 0.3s ease",
                        "&:hover": {
                          boxShadow: "0 8px 24px rgba(0,0,0,0.2)",
                          transform: "translateY(-3px)",
                        },
                      }}
                    >
                      <Typography
                        variant="subtitle2"
                        className="text-gray-700 uppercase tracking-wide"
                      >
                        {item.key}
                      </Typography>
                      <Typography variant="h6" className="font-bold mt-1">
                        {Array.isArray(item.value[0])
                          ? item.value[0].join(" / ")
                          : item.value[0]}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>

          {/* Fundamentals */}
          <Card
            sx={{ borderRadius: 3, boxShadow: "0 8px 20px rgba(0,0,0,0.12)" }}
          >
            <CardContent>
              <Typography variant="h6" className="font-bold text-gray-800 mb-4">
                🏦 Fundamentals
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(tableData.result).map(([key, value]) => (
                  <Grid item xs={6} md={3} key={key}>
                    <Box
                      sx={{
                        p: 3,
                        borderRadius: 3,
                        background: "linear-gradient(135deg, #f3f4f6, #e5e7eb)",
                        transition: "all 0.3s ease",
                        "&:hover": {
                          boxShadow: "0 8px 24px rgba(0,0,0,0.2)",
                          transform: "translateY(-3px)",
                        },
                      }}
                    >
                      <Typography
                        variant="subtitle2"
                        className="text-gray-500 uppercase tracking-wide"
                      >
                        {key}
                      </Typography>
                      <Typography
                        variant="h6"
                        className={`${getValueColor(key, value)} mt-1`}
                      >
                        {value}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default App;
